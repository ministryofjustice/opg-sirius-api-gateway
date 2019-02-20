variable "lambda_name" {
  description = "Name for the lambda function and role policies that accompany it."
}

variable "lambda_function_filename" {
  description = "Relative path to file with lambda source code"
}

variable "lambda_runtime" {
  description = "Language used for the lambda function"
  default     = "python3.7"
}

variable "security_group_ids" {
  type        = "list"
  description = "List of security group IDs for lambda function vpc_config"
}

variable "api_gateway" {
  description = "API gateway REST API to attach lambda functions to"
}

variable "account_id" {
  description = "AWS account number"
}

variable "api_gateway_deployment_stage" {
  description = "The name of the deployment stage. If the specified stage already exists, it will be updated to point to the new deployment. If the stage does not exist, a new one will be created and point to this deployment"
}

variable "permitted_consumer_roles" {
  description = "Cross account IAM roles that are permitted to use the API resource, in ARN format"
  type        = "list"
  default     = []
}

variable "vpc" {
  description = "Name of vpc to target"
}

variable "environment" {
  description = "Environment configuration for the Lambda function"
  type        = "map"
  default     = {}
}

variable "tags" {
  description = "A mapping of tags"
  type        = "map"
  default     = {}
}
