terraform {
  backend "s3" {
    bucket         = "opg.terraform.state"
    key            = "opg-sirius-api-gateway/terraform.tfstate"
    encrypt        = true
    region         = "eu-west-1"
    role_arn       = "arn:aws:iam::311462405659:role/state_write"
    dynamodb_table = "remote_lock"
  }
}

provider "aws" {
  region = "eu-west-1"

  assume_role {
    role_arn     = "arn:aws:iam::${lookup(local.target_account, "development")}:role/${var.default_role}"
    session_name = "terraform-session"
  }
}

#terraform.workspace
provider "aws" {
  region = "eu-west-1"
  alias  = "management"

  assume_role {
    role_arn     = "arn:aws:iam::311462405659:role/${var.management_role}"
    session_name = "terraform-session"
  }
}
