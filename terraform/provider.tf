terraform {
  backend "s3" {
    encrypt        = true
    region         = "us-east-1"
    bucket         = "apopora-tf-state-bucket"
    dynamodb_table = "tf-state-table"
    key            = "pi-lamp"
  }
}

provider "aws" {
  region = var.region
}

#role_arn       = "arn:aws:iam::${var.account_id}:role/terraform-remote-state/tf-state-management"

