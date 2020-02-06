# Defines the gateway, its settings, and the deploy

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
      ]

      type = "AWS"
    }

    actions = ["execute-api:Invoke"]

    // API Gateway will add all of the rest of the ARN details in for us. Provents a circular dependency.
    resources = ["execute-api:/*/GET/lpa-online-tool/*"]
  }

  statement {
    sid    = "useanlpaaccess"
    effect = "Allow"

    principals {
      identifiers = [
        "${local.api_gateway_allowed_roles_use_an_lpa}",
      ]

      type = "AWS"
    }

    actions = ["execute-api:Invoke"]

    // API Gateway will add all of the rest of the ARN details in for us. Provents a circular dependency.
    resources = ["execute-api:/*/GET/use-an-lpa/*"]
  }
}

//------------------------------------
// Deploy the gateway

resource "aws_api_gateway_deployment" "deployment_v1" {
  rest_api_id = "${aws_api_gateway_rest_api.opg_api_gateway.id}"
  stage_name  = "v1"

  // The policy is dependent on the module completing, so we can depend on that to mean everything is in place
  depends_on = [
    "aws_iam_role_policy_attachment.lpa_online_tool_get_lpas_id_access_policy",
    "aws_iam_role_policy_attachment.use_an_lpa_get_sirius_uid_access_policy",
  ]

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
  stage_name  = "${aws_api_gateway_deployment.deployment_v1.stage_name}"
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
  stage_name  = "${aws_api_gateway_deployment.deployment_v1.stage_name}"
  domain_name = "${aws_api_gateway_domain_name.opg_api_gateway.domain_name}"
  base_path   = "${aws_api_gateway_deployment.deployment_v1.stage_name}"
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
