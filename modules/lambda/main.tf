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

  environment = ["${slice( list(var.environment), 0, length(var.environment) == 0 ? 0 : 1 )}"]
  tags        = "${var.tags}"
}