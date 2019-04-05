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
        "${local.lpa_tool_api2_role}",

        # "${local.lpa_sources_dev}",
        "arn:aws:iam::631181914621:user/andrew.pearce",

        "arn:aws:iam::631181914621:user/neil.smith",
      ]
    }
  }
}
