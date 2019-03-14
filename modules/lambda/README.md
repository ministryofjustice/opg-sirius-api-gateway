# Lambdas for OPG API Gateway

This module provisions 
* An single VPC based lambda
* The lambda's execution policy and role


## Inputs

| Name                       | Description                                                       |  Type  | Default | Required |
| -------------------------- | ----------------------------------------------------------------- | :----: | :-----: | :------: |
| environment                | Environment configuration for the Lambda function                 |  map   | `<map>` |    no    |
| lambda\_function\_filename | Relative path to file with lambda source code                     | string |    -    |   yes    |
| lambda\_handler            | The function entrypoint in your code.                             | string |    -    |   yes    |
| lambda\_name               | Name for the lambda function and role policies that accompany it. | string |    -    |   yes    |
| security\_group\_ids       | List of security group IDs for lambda function vpc_config         |  list  |    -    |   yes    |
| tags                       | A mapping of tags                                                 |  map   | `<map>` |    no    |
| vpc                        | Name of vpc to target                                             | string |    -    |   yes    |

## Outputs

| Name         | Description                              |
| ------------ | ---------------------------------------- |
| lambda\_arn  | The ARN for your lambda function         |
| lambda\_name | The unique name for your lambda function |
