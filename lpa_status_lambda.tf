data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Stack"
    values = ["${local.vpc_name}"]
  }
}

resource "aws_security_group" "lpa_status_allow_all" {
  name        = "lpa_status-allow_all"
  description = "Allow all inbound traffic"
  vpc_id      = "${data.aws_vpc.vpc.id}"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
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
    "${aws_security_group.lpa_status_allow_all.id}",
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

output "lambda_invoke_url" {
  value = "${module.lpa_status.lambda_name} invoke URL: ${module.lpa_status.lambda_invoke_url}"
}
