# Defines endpoints for the lpas collection

//-------------------------------
// Pull in the secrets

data "aws_secretsmanager_secret" "sirius_credentials" {
  name = "${terraform.workspace}/sirius/credentials"
}

data "aws_secretsmanager_secret_version" "sirius_credentials" {
  secret_id = "${data.aws_secretsmanager_secret.sirius_credentials.id}"
}

//-------------------------------
// Setup the Lambda

resource "aws_security_group" "lpas_collection" {
  name        = "lpas_collection"
  description = "lpas_collection Security Group"
  vpc_id      = "${data.aws_vpc.vpc.id}"
}

module "lpas_collection_lambda" {
  source = "modules/lambda"

  lambda_name              = "lpas_collection"
  lambda_function_filename = "./lambdas/lpas_collection_lambda.zip"
  lambda_handler           = "id_handler"

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

//----------------------------------------------
// Setup LPA Online Tool gateway endpoint

module "lpa_online_tool_get_lpas_id" {
  source = "modules/api_gateway_get_collection_id"

  api_gateway_id               = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
  api_gateway_root_resource_id = "${aws_api_gateway_rest_api.opg_api_gateway.root_resource_id}"
  api_gateway_execution_arn    = "${aws_api_gateway_rest_api.opg_api_gateway.execution_arn}"

  gateway_path_product    = "lpa-online-tool"
  gateway_path_collection = "lpas"
  gateway_path_id_name    = "{lpa_online_tool_id}"

  lambda_arn  = "${module.lpas_collection_lambda.lambda_arn}"
  lambda_name = "${module.lpas_collection_lambda.lambda_name}"
}

// Give access to the relevant roles
resource "aws_iam_role_policy_attachment" "lpa_online_tool_get_lpas_id_access_policy" {
  role       = "${aws_iam_role.lpa_online_tool_role.name}"
  policy_arn = "${module.lpa_online_tool_get_lpas_id.access_policy_arn}"
}

//----------------------------------------------
// Setup Use my LPA gateway endpoint


// TODO

