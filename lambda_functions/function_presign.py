# This function needs to crate the s3Key
# OS is a standard library of Python, and allows to read environment variables --> os.environ is a dict which includes all the env variables available for lambda when it runs
# Lambda always returns a python dict

# What does this function do?
# - take HTTP request from API Gateway, and the userId
# - ask to s3 a presigned PUT URL
# - create a meal ID and create s3Key as identifier --> s3key = f"uploads/{user_id}/{meal_id}.jpg
# - send the URL back to the frontend

import json
import os
import uuid
import boto3  
from datetime import datetime, timezone
from botocore.config import Config

# first of all I need to create a client to make possible to connect python with the aws service s3. Python cannot communicate with s3 by itself
# s3 is a python object which knows where is s3, how to authenticate, which APIs exist 
# boto3 is the SDK of AWS for Python, without it I cannot call aws services, python alone is not "cloud aware"
# client = a way to speak with an external service
# client s3 = python object.
# boto3 automatically uses the lambda role created with all the permissions (and therefore uses the temporary credentials provided by STS)
# boto3 always uses Default Credential Provuder Chain --> automatically look for credentials in the environment based on the resource is linking to
# boto3 knbows the aws APIs (endpoints HTTP), is a wrapper on the APIs
# I could also calls the APIs manually, but would be very time consuming and less scalable, more likely to make mistakes

AWS_REGION = os.environ.get("AWS_REGION", "eu-west-2")

# what is an endpoint? --> an access point that allows to send a request and gain/do something.
# endpoint = HTTP method + (HET, PUT, POST...)URL path (with the action, presign for example) --> POST https://api.myapp.com/presign
# http methods indicate the type of action I intend to do:
# 1) PUT: write
# 2) GET: read
# 3) POST: create something new
# 4) DELETE ...
# IMPORTANT CONCEPT: Idempotency --> an operation is idempotent if calling multiple times produces the same result. POST is tipycally not idempotent becasue creates something new.

# HTTP (HyperText Transfer Protocol) REQUEST = a message sent by a client (browser, app, frontent) to a server asking it to do something
# HTTP REQUEST = method + URL + headers (metadata about the request) + body (actual data sent)
# HTTP RESPONSE = answer from the server = status code + Headers + body 
# HTTPS = HTTP + encryption --> API Gateway only expose HTTPS enpoints, †ha†'s why is good to use the gateway

# API Gateway = front door of my backend that exposes HTTPS endpoints, receives HTTPS requests from clients and forward them to the right backend service (routing)

# Force region-specific endpoint to avoid 301 redirects (breaks browser CORS preflight).
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
    config=Config(signature_version="s3v4")
) # creating the bridge between python and S3 through the SDK (boto3) --> the client s3
dynamodb = boto3.resource("dynamodb")

BUCKET_NAME = os.environ["UPLOADS_BUCKET"] # here I could use the real name of the bucket but is hardcoded, is safer to use variables
TABLE_NAME = os.environ["TABLE_NAME"]   
recommendations_table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    print(f"DEBUG: BUCKET_NAME={BUCKET_NAME}")
    user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    print(f"DEBUG: user_id={user_id}")
# this is the result of the authentication made by cognito and sent via api gateway. It is a data tree:
# API gateway takes jwt from Cognito and verifies it and checks if it is valid, extracting the claims
# requestContext includes all the other levels, authorizer same, until sub.
# requestContext = info on API, identity etc
# authorizer = cognito
# jwt = token encoded
# claims = fields inside jwt
# sub = userId

#    claims = event["requestContext"]["authorizer"]["jwt"]["claims"]

#    targets = {
 #       "calories": int(claims["custom:targetCalories"]), #custom is the other type of attributes in cognito that I define. with int I convert the string in number
 #       "protein": int(claims["custom:targetProtein"]),
 #       "carbs": int(claims["custom:targetCarbs"]),
 #       "fat": int(claims["custom:targetFat"]),
 #   }

    upload_id = str(uuid.uuid4()) #uuid is a library/module used to create Universally Unique Identifier, uuid4 is the function to create RANDOM uuid
    s3_key = f"uploads/{user_id}/{upload_id}.jpg"
    recommendations_table.put_item(
        Item={
            "PK": f"USER_{user_id}",
            "SK": f"UPLOAD_{upload_id}",
     #       "targets": targets,
            "s3Key": s3_key,
            "createdAt": datetime.now(timezone.utc).isoformat(), #isoformat convert the object datetime in string date format
            "status": "UPLOADING"

        }
    )

    

    upload_url = s3.generate_presigned_url(
        ClientMethod="put_object",      # here I'm just saying what the user can do (upload = write = put)
        Params={                        # provides parameters to the API call, s3 works with bucket and key, and during runtime key is provided.
            "Bucket": BUCKET_NAME,      # params defines the exact S3 API operation that this presigned URL authorizes (PUT object only)
            "Key": s3_key,                  
        },
        ExpiresIn=300 
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({            # frontend works with JSON, API Gateway expects a string, with json.dumps i get as body a JSON string
            "uploadUrl": upload_url,    # these data arrive to the frontend        
            "s3Key": s3_key,
            "uploadId": upload_id
        })
    }
