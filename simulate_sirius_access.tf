module "sirius_access_test_lambda" {
  source = "modules/lambda"

  lambda_name              = "simulate_sirius_access"
  lambda_function_filename = "./lambda_artifact.zip"
  lambda_handler           = "test_handler"

  security_group_ids = [
    "${data.aws_security_group.lambda.id}",
  ]

  vpc = "${local.vpc_name}"

  dynamodb_auth_cache_table = "${aws_dynamodb_table.auth_cache.arn}"
  dynamodb_data_cache_table = "${aws_dynamodb_table.data_cache.arn}"

  environment {
    variables {
      CREDENTIALS  = "${data.aws_secretsmanager_secret_version.sirius_credentials.secret_string}"
      URL_MEMBRANE = "http://membrane.${local.target_environment}.ecs"
    }
  }

  tags = "${local.default_tags}"
}
