data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Stack"
    values = ["${local.vpc_name}"]
  }
}

resource "aws_security_group" "hello_world" {
  name        = "hello_world"
  description = "hello_world Security Group"
  vpc_id      = "${data.aws_vpc.vpc.id}"
}

data "archive_file" "hello_world_lambda_archive" {
  type        = "zip"
  source_dir  = "${path.module}/hello_world_lambda/"
  output_path = "${path.module}/hello_world_lambda/hello_world_lambda.zip"
}

module "hello_world" {
  source = "modules/api_gateway_lambda_function"

  lambda_name              = "hello_world"
  lambda_function_filename = "${data.archive_file.hello_world_lambda_archive.output_path}"
  lambda_runtime           = "python3.7"

  security_group_ids = [
    "${aws_security_group.hello_world.id}",
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

output "hello_world_invoke_url" {
  value = "${module.hello_world.lambda_name} invoke URL: ${module.hello_world.lambda_invoke_url}"
}
