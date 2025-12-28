resource "aws_s3_bucket" "uploads" {
    bucket = "s3-uploads-ai-running-coach-tobia"
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle_uploads" {
    bucket = aws_s3_bucket.uploads.id # this is the id of the bucket as resource, arn is for policies

    rule {              # this is a block!
        id = "delete-expired-uploads" # this is the id of the rule
        status = "Enabled"
        filter {prefix = "uploads/"}
        expiration {days = 14}
    }
}

resource "aws_s3_bucket_public_access_block" "uploads" {
    bucket = aws_s3_bucket.uploads.id

    block_public_acls       = true
    block_public_policy     = true    # prevent any public policies that could make the bucket public
    ignore_public_acls      = true    # ignore any existing acls
    restrict_public_buckets = true    # further protection
}



# ACL = Access Control List --> who can access the bucket or an object + which permissions there are

# Per S3 ho usato un module because I'm not just creating a bucket, I have the lifecylce rule, public access etc, so in this way I don't eed to rewrite everything each time, I can just refer to this module


