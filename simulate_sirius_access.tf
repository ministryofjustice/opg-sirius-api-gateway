
module "sirius_access_test_lambda" {
  source = "modules/lambda"

  lambda_name              = "simulate_sirius_access"
  lambda_function_filename = "./lambda_artifact.zip"
  lambda_handler           = "test_handler"

  security_group_ids = [
    "${aws_security_group.lambda.id}",
    "${data.aws_security_group.membrane_client.id}"
  ]

  vpc = "${local.vpc_name}"

  environment {
    variables {
      CREDENTIALS = "${data.aws_secretsmanager_secret_version.sirius_credentials.secret_string}"
      URL_MEMBRANE = "https://${local.membrane_hostname}"
    }
  }

  tags = "${local.default_tags}"
}
