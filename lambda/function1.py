import json, base64 

def handler(event, context):
    body = json.loads(event["body"])            #the HTTP request received is a string and I need to convert it to a dict in order to work efficiently witht the different fields
    image_b64 = body["image"]                   # extract the image written as a string and I assign it to the variable image_b64
    image_bytes = base64.b64decode(image_b64)   # convert the image from base64(string) to bytes
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
        "max_tokens": 512,                            #in general: list when Ihave an ordered list of objects also not related with each other, DICT when I'm describing a single object with several attributes
        "messages": [                                 #root is a dic becasue has several properties defining the same "object"
            {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "bytes",
                        "media_type": "image/png",
                        "data": image_bytes
                }
                },
                {
                    "type": "text",
                    "text": system_prompt
                    }
            ]
                
            }
            ]
                 
            }
    


