output "lambda_invoke_url" {
  value = "${aws_api_gateway_deployment.deployment.invoke_url}"
}

output "lambda_name" {
  value = "${aws_lambda_function.lambda_function.function_name}"
}
