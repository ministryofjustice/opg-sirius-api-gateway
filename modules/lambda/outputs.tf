
output "lambda_arn" {
  description = "The ARN for your Lambda Function"
  value       = "${aws_lambda_function.lambda_function.arn}"
}

output "lambda_name" {
  description = "The unique name for your Lambda Function"
  value       = "${aws_lambda_function.lambda_function.function_name}"
}
