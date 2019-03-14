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
  domain_name              = "api.sirius.opg.digital"
  regional_certificate_arn = "${aws_acm_certificate_validation.opg_api_gateway.certificate_arn}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Domain names and Certificates are provisioned in the Management account
data "aws_route53_zone" "sirius_opg_digital" {
  name = "sirius.opg.digital."
}

resource "aws_route53_record" "opg_api_gateway" {
  name    = "api.sirius.opg.digital"
  type    = "A"
  zone_id = "${data.aws_route53_zone.sirius_opg_digital.id}"

  alias {
    evaluate_target_health = true
    name                   = "${aws_api_gateway_domain_name.opg_api_gateway.regional_domain_name}"
    zone_id                = "${aws_api_gateway_domain_name.opg_api_gateway.regional_zone_id}"
  }
}

resource "aws_acm_certificate" "opg_api_gateway" {
  domain_name       = "api.sirius.opg.digital"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "opg_api_gateway_certificate_validation" {
  name    = "${aws_acm_certificate.opg_api_gateway.domain_validation_options.0.resource_record_name}"
  type    = "${aws_acm_certificate.opg_api_gateway.domain_validation_options.0.resource_record_type}"
  zone_id = "${data.aws_route53_zone.sirius_opg_digital.id}"
  records = ["${aws_acm_certificate.opg_api_gateway.domain_validation_options.0.resource_record_value}"]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "opg_api_gateway" {
  certificate_arn         = "${aws_acm_certificate.opg_api_gateway.arn}"
  validation_record_fqdns = ["${aws_route53_record.opg_api_gateway_certificate_validation.fqdn}"]
}

output "opg_sirius_api_gateway_custom_url" {
  value = "${aws_api_gateway_domain_name.opg_api_gateway.domain_name}"
}
