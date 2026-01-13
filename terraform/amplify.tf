resource "aws_amplify_app" "frontend" {
  name       = "fitness-ai-coach"
  repository = "https://github.com/TPtobiaperosino/AI-Coach"
  platform   = "WEB_COMPUTE" # required for SSR (Next.js) on Amplify

  # The build_spec defines how Amplify builds the Next.js app
  build_spec = <<-EOT
    version: 1
    applications:
      - appRoot: frontend
        frontend:
          phases:
            preBuild:
              commands:
                - npm ci
            build:
              commands:
                - npm run build
          artifacts:
            baseDirectory: .next
            files:
              - '**/*'
          cache:
            paths:
              - node_modules/**/*
  EOT

  # Environment variables for the build process
  environment_variables = {
    NEXT_PUBLIC_API_BASE      = aws_apigatewayv2_api.http_api.api_endpoint
    NODE_VERSION              = "20"
    AMPLIFY_MONOREPO_APP_ROOT = "frontend"
  }

  access_token = var.github_token
}

resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.frontend.id
  branch_name = "main"

  # Framework must be set for Next.js SSR apps
  # However, in modern Amplify (Gen 2 or late Gen 1), it often detects it
  # We set it specifically to avoid issues.
  framework = "Next.js - SSR"
}
