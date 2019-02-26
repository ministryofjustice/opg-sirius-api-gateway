output "lambda_invoke_url" {
  description = "The URL to invoke the API pointing to the stage, e.g. https://z4675bid1j.execute-api.eu-west-2.amazonaws.com/prod"
  value       = "${aws_api_gateway_deployment.deployment.invoke_url}"
}

output "lambda_name" {
  description = "The unique name for your Lambda Function"
  value       = "${aws_lambda_function.lambda_function.function_name}"
}
