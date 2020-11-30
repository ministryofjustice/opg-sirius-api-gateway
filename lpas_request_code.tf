module "lpas_request_code_lambda" {
  source = "modules/lambda"

  lambda_name              = "LpasRequestCodeHandler"
  lambda_function_filename = "./lambda_artifact.zip"
  lambda_handler           = "handler"

  security_group_ids = [
    "${data.aws_security_group.lambda.id}",
  ]

  vpc = "${local.vpc_name}"

  dynamodb_auth_cache_table = "${aws_dynamodb_table.auth_cache.arn}"
  dynamodb_data_cache_table = "${aws_dynamodb_table.data_cache.arn}"

  environment {
    variables {
      CREDENTIALS                    = "${data.aws_secretsmanager_secret_version.sirius_credentials.secret_string}"
      URL_MEMBRANE                   = "http://membrane.${local.target_environment}.ecs"
      DYNAMODB_AUTH_CACHE_TABLE_NAME = "${aws_dynamodb_table.auth_cache.name}"
      DYNAMODB_DATA_CACHE_TABLE_NAME = "${aws_dynamodb_table.data_cache.name}"
    }
  }

  tags = "${local.default_tags}"
}

module "use_an_lpa_lpas_request_code" {
  source = "modules/api_gateway_get_collection_id"

  api_gateway_id               = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
  api_gateway_root_resource_id = "${aws_api_gateway_rest_api.opg_api_gateway.root_resource_id}"
  api_gateway_execution_arn    = "${aws_api_gateway_rest_api.opg_api_gateway.execution_arn}"

  gateway_path_product    = "use-an-lpa2" // change me
  gateway_path_collection = "requestCode"
  gateway_path_id_name    = "{sirius_uid}"

  lambda_arn  = "${module.lpas_request_code_lambda.lambda_arn}"
  lambda_name = "${module.lpas_request_code_lambda.lambda_name}"
}

resource "aws_iam_role_policy_attachment" "use_an_lpa_lpas_request_code_access_policy" {
  role       = "${aws_iam_role.use_an_lpa_role.name}"
  policy_arn = "${module.use_an_lpa_lpas_request_code.access_policy_arn}"
}
