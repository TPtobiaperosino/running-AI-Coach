# this is a resource based policy attached to the policy which authorises s3 to invoke the lambda
# who is invoked decides who can invoke it. that's why the policy is attached to lambda
# this policy should be external to the module s3 becasue it has to create a resource, not define how it interacts with the environment
# AWS has 2 types of policies:
# 1/ Identity based policies --> attached to users, roles and groups
# 2/ Resource based policies --> attached to Lambda functions, S3 buckets, SQS queues etc

# Other ways to do this were (i) EventBridge (ii) just API gateway (iii) SQS
# why s3 event? 
# 1/ cheap, scalable (if there are 100 uploads the system will scale automatically) 
# 2/ decoupling frontend (upload file e lambda call are separated), ai processing e.g. can take time and creates delays in the frontend
# 2/ also frotend could call lambda before the file is completely uploaded giving error
# 3/ reliability --> even if the user closes everything the photo is processed
# why not:
# EventBridge: usually used with more consumers (event triggers more lambda), here I have 1 consumet = more complexity, more terraform and latency
# API Gateway: race condition (processing before upload), add latency becasue processing is slow and can slow down frontend, also I'm shifting backend logic in the frontend which is not safe, it's coupling.
# API Gateway: the goal is Loose Coupling --> design components so they depend on each other as little as possible
# SQS: I need it when processing accumulates, monitor speed, s3 + lambda is already highy scalable. SQS could help if I exceed the concurrency limit, I need to process a speicifc number of images per minute for example (need specific speed).

resource "aws_lambda_permission" "allow_s3_invoke_processor" {
    statement_id = "AllowS3InvokeProcessor"
    action = "lambda:InvokeFunction"
    function_name = ***
    principal = "s3.amazonaws.com"
    source_arn = aws_s3_bucket.uploads.arn
}

resource "aws_s3_bucket_notification" "image_uploaded" {
    bucket = aws_s3_bucket.uploads.id

    lambda_function {
        lambda_function_arn = ***
        events = ["s3:ObjectCreated:*"]
        filter_prefix = "uploads/"
    }
    depeneds_on = [aws_lambda_permission.allow_s3_invoke_processor]
}
