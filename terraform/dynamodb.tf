resource "aws_dynamodb_table" "recommendations" {
  name         = "ai-running-coach-recommendations"
  billing_mode = "PAY_PER_REQUEST" # If i don't put on-demand the standard is provisioned

  PK = "userId" # primary key

  SK = "createdAt" # sort key

  attribute {
    name = "userId"
    type = "S" # I need to define the attribute type to then use it as key
  }

  attribute {
    name = "createdAt"
    type = "S" # I need to define the attribute type to then use it as key
  }

  ttl {
    attribute_name = "expiresAt"
    enabled        = true
  }
}

# all the other attributes will be defined through lambda (PutItem)

# DynamoDB:
# - table: contains the items (in rows)
# - item: record json like
# In every item there are fields --> I'll put a UUID to match each recommendation with its corresponding photo
# - Primary Key: how dynamo organises and find the items and can have:
# (i) Partition Key (PK): decide where the item finishes (sharding)
# (ii) Sort Key (SK): order items in the PK
# - Query: use PK and SK, very fast
# - Scan: read everything, slow and expensive
# - TTL (Time To Live) --> auto-delete machanism of items after a certain date based on timestamp epoch:
# timestamp epoch is like the sum of seconds since the item has bee recorded, when it exceeds expiresAt (max sum of seconds) the item is deleted
# GSI (Global Secondary Index) --> a second way to read the table using different keys from the primary ones
# Pay Per Request --> measures how much do I pay based on units consumed including: (i) read request units (ii) write request units (iii) storage occupied

# In my use case:
# I'll use PK (primary key) to record the userid, and SK (sort key) to record when it has been created
# 
# s3Key --> to link to the photo in s3
# photo summary (string)
# recommendation (string)
# TTL --> now_epoch > expiresAt 
