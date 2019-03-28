
module "sirius_access_test_lambda" {
  source = "modules/lambda"

  lambda_name              = "sirius_access_test"
  lambda_function_filename = "./lambdas/lpas_collection_lambda.zip"
  lambda_handler           = "test_handler"

  security_group_ids = [
    "${aws_security_group.lpas_collection.id}",
  ]

  vpc = "${local.vpc_name}"

  environment {
    variables {
      CREDENTIALS = "${data.aws_secretsmanager_secret_version.sirius_credentials.secret_string}"
    }
  }

  tags = "${local.default_tags}"
}
