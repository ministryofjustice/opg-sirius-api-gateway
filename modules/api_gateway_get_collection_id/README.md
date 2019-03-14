# API Gateway: GET a Resource from a Collection

This module provisions 
* A single endpoint with the schema `/<product>/<collection>/{<id>}`
* An _Integration_ that links the endpoint to a passed lambda function.
* A function policy to access the lambda.
* A _policy_ that provides access to invoke the endpoint, ready to be attached to a user/group/role.

## Inputs

| Name                             | Description                                                       |  Type  | Default | Required |
| -------------------------------- | ----------------------------------------------------------------- | :----: | :-----: | :------: |
| api\_gateway\_execution\_arn     | Execution ARN for your gateway                                    | string |    -    |   yes    |
| api\_gateway\_id                 | The ID of your REST API                                           | string |    -    |   yes    |
| api\_gateway\_root\_resource\_id | The resource ID of your REST API's root                           | string |    -    |   yes    |
| gateway\_path\_collection        | Pluralise name of your collection                                 | string |    -    |   yes    |
| gateway\_path\_id\_name          | The parameter name to use for your resource id. For example: {id} | string |    -    |   yes    |
| gateway\_path\_product           | Slug representing your product's namespace                        | string |    -    |   yes    |
| lambda\_arn                      | ARN of your lambda which this endpoint will invoke                | string |    -    |   yes    |
| lambda\_name                     | The name of your lambda function                                  | string |    -    |   yes    |

## Outputs

| Name                | Description                                                              |
| ------------------- | ------------------------------------------------------------------------ |
| access\_policy\_arn | Policy ARN for accessing the endpoint. Add this to your user/group/role. |
