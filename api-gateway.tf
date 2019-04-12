# Defines the gateway, its settings, and the deploy

//------------------------------------
// Setup account level logging
// TODO: Move out of product specific code

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

//------------------------------------
// Setup the API Gateway

resource "aws_api_gateway_rest_api" "opg_api_gateway" {
  name        = "opg-sirius-api-gateway-${terraform.workspace}"
  description = "OPG Sirius API Gateway - ${terraform.workspace}"
  policy      = "${data.aws_iam_policy_document.resource_policy.json}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

data "aws_iam_policy_document" "resource_policy" {
  statement {
    sid    = "onlinelpaaccess"
    effect = "Allow"

    principals {
      identifiers = [
        "${local.api_gateway_allowed_roles_online_lpa_tool}",
        "arn:aws:iam::631181914621:user/neil.smith",
      ]

      type = "AWS"
    }

    actions   = ["execute-api:Invoke"]
    //resources = ["arn:aws:execute-api:${data.aws_region.current.name}:${local.target_account}:*/*/GET/lpa-online-tool/lpas/*"]
    resources = ["${aws_api_gateway_rest_api.opg_api_gateway.execution_arn}:*/*/GET/lpa-online-tool/lpas/*"]
  }
}

//------------------------------------
// Deploy the gateway

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
  stage_name  = "testing"

  // The policy is dependent on the module completing, so we can depend on that to mean everything is in place
  depends_on = ["aws_iam_role_policy_attachment.lpa_online_tool_get_lpas_id_access_policy"]

  variables {
    // Force a deploy on every apply.
    deployed_at = "${timestamp()}"
  }

  lifecycle {
    create_before_destroy = true
  }
}

//------------------------------------
// Stage level settings

resource "aws_api_gateway_method_settings" "global_gateway_settings" {
  rest_api_id = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
  stage_name  = "${aws_api_gateway_deployment.deployment.stage_name}"
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

resource "aws_api_gateway_domain_name" "opg_api_gateway" {
  domain_name              = "api.${local.opg_sirius_hosted_zone}"
  regional_certificate_arn = "${data.aws_acm_certificate.sirius_opg_digital.arn}"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_base_path_mapping" "mapping" {
  api_id      = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
  stage_name  = "${aws_api_gateway_deployment.deployment.stage_name}"
  domain_name = "${aws_api_gateway_domain_name.opg_api_gateway.domain_name}"
  base_path   = "${aws_api_gateway_deployment.deployment.stage_name}"
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
