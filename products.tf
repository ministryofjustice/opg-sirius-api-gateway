# Defines products that have access to endpoint on the Gateway

// -----------------------------------------------------------
// LPA Online Tool

resource "aws_iam_role" "lpa_online_tool_role" {
  name               = "sirius-api-gateway-access-lpa-online-tool"
  assume_role_policy = "${data.aws_iam_policy_document.lpa_online_tool_role_cross_account_policy.json}"
}

// Access policy, defining who and assume this role
data "aws_iam_policy_document" "lpa_online_tool_role_cross_account_policy" {
  statement {
    sid = "CrossAccountApiGatewayAccessPolicy"

    actions = [
      "sts:AssumeRole",
    ]

    principals {
      type = "AWS"

      identifiers = [
        "${local.api_gateway_allowed_roles}",
        "${local.api_gateway_allowed_users}",
      ]
    }
  }
}
