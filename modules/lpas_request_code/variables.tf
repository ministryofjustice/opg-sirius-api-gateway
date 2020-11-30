variable "api_gateway_id" {
  description = "The ID of your REST API"
}

variable "api_gateway_root_resource_id" {
  description = "The resource ID of your REST API's root"
}

variable "api_gateway_execution_arn" {
  description = "Execution ARN for your gateway"
}

variable "lambda_arn" {
  description = "ARN of your lambda which this endpoint will invoke"
}

variable "lambda_name" {
  description = "The name of your lambda function"
}
