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

  security_group_ids = [
    "${data.aws_security_group.default.id}",
  ]

  vpc                          = "${lookup(local.vpc, terraform.workspace)}"
  account_id                   = "${lookup(local.target_account, terraform.workspace)}"
  api_gateway                  = "opg-api-gateway"
  api_gateway_deployment_stage = "testing-0-0-1"

  permitted_consumer_roles = [
    "arn:aws:iam::${lookup(local.accounts, "sandbox")}:root",
    "arn:aws:iam::${lookup(local.accounts, "sandbox")}:role/SandboxPoweruser",
    "arn:aws:iam::${lookup(local.accounts, "lpa-development")}:role/api2.staging04",
  ]
}

output "lambda_invoke_url" {
  value = "${module.lpa_status.lambda_name} invoke URL: ${module.lpa_status.lambda_invoke_url}"
}
