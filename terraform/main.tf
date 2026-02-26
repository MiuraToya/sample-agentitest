terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    key = "terraform.tfstate"
    # bucket, region, dynamodb_table, profile は backend.tfvars で指定
    # terraform init -backend-config=backend.tfvars
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

# CloudFront requires ACM certs in us-east-1, but we don't need custom domain
# so no alias provider needed
