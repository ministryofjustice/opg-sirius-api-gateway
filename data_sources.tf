data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "allow_assume_role" {
  statement {
    effect = "Allow"

    principals = {
      type        = "AWS"
      identifiers = ["arn:aws:iam::357766484745:root"]
    }

    actions = ["sts:AssumeRole"]
  }
}
