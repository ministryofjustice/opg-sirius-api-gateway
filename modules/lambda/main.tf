# Defines a single lambda function

data "aws_region" "current" {}
data "aws_availability_zones" "available" {}

//-------------------------------------
// Network configuration

data "aws_subnet" "private" {
  count             = 3
  availability_zone = "${data.aws_availability_zones.available.names[count.index]}"

  filter {
    name = "tag:Name"

    values = [
      "private-eu-west-1a",
      "private-eu-west-1b",
      "private-eu-west-1c",
    ]
  }
}

//-------------------------------------
// The lambda's execution role

resource "aws_iam_role" "iam_for_lambda" {
  name               = "${var.lambda_name}-invoke"
  assume_role_policy = "${data.aws_iam_policy_document.lambda_assume.json}"
  tags               = "${var.tags}"
}

resource "aws_iam_role_policy_attachment" "aws_lambda_vpc_access_execution_role" {
  role       = "${aws_iam_role.iam_for_lambda.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

data "aws_iam_policy_document" "iam_for_lambda_inline_execution_role" {
  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
    ]
    resources = [
      "${var.dynamodb_auth_cache_table}",
      "${var.dynamodb_data_cache_table}",
    ]
  }
}

resource "aws_iam_role_policy" "iam_for_lambda_inline_execution_role" {
  name   = "ViewerApplicationPermissions"
  policy = "${data.aws_iam_policy_document.iam_for_lambda_inline_execution_role.json}"
  role   = "${aws_iam_role.iam_for_lambda.id}"
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

//-------------------------------------
// The lambda function itself

resource "aws_lambda_function" "lambda_function" {
  function_name = "${var.lambda_name}"
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  handler       = "${var.lambda_name}.${var.lambda_handler}"
  runtime       = "python3.7"
  timeout       = 20
  memory_size   = 128

  filename         = "${var.lambda_function_filename}"
  source_code_hash = "${base64sha256(file("${var.lambda_function_filename}"))}"

  vpc_config {
    subnet_ids = [
      "${data.aws_subnet.private.*.id}",
    ]

    security_group_ids = ["${var.security_group_ids}"]
  }

  environment = ["${slice(list(var.environment), 0, length(var.environment) == 0 ? 0 : 1)}"]
  tags        = "${var.tags}"
}
