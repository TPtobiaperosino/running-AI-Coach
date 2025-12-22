# here I'll build the infra

# Roles HAVE TRUST RELATIONSHIPS THAT SET WHO CAN USE THEM
# Also USERS HAVE TO HAVE PERMISSIONS TO ASSUME ROLES

# first thing I need to do is to create an IAM role that the Lambda can use.
# terraform resources always follow this structure: "provider_type" "local_name"
# the local name is just in terraform, so is up to me, is like a variable
# Lambda need this role to receive then temporary permissions
# the name is instead what I see in the console when watching the IAM role, that is the the AWS real resource
# in aws avery entity that execute actions has to have a role (an identity)

resource "aws_iam_role" "first_lambda" {
    name = "ai-coach-lambda-role"       # name that is in the console


# assume_role_policy is the trust policy of the role and says who can assume that role. It is an attribute of the role.
# this role will be used only by lambda
# sto dicendo che a lambda e' permesso di assumere il ruolo

assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
    }]
})
}