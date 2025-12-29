# hash is like a digital footprint of a file. using source_code_hash I'm able to to check if the code of the function has changed or not, and in case update the lambda
# even one different character changes the hash of the file. And in this case is important, because zip file name will be the same.
# what does "update lambda" means? --> let's say I have a lmbda already deployed, I change the function, new zip file ecc, if hash is different terraform will replace the code with the new one.

resource "aws_lambda_function" "processor" {
    function_name = "ai-coach-processor"
    role = "aws_iam_role.lambda_role.arn"
    runtime = "python3.12"
    handler = "function_processor.handler"

    filename = "../lambda_functions/function_processor.zip" # this says to terraform --> when you create/update the lambda use this file as code/function
    source_code_hash = filebase64sha256("../lambda_functions/function_processor.zip") # file() reads file byte per byte, sha256 produces the hash in bytes, base64 transforms bytes in string.

environment {
        variables = {
            UPLOADS_BUCKET = aws_s3_bucket.uploads.id # --> I need to define this as a variable because python cannot read terraform, so at runtime level I need a way to refer to the bucket
            TABLE_NAME = aws_dynamodb_table.recommendations.name
        }
    }
    timeout = 30
    memory_size = 1024        #being a GetObject, involving processing and storing data, lambda has to be more powerfull, have more memory
}