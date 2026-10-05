# A implementar: provider AWS usando var.aws_region e autenticação externa.
# Nunca inserir access keys neste arquivo.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.67.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "2.8.1"
    }
  }


  backend "s3" {
    bucket       = "joaosalesdev-terraform-state"
    key          = "portfolio-ai-assistant/dev/base/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}