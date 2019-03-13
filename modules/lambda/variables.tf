variable "lambda_name" {
  description = "Name for the lambda function and role policies that accompany it."
}

variable "lambda_handler" {
  description = "The function entrypoint in your code."
  default     = "handler"
}

variable "lambda_function_filename" {
  description = "Relative path to file with lambda source code"
}


variable "tags" {
  description = "A mapping of tags"
  type        = "map"
  default     = {}
}

variable "vpc" {
  description = "Name of vpc to target"
}

variable "security_group_ids" {
  type        = "list"
  description = "List of security group IDs for lambda function vpc_config"
}

variable "environment" {
  description = "Environment configuration for the Lambda function"
  type        = "map"
  default     = {}
}
