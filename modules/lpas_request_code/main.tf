data "aws_region" "current" {}

resource "aws_api_gateway_resource" "resource" {
  rest_api_id = "${var.api_gateway_id}"
  parent_id   = "${var.api_gateway_root_resource_id}"

  path_part = "requestCode"
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = "${var.api_gateway_id}"
  resource_id   = "${aws_api_gateway_resource.resource.id}"
  http_method   = "POST"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = "${var.api_gateway_id}"
  resource_id             = "${aws_api_gateway_resource.resource.id}"
  http_method             = "${aws_api_gateway_method.method.http_method}"
  integration_http_method = "POST"

  type             = "AWS_PROXY"
  content_handling = "CONVERT_TO_TEXT"

  uri = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${var.lambda_arn}/invocations"
}

resource "aws_lambda_permission" "permission" {
  depends_on = ["aws_api_gateway_resource.resource"]

  statement_id  = "AllowOpgApiGatewayInvoke_lpas_request_code_id"
  action        = "lambda:InvokeFunction"
  function_name = "${var.lambda_name}"
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway REST API.
  source_arn = "${var.api_gateway_execution_arn}/*/${aws_api_gateway_method.method.http_method}${aws_api_gateway_resource.resource.path}"
}

data "aws_iam_policy_document" "policy_document" {
  statement {
    sid = "OPGApiGatewayAccessPolicy"

    actions = [
      "execute-api:Invoke",
    ]

    resources = [
      "${var.api_gateway_execution_arn}/*/*${aws_api_gateway_resource.resource.path}/*",
    ]
  }
}

resource "aws_iam_policy" "policy" {
  depends_on = ["aws_api_gateway_integration.integration"]

  name   = "lpas_request_code_policy"
  path   = "/"
  policy = "${data.aws_iam_policy_document.policy_document.json}"
}
