
output "access_policy_arn" {
  description = "Policy ARN for accessing the endpoint. Add this to your user/group/role."
  value       = "${aws_iam_policy.opg_api_gateway_access_policy.arn}"
}
