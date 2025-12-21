import json, boto3

client = boto3.client("bedrock-runtime")

def handler(event, context):
    body = json.loads(event["body"])            # parse the body of the event and convert it from a string to a dictionary
    image_b64 = body["image"]             #I need body as a dict to access the image key      
    media_type = "image/png"
    if isinstance(image_b64, str) and image_b64.startswith("data:"):    #the image could be delivered as "image": "data:image/png;base64,iVBORw0KGgoAAA...  
        try:
            header, image_b64 = image_b64.split(",", 1)  #takes everything before, and it assigns it to header, and takes everthing after and it assigns it to image_b64
        except ValueError:
            return{
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid image URL (missing comma)"}),
            }
    system_prompt = """
You are a professional makeup artist and beauty consultant. Analyze the person’s face in the uploaded photo (skin tone, undertone, face shape, eye color, brow shape, lip shape, visible features) and give clear, practical makeup recommendations.
For this person, provide:
1) One natural everyday makeup look.
2) One soft-glam or evening look.
For each look, suggest:
- Foundation finish and coverage level, and 1–2 shade ranges that would match this skin tone.
- Blush, bronzer/contour, and highlighter colors and placement that flatter this face shape.
- Eyeshadow color families and finishes that enhance their eye color, plus basic liner and mascara tips.
- Lip colors and finishes (matte, gloss, satin) that complement their features.
Explain application steps in short, numbered bullets. Keep the tone friendly, supportive, and easy to follow for beginners. Do not mention brand names unless explicitly asked; focus on colors, textures, and general product types.
"""
    payload_for_Bedrock  = {                          #when there are multiple dictionaries as elements I need to include them in a list.
        "anthropic_version": "bedrock-2023-05-31",    
        "max_tokens": 512,                            #in general: list when I have an ordered list (so order is important, for example in messages I need to include a conversation) of objects also not related with each other, DICT when I'm describing a single object with several attributes
        "messages": [                                 #root is a dic becasue has several properties defining the same "object"
            {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_b64
                }
                },
                {
                    "type": "text",
                    "text": system_prompt
                    }
            ],
            }
            ],    
            }

    request = json.dumps(payload_for_Bedrock)

    response = client.invoke_model(
        modelId="anthropic.claude-sonnet-4-5-20250929-v1:0",
        contentType="application/json",
        accept="application/json",                      #what format we expect in return
        body=request,
    )

    bytes_outcome = response["body"].read()             # Bedrock will send back as answer a python dict thanks to boto3 acting as a wrapper that converts automatically the raw http request into python
    # with .read we convert the stream (where the body is) into bytes. A stream is  a file-like object that delivers data incrementally instead of giving me the wjole content at once. In this way the SDK can handle large responses without having to load everything into memory.
    outcome = json.loads(bytes_outcome)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(outcome),
    }
