variable "lambda_name" {
  description = "Name of the lambda and role policy that accompanies it."
}

variable "lambda_function_filename" {
  description = "Relative path to file with lambda source code"
}

variable "lambda_runtime" {
  description = ""
  default     = "python3.7"
}

variable "security_group_ids" {
  type        = "list"
  description = "List of security group IDs for lambda function vpc_config"
}

variable "api_gateway" {
  description = "API gateway to use"
  default     = "opg-api-gateway"
}

variable "account_id" {
  description = "AWS account number"
}

variable "api_gateway_deployment_stage" {
  description = "The name of the stage. If the specified stage already exists, it will be updated to point to the new deployment. If the stage does not exist, a new one will be created and point to this deployment"
}

variable "permitted_consumer_roles" {
  description = "Cross account IAM roles to permit access to in ARN format"
  type        = "list"
  default     = []
}
