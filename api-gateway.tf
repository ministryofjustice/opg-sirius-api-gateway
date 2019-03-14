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

resource "aws_api_gateway_domain_name" "opg_api_gateway" {
  domain_name              = "api.${local.opg_sirius_hosted_zone}"
  regional_certificate_arn = "${data.aws_acm_certificate.sirius_opg_digital.arn}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

data "aws_route53_zone" "sirius_opg_digital" {
  name = "${local.opg_sirius_hosted_zone}."
}

data "aws_acm_certificate" "sirius_opg_digital" {
  domain      = "*.${local.opg_sirius_hosted_zone}"
  types       = ["AMAZON_ISSUED"]
  most_recent = true
}

resource "aws_route53_record" "opg_api_gateway" {
  name    = "api.${local.opg_sirius_hosted_zone}"
  type    = "A"
  zone_id = "${data.aws_route53_zone.sirius_opg_digital.id}"

  alias {
    evaluate_target_health = true
    name                   = "${aws_api_gateway_domain_name.opg_api_gateway.regional_domain_name}"
    zone_id                = "${aws_api_gateway_domain_name.opg_api_gateway.regional_zone_id}"
  }
}

output "opg_sirius_api_gateway_custom_url" {
  value = "${aws_api_gateway_domain_name.opg_api_gateway.domain_name}"
}
