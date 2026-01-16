# Identity provider (authentication) for the app
# There are two concetps Cognito offers:
# 1. User Pool --> users authentication and login (authentication)
# 2. Identity Pool --> provides credentials to aws (authorization)

# I choose 1 because I don't need AIM authorisation management or assign
# IAM temporary credentials, I just need to manager login/signup.

# JWT = JSON Web Token --> is a string which includes data --> it is a string in the HTTP request
# in the JWT there are: 
# A. Header
# B. Payload (CLAIMS) --> sub, email ecc
# C. Cognito signature

# In Cognito there are:
# 1. User Pool --> "users database"
# 2. App Client --> application authorised to use that pool

# when a user authenticates successfully cognito generates a token (JWT) which is basically a string aws signed and it goes in the browser and is saved by the frontend.
# every time frintend calls backend the token goes into the header of the HTTP request, and the backend let the user pass without password

# Client = application, is not a person, is registered in Cognito, and asks for the token for the user
# User = person registered in the user pool, a real person


# -------------------------------------------------
# USER POOL

resource "aws_cognito_user_pool" "user_pool" {
  name = "ai-coach-user-pool"

  username_attributes      = ["email"] # email is the user identifier
  auto_verified_attributes = ["email"] # email will be auto-verified

  password_policy {
    minimum_length    = 8
    require_lowercase = false
    require_uppercase = false
    require_numbers   = false
    require_symbols   = false
  }
}

# -------------------------------------------------
# APP CLIENT

resource "aws_cognito_user_pool_client" "frontend" {
  name         = "ai-coach-frontend-client"
  user_pool_id = aws_cognito_user_pool.user_pool.id

  generate_secret = false
  # No client secret because this is a browser-based app

  read_attributes = [
    "email"
  ]

  write_attributes = [
    "email"
  ]

  # OAuth configuration
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"] # Authorization Code Flow

  allowed_oauth_scopes = [
    "email",
    "openid",
    "profile"
  ]

  supported_identity_providers = ["COGNITO"]

  callback_urls = [
    "http://localhost:3000",
    "http://localhost:3000/callback",
    "https://main.d21xmugc315cvv.amplifyapp.com",
    "https://main.d21xmugc315cvv.amplifyapp.com/callback"
  ]

  logout_urls = [
    "http://localhost:3000",
    "https://main.d21xmugc315cvv.amplifyapp.com",
    "https://main.d21xmugc315cvv.amplifyapp.com/callback"
  ]
}

# -------------------------------------------------
# DOMAIN

resource "aws_cognito_user_pool_domain" "user_pool_domain" {
  domain       = "ai-fitness-coach-tobia"
  user_pool_id = aws_cognito_user_pool.user_pool.id

  managed_login_version = 2
}
