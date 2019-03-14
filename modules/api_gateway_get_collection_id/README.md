# API Gateway: GET a Resource from a Collection

This module provisions 
* A single endpoint with the schema `/<product>/<collection>/{<id>}`
* An _Integration_ that links the endpoint to a passed lambda function.
* A function policy to access the lambda.
* A _policy_ that provides access to invoke the endpoint, ready to be attached to a user/group/role.

## Inputs
Are defined in `variables.tf`

## Outputs
Are defined in `outputs.tf`
