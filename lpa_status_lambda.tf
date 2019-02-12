data "aws_security_group" "default" {
  id = "sg-10537c76"
}

data "archive_file" "lpa_status_lambda_archive" {
  type        = "zip"
  source_dir  = "${path.module}/lpa_status_lambda/"
  output_path = "${path.module}/lpa_status_lambda/lpa_status_lambda.zip"
}

module "lpa_status" {
  source = "modules/api_gateway_lambda_function"

  lambda_name              = "lpa_status"
  lambda_function_filename = "${data.archive_file.lpa_status_lambda_archive.output_path}"
  lambda_runtime           = "python3.7"

  subnet_ids = [
    "${data.aws_subnet.private_1.id}",
    "${data.aws_subnet.private_2.id}",
    "${data.aws_subnet.private_3.id}",
  ]

  security_group_ids = [
    "${data.aws_security_group.default.id}",
  ]

  api_gateway                  = "opg-api-gateway"
  account_id                   = "${lookup(local.accounts, "opg-sirius-development")}"
  api_gateway_deployment_stage = "testing-0-0-1"

  permitted_consumer_roles = [
    "arn:aws:iam::${lookup(local.accounts, "sandbox")}:root",
    "arn:aws:iam::${lookup(local.accounts, "sandbox")}:role/SandboxPoweruser",
    "arn:aws:iam::${lookup(local.accounts, "lpa-development")}:role/api2.staging04",
  ]
}


data "aws_subnet" "private_1" {
  filter {
    name   = "tag:Name"
    values = ["private-1a.dev-vpc"]
  }
}

data "aws_subnet" "private_2" {
  filter {
    name   = "tag:Name"
    values = ["private-1b.dev-vpc"] # insert value here
  }
}

data "aws_subnet" "private_3" {
  filter {
    name   = "tag:Name"
    values = ["private-1c.dev-vpc"] # insert value here
  }
}
