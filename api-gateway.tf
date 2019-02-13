resource "aws_api_gateway_rest_api" "opg_api_gateway" {
  name        = "opg-api-gateway-${terraform.workspace}"
  description = "OPG's API Gateway"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}
