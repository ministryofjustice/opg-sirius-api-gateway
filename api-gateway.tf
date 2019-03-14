resource "aws_api_gateway_rest_api" "opg_api_gateway" {
  name        = "opg-sirius-api-gateway-${terraform.workspace}"
  description = "OPG Sirius API Gateway - ${terraform.workspace}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_account" "opg_api_gateway" {
  cloudwatch_role_arn = "${aws_iam_role.cloudwatch.arn}"
}

resource "aws_iam_role" "cloudwatch" {
  name = "api_gateway_cloudwatch_global"

  assume_role_policy = "${data.aws_iam_policy_document.assume_role.json}"
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "log_to_cloudwatch" {
  role       = "${aws_iam_role.cloudwatch.id}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}


resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
  stage_name  = "more-testing"

  // The policy is dependent on the module completing, so we can depend on that to mean everything is in place
  depends_on  = ["aws_iam_role_policy_attachment.lpa_online_tool_get_lpas_id_access_policy"]

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_method_settings" "global_gateway_settings" {
  depends_on = ["aws_api_gateway_deployment.deployment"]

  rest_api_id = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
  stage_name  = "more-testing"
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}
