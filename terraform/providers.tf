# A implementar: provider AWS usando var.aws_region e autenticação externa.
# Nunca inserir access keys neste arquivo.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket       = "joaosalesdev-terraform-state"
    key          = "portfolio-ai/dev/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }


}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}