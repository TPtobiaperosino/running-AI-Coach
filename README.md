# running-AI-Coach
Architecture Overview

This project implements a serverless, AI-powered web application on AWS, designed for scalability, security, and rapid iteration. The architecture follows AWS best practices and is fully provisioned using Terraform (Infrastructure as Code).

High-level flow

Users interact with a web frontend hosted on AWS Amplify

Authentication is handled via Amazon Cognito User Pools (JWT-based auth)

Authenticated requests are sent to Amazon API Gateway (HTTP API)

API Gateway invokes AWS Lambda for backend compute

Lambda:

processes inputs

optionally stores files in Amazon S3 (private, via presigned URLs)

persists metadata and results in Amazon DynamoDB

invokes Amazon Bedrock for AI inference

Results are returned to the frontend via the API

Core components

Frontend: AWS Amplify (React / Next.js)

Authentication: Amazon Cognito User Pool

API Layer: API Gateway (HTTP API)

Compute: AWS Lambda (stateless, event-driven)

File Storage: Amazon S3 (private buckets, presigned access)

Data Storage: Amazon DynamoDB (NoSQL)

AI / ML: Amazon Bedrock

Infrastructure: Terraform (AWS provider, assume-role via STS)

Security: IAM least-privilege roles, no direct client access to backend resources

Design principles

Serverless-first: no servers to manage, automatic scaling

Stateless compute: Lambdas are independent and replaceable

Secure by default: private storage, JWT authorization, scoped IAM roles

Modular IaC: services can be added or modified without refactoring

MVP-friendly, production-ready: minimal initial scope with a clear path to hardening

Cost considerations

Most services fall within the AWS Free Tier at MVP scale

Amazon Bedrock is usage-based and not free tier, but costs remain low for limited inference volumes