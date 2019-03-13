//---------------------
// Gateway resource details

variable "api_gateway_id" {
  description = "The ID of the REST API"
}

variable "api_gateway_root_resource_id" {
  description = "The resource ID of the REST API's root"
}

variable "api_gateway_execution_arn" {
  description = "Execution ARN for the gateway"
}

//---------------------
// Path details

variable "gateway_path_product" {
  description = "Slug representing the product's namespace"
}

variable "gateway_path_collection" {
  description = "Pluralise collection name"
}

variable "gateway_path_id_name" {
  description = "The parameter name to use for the resource id"
}

//---------------------
// Lambda details

variable "lambda_arn" {
  description = "ARN of the lambda which this endpoint will invoke."
}

variable "lambda_name" {
  description = "The name of the lambda function"
}
