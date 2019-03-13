
// -----------------------------------------------------------
// LPA Online Tool

resource "aws_iam_role" "lpa_online_tool_role" {
  name = "sirius-api-gateway-access-lpa-online-tool"
  assume_role_policy = "${data.aws_iam_policy_document.lpa_online_tool_role_cross_account_policy.json}"
}

// Access policy, defining who and assume this role
data "aws_iam_policy_document" "lpa_online_tool_role_cross_account_policy" {
  statement {
    sid = "assume-role-policy-sirius-api-gateway-access-lpa-online-tool"

    actions = [
      "sts:AssumeRole"
    ]

    principals {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${lookup(local.accounts, "sandbox")}:root",
        "arn:aws:iam::${lookup(local.accounts, "sandbox")}:role/SandboxPoweruser",
        "arn:aws:iam::${lookup(local.accounts, "lpa-development")}:role/api2.staging04",
      ]
    }

  }
}
