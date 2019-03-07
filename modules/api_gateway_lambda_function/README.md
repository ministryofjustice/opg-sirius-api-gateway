# API Gateway REST API Lambda Function

This module creates Lambda functions from source, and attaches them to an existing API Gateway REST API


## Inputs

| Name                                | Description                                                                                                                                                                                                     |  Type  |   Default   | Required |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----: | :---------: | :------: |
| account\_id                         | AWS account number                                                                                                                                                                                              | string |      -      |   yes    |
| api\_gateway                        | API gateway REST API to attach lambda functions to                                                                                                                                                              | string |      -      |   yes    |
| api\_gateway\_cloudwatch\_role\_arn | The ARN of an IAM role for CloudWatch (to allow logging & monitoring).                                                                                                                                          | string |      -      |   yes    |
| api\_gateway\_deployment\_stage     | The name of the deployment stage. If the specified stage already exists, it will be updated to point to the new deployment. If the stage does not exist, a new one will be created and point to this deployment | string |      -      |   yes    |
| environment                         | Environment configuration for the Lambda function                                                                                                                                                               |  map   |   `<map>`   |    no    |
| lambda\_function\_filename          | Relative path to file with lambda source code                                                                                                                                                                   | string |      -      |   yes    |
| lambda\_handler                     | The function entrypoint in your code.                                                                                                                                                                           | string |  `handler`  |    no    |
| lambda\_name                        | Name for the lambda function and role policies that accompany it.                                                                                                                                               | string |      -      |   yes    |
| lambda\_runtime                     | Language used for the lambda function                                                                                                                                                                           | string | `python3.7` |    no    |
| logging\_level                      | Specifies the logging level for this method, which effects the log entries pushed to Amazon CloudWatch Logs. The available levels are OFF, ERROR, and INFO                                                      | string |   `INFO`    |    no    |
| permitted\_consumer\_roles          | Cross account IAM roles that are permitted to use the API resource, in ARN format                                                                                                                               |  list  |  `<list>`   |    no    |
| security\_group\_ids                | List of security group IDs for lambda function vpc_config                                                                                                                                                       |  list  |      -      |   yes    |
| tags                                | A mapping of tags                                                                                                                                                                                               |  map   |   `<map>`   |    no    |
| vpc                                 | Name of vpc to target                                                                                                                                                                                           | string |      -      |   yes    |

## Outputs

| Name                | Description                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------- |
| lambda\_invoke\_url | The URL to invoke the API pointing to the stage, e.g. https://z4675bid1j.execute-api.eu-west-2.amazonaws.com/prod |
| lambda\_name        | The unique name for your Lambda Function                                                                          |
