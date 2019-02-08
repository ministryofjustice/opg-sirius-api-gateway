No state storage for this repository yet
Split up modules/api_gateway_lambda_function/main.tf into smaller files
Use lookup patter for account numbers everywhere `${lookup(local.accounts, "opg-sirius-development")`
Tag all resources
