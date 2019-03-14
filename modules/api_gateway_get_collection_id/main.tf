
# Defines a single HTTP endpoint representing a product, collection and resource id
# The schema is: /<product>/<collection>/{id}

data "aws_region" "current" {}

//-------------------------------------
// Setup the resource chain

resource "aws_api_gateway_resource" "gateway_resource_product" {
  rest_api_id = "${var.api_gateway_id}"
  parent_id   = "${var.api_gateway_root_resource_id}"

  path_part   = "${var.gateway_path_product}"   // eg. lpa-online-tool
}

resource "aws_api_gateway_resource" "gateway_resource_collection" {
  rest_api_id = "${var.api_gateway_id}"
  parent_id   = "${aws_api_gateway_resource.gateway_resource_product.id}"

  path_part   = "${var.gateway_path_collection}"    // eg. lpas
}

resource "aws_api_gateway_resource" "gateway_resource_collection_resource" {
  rest_api_id = "${var.api_gateway_id}"
  parent_id   = "${aws_api_gateway_resource.gateway_resource_collection.id}"

  path_part   = "${var.gateway_path_id_name}"    // eg. {lpa_online_tool_id}
}

//-------------------------------------
// Setup the method

resource "aws_api_gateway_method" "gateway_resource_collection_resource_get" {
  rest_api_id = "${var.api_gateway_id}"
  resource_id   = "${aws_api_gateway_resource.gateway_resource_collection_resource.id}"
  http_method   = "GET"
  authorization = "AWS_IAM"
}

//-------------------------------------
// Setup the integration

resource "aws_api_gateway_integration" "gateway_lpa_online_tool_lpas_collection_resource_get_integration" {
  rest_api_id             = "${var.api_gateway_id}"
  resource_id             = "${aws_api_gateway_resource.gateway_resource_collection_resource.id}"
  http_method             = "${aws_api_gateway_method.gateway_resource_collection_resource_get.http_method}"
  integration_http_method = "POST"  # We POST to Lambda, even on a HTTP GET.

  type                    = "AWS_PROXY"
  content_handling        = "CONVERT_TO_TEXT"

  uri                     = "arn:aws:apigateway:${data.aws_region.current.name}:lambda:path/2015-03-31/functions/${var.lambda_arn}/invocations"
}

//-------------------------------------
// Configure the endpoint's permissions

// Allow the endpoint to invoke the lambda.
resource "aws_lambda_permission" "gateway_lambda_permission" {
  depends_on = ["aws_api_gateway_resource.gateway_resource_collection_resource"]

  statement_id  = "AllowOpgApiGatewayInvoke_${var.gateway_path_product}_${var.gateway_path_collection}_id"
  action        = "lambda:InvokeFunction"
  function_name = "${var.lambda_name}"
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path within API Gateway REST API.
  source_arn = "${var.api_gateway_execution_arn}/*/${aws_api_gateway_method.gateway_resource_collection_resource_get.http_method}${aws_api_gateway_resource.gateway_resource_collection_resource.path}"
}


//-------------------------------------
// Configure the endpoint's access policy
// i.e. who can access the endpoint

// Generate a policy that allowed the endpoint to be called from a user/group/role.
data "aws_iam_policy_document" "gateway_resource_execution_policy" {
  statement {
    sid = "OPGApiGatewayAccessPolicy"

    actions = [
      "execute-api:Invoke"
    ]

    resources = [
      "${var.api_gateway_execution_arn}/*/*${aws_api_gateway_resource.gateway_resource_product.path}/*",
    ]
  }
}

resource "aws_iam_policy" "opg_api_gateway_access_policy" {
  name   = "${var.gateway_path_product}_${var.gateway_path_collection}_access_policy"
  path   = "/"
  policy = "${data.aws_iam_policy_document.gateway_resource_execution_policy.json}"
}
