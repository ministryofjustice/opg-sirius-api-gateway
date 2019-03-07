resource "aws_security_group" "lpa_status" {
  name        = "lpa_status"
  description = "LPA Status Security Group"
  vpc_id      = "${data.aws_vpc.vpc.id}"
}

module "lpa_status" {
  source = "modules/api_gateway_lambda_function"

  lambda_name              = "lpa_status"
  lambda_function_filename = "~/lambdas/lpa_status_lambda.zip"
  lambda_runtime           = "python3.7"

  security_group_ids = [
    "${aws_security_group.lpa_status.id}",
  ]

  vpc                          = "${local.vpc_name}"
  account_id                   = "${local.target_account}"
  api_gateway                  = "${aws_api_gateway_rest_api.opg_api_gateway.name}"
  api_gateway_deployment_stage = "testing-0-0-1"

  permitted_consumer_roles = [
    "arn:aws:iam::${lookup(local.accounts, "sandbox")}:root",
    "arn:aws:iam::${lookup(local.accounts, "sandbox")}:role/SandboxPoweruser",
    "arn:aws:iam::${lookup(local.accounts, "lpa-development")}:role/api2.*",
  ]

  environment {
    variables {
      USER = "user-one"
    }
  }

  tags = "${local.default_tags}"
}

output "lpa_status_invoke_url" {
  value = "${module.lpa_status.lambda_name} invoke URL: ${module.lpa_status.lambda_invoke_url}"
}
