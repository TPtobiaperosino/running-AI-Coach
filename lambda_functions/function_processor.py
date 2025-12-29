# here this function has to be triggered when the photo is uploaded
# has to extract the image from S3, convert from stream of bytes to base64, invoke BedRock, get the recommendation and store it in DynamoDB
# The structure of the json I receive with an S3 event
#{
#  "Records": [
#    {
#      "eventSource": "aws:s3",
#      "eventName": "ObjectCreated:Put",
#      "awsRegion": "eu-west-2",
#      "s3": {
#        "bucket": {
#          "name": "my-upload-bucket"
#        },
#        "object": {
#          "key": "uploads/user123/file.jpg",
#          "size": 123456
#        }
#      }
#    }
#  ]
#}

import boto3
import base64
import os
import json
from datetime import datetime, timezone       # I need it to identify the exact moment when the event happened --> createdAt
                                              # from the datetime module take the class datetime. the class datetime represents a specific point in the time

# SDK section
s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime")           # I use client when I simply need to call an API
dynamodb = boto3.resource("dynamodb")               # I use resource when I need to call API but also create objects representing the resurce and operate on it

BUCKET_NAME = os.environ["UPLOADS_BUCKET"]
TABLE_NAME = os.environ["TABLE_NAME"]                               # This is just a string, is not enough in this case because I need to create an object representation of the dynamodb table and then operate on it.

recommendations_table = dynamodb.Table(TABLE_NAME)                  # Here I use the TABLE_NAME to specify the Table im referring to and then to create an object representation of the table created in terraform

def handler(event, context):        # In event I'll find a JSON with what happened in S3, because s3 event invoke this specific function
   upload = event["Records"][0]      # it's not compulsory, but better so I already defined the event in a variable. record because I need to access the list, but the list can include multiple events, so I want to make sure to extract only the first one that is the upload
   bucket = upload["s3"]["bucket"]["name"]  # in s3 every object is always identified by key + bucket
   s3_key = upload["s3"]["object"]["key"]
   
   _, user_id, upload_id_jpg = s3_key.split("/") #_ means ignore
   upload_id = upload_id_jpg.replace(".jpg", "") # remove jpg
   
   s3_request = s3.get_object(Bucket = bucket, Key = s3_key)
   image_bytes = s3_request["Body"].read() # get_object just give me back the http request, so to access the photo i need to access the body
   image_base64 = base64.b64encode(image_bytes).decode("utf-8") # untile decode they are still bytes but cleaner, with utf i convert those bytes into a python string


   uploaded_item = recommendations_table.get_item(
      Key = {
      "PK": f"USER_{user_id}",
      "SK": f"UPLOAD_{upload_id}"
      }
   )

   if "Item" not in uploaded_item:
      raise Exception("Uploaded context not found in the database") # Lambda fails
   
   targets = uploaded_item["Item"]["targets"]

# TRACKING UPLOAD

   recommendations_table.update_item(
      Key={       
      "PK": f"USER_{user_id}",
      "SK": f"UPLOAD_{upload_id}"
      },

# status is a reserved word in dynamodb, i cannot use it as variable, therefore I'll use an alias
# "#" before the first letter indicates it is an alias for names/variables, ":" for values
# I need to write this below becasue I want to update a field, not upload an actual item
       UpdateExpression = "SET #s = :s", # it's just a remote code in the dynamodb language to say that I want to modify that field
       ExpressionAttributeNames = {"#s": "status"},
       ExpressionAttributeValues = {":s": "PROCESSING"}
   )

   PROMPT_TEMPLATE = """
    You are a nutrition analysis and coaching assistant.

    You will be given:
    - An image of a single meal
    - The user's DAILY nutrition targets (calories and macros)

    Your job is to:
    1. Analyze the meal shown in the image
    2. Estimate its nutritional content
    3. Evaluate the meal quality
    4. Provide a concrete recommendation for the NEXT meal to help the user reach their daily targets

    IMPORTANT RULES
    - Base your analysis ONLY on what is visible in the image.
    - If something is unclear, make a reasonable assumption and mention uncertainty.
    - Be realistic and practical. No extreme or unrealistic advice.
    - Do NOT include markdown, explanations, or extra text.
    - Output MUST be valid JSON and MUST follow the schema exactly.

    -------------------------
    DAILY TARGETS
    -------------------------
    {{daily_targets_json}}

    -------------------------
    OUTPUT SCHEMA (STRICT)
    -------------------------
    {
    "meal_estimate": {
        "calories": number,
        "protein_g": number,
        "carbs_g": number,
        "fat_g": number
    },
    "meal_score": number,
    "meal_evaluation": string,
    "next_meal_recommendation": {
        "goal": string,
        "suggested_foods": [string],
        "macro_focus": string
    },
    "confidence_note": string
    }

    -------------------------
    SCORING GUIDELINES
    -------------------------
    - 90-100: excellent meal quality and balance
    - 70-89: good but improvable
    - 50-69: acceptable but suboptimal
    - <50: poor nutritional quality

    -------------------------
    NEXT MEAL LOGIC
    -------------------------
    - Use the remaining daily targets to guide the recommendation
    - Suggest realistic foods someone could eat next
    - Focus on what is most missing (protein, fiber, calories, micronutrients)
    - Keep the recommendation concise and actionable
    """

   prompt_text = PROMPT_TEMPLATE.replace(
        "{{daily_targets_json}}",
        json.dumps(targets))

   api_response = bedrock.invoke_model(
     modelId="amazon.nova-2-lite-v1:0",
     contentType="application/json",
     accept="application/json",
     body=json.dumps({
       "messages": [
         {
         "role":"user",
         "content": [
           {
             "type":"image",
             "source": 
               {"type":"base64",
               "media_type":"image/jpeg",
               "data": image_base64}
           },
           {
             "type":"text",
             "text": prompt_text
             }
         ]
         } 
         ]
       
           }
     )
   )

   # bedrock sends me the answer in json but since the api request gives me back an answer via HTTP the body, to avoid loading everything in memory at once, arrives in stream of bytes
   # with .read() reads the bytes from the stream.
   # then json.loads transforms the bytes that include json in a python object (dict/list) 

   result = json.loads(api_response["body"].read())

# TRACKING RECOMMENDATION

   recommendations_table.put_item(
        Item={
            # Chiavi primarie (definite da te in Terraform)
            "PK": f"USER_{user_id}",
            "SK": f"RECOMMENDATION_{upload_id}",

            # Dati di dominio (tutti personalizzabili)
            "s3Key": s3_key,
            "targets": targets,
            "analysis": result,

            # Metadata
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "status": "PROCESSED"
        }
    )

# TRACKING UPLOAD

   recommendations_table.update_item(
      Key={       
      "PK": f"USER_{user_id}",
      "SK": f"UPLOAD_{upload_id}"
      },

# status is a reserved word in dynamodb, i cannot use it as variable, therefore I'll use an alias
# "#" before the first letter indicates it is an alias for names/variables, ":" for values
# I need to write this below becasue I want to update a field, not upload an actual item

       UpdateExpression = "SET #s = :s", # it's just a remote code in the dynamodb language to say that I want to modify that field
       ExpressionAttributeNames = {"#s": "status"},
       ExpressionAttributeValues = {":s": "PROCESSED"}
   )







