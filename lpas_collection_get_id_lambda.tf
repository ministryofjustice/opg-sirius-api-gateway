resource "aws_security_group" "lpas_collection" {
  name        = "lpas_collection"
  description = "lpas_collection Security Group"
  vpc_id      = "${data.aws_vpc.vpc.id}"
}

module "lpas_collection" {
  source = "modules/api_gateway_lambda_function"

  lambda_name              = "lpas_collection"
  lambda_function_filename = "./lambdas/lpas_collection_lambda.zip"
  lambda_runtime           = "python3.7"

  security_group_ids = [
    "${aws_security_group.lpas_collection.id}",
  ]

  vpc                          = "${local.vpc_name}"
  account_id                   = "${local.target_account}"
  api_gateway                  = "${aws_api_gateway_rest_api.opg_api_gateway.name}"
  api_gateway_deployment_stage = "testing-0-0-1"

  permitted_consumer_roles = [
    "arn:aws:iam::${lookup(local.accounts, "sandbox")}:root",
    "arn:aws:iam::${lookup(local.accounts, "sandbox")}:role/SandboxPoweruser",
    "arn:aws:iam::${lookup(local.accounts, "lpa-development")}:role/api2.staging04",
  ]

  environment {
    variables {
      USER = "user-one"
    }
  }

  tags = "${local.default_tags}"
}

output "lpas_collection_invoke_url" {
  value = "${module.lpas_collection.lambda_name} invoke URL: ${module.lpas_collection.lambda_invoke_url}"
}
