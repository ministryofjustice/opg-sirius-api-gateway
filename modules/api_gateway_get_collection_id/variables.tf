//---------------------
// Gateway resource details

variable "api_gateway_id" {
  description = "The ID of your REST API"
}

variable "api_gateway_root_resource_id" {
  description = "The resource ID of your REST API's root"
}

variable "api_gateway_execution_arn" {
  description = "Execution ARN for your gateway"
}

//---------------------
// Path details

variable "gateway_path_product" {
  description = "Slug representing your product's namespace"
}

variable "gateway_path_collection" {
  description = "Pluralise name of your collection"
}

variable "gateway_path_id_name" {
  description = "The parameter name to use for your resource id. For example: {id}"
}

//---------------------
// Lambda details

variable "lambda_arn" {
  description = "ARN of your lambda which this endpoint will invoke"
}

variable "lambda_name" {
  description = "The name of your lambda function"
}
