data "aws_region" "current" {}
data "aws_availability_zones" "available" {}

data "aws_subnet" "private" {
  count             = 3
  availability_zone = "${data.aws_availability_zones.available.names[count.index]}"

  filter {
    name = "tag:Name"

    values = [
      "private-1a.${var.vpc}",
      "private-1b.${var.vpc}",
      "private-1c.${var.vpc}",
    ]
  }
}

# Lambda Function IAM
resource "aws_iam_role" "iam_for_lambda" {
  name               = "${var.lambda_name}-invoke"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_assume.json}"
  tags               = "${var.tags}"
}

resource "aws_iam_role_policy_attachment" "aws_lambda_vpc_access_execution_role" {
  role       = "${aws_iam_role.iam_for_lambda.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    sid = "OPGAPIGatewayLambdaInvoke"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# Lambda Function
resource "aws_lambda_function" "lambda_function" {
  function_name = "${var.lambda_name}"
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  handler       = "lambda_function.handler"
  runtime       = "${var.lambda_runtime}"
  timeout       = 60
  memory_size   = 128

  filename         = "${var.lambda_function_filename}"
  source_code_hash = "${base64sha256(file("${var.lambda_function_filename}"))}"

  vpc_config {
    subnet_ids = [
      "${data.aws_subnet.private.*.id}",
    ]

    security_group_ids = ["${var.security_group_ids}"]
  }

  environment = ["${slice( list(var.environment), 0, length(var.environment) == 0 ? 0 : 1 )}"]
  tags        = "${var.tags}"
}

# Add api gateway route
data "aws_api_gateway_rest_api" "api_gateway_rest_api" {
  name = "${var.api_gateway}"
}

resource "aws_api_gateway_resource" "gateway_resource" {
  rest_api_id = "${data.aws_api_gateway_rest_api.api_gateway_rest_api.id}"
  parent_id   = "${data.aws_api_gateway_rest_api.api_gateway_rest_api.root_resource_id}"
  path_part   = "${var.lambda_name}"
}

resource "aws_api_gateway_method" "gateway_method_get" {
  rest_api_id   = "${data.aws_api_gateway_rest_api.api_gateway_rest_api.id}"
  resource_id   = "${aws_api_gateway_resource.gateway_resource.id}"
  http_method   = "GET"
  authorization = "AWS_IAM"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = "${data.aws_api_gateway_rest_api.api_gateway_rest_api.id}"
  resource_id             = "${aws_api_gateway_resource.gateway_resource.id}"
  http_method             = "${aws_api_gateway_method.gateway_method_get.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  content_handling        = "CONVERT_TO_TEXT"
  uri                     = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${aws_lambda_function.lambda_function.arn}/invocations"
}

# Give API Gateway permissions to execute the Lambda
resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowOpgApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda_function.function_name}"
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${data.aws_region.current.name}:${var.account_id}:${data.aws_api_gateway_rest_api.api_gateway_rest_api.id}/*/${aws_api_gateway_method.gateway_method_get.http_method}${aws_api_gateway_resource.gateway_resource.path}"
}

# Deploy the Gateway Stage

resource "aws_api_gateway_deployment" "deployment" {
  depends_on  = ["aws_api_gateway_integration.integration", "aws_lambda_permission.lambda_permission"]
  rest_api_id = "${data.aws_api_gateway_rest_api.api_gateway_rest_api.id}"
  stage_name  = "${var.api_gateway_deployment_stage}"

  lifecycle {
    create_before_destroy = true
  }
}

# OPG API Gateway Access Policy
resource "aws_iam_role" "opg_api_endpoint_access" {
  name               = "${var.lambda_name}_opg_api_endpoint_access"
  assume_role_policy = "${data.aws_iam_policy_document.cross_account_access_lpa.json}"
}

resource "aws_iam_role_policy_attachment" "opg_api_gateway_access_policy" {
  role       = "${aws_iam_role.opg_api_endpoint_access.name}"
  policy_arn = "${aws_iam_policy.opg_api_endpoint_access.arn}"
}

resource "aws_iam_policy" "opg_api_endpoint_access" {
  name   = "${var.lambda_name}_opg_api_endpoint_access"
  path   = "/"
  policy = "${data.aws_iam_policy_document.opg_api_endpoint_access.json}"
}

data "aws_iam_policy_document" "opg_api_endpoint_access" {
  statement {
    sid = "OPGApiGatewayAccessPolicy"

    actions = [
      "execute-api:Invoke",
    ]

    resources = ["arn:aws:execute-api:${data.aws_region.current.name}:${var.account_id}:${data.aws_api_gateway_rest_api.api_gateway_rest_api.id}/${aws_api_gateway_deployment.deployment.stage_name}/${aws_api_gateway_method.gateway_method_get.http_method}${aws_api_gateway_resource.gateway_resource.path}"]
  }
}

# Cross account roles that can access this lambda/endpoint
data "aws_iam_policy_document" "cross_account_access_lpa" {
  statement {
    sid = "CrossAccountApiGatewayAccessPolicy"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type = "AWS"

      identifiers = "${var.permitted_consumer_roles}"
    }
  }
}
