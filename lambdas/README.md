# Lambda functions

Each function should have its own Python file in the root of this directory.

## Requirements

* Python 3.7
* pip3

## Accepted Environment Variables

* `URL_MEMBRANE`: Required. The protocol and domain for the Sirius Membrane service. e.g. `https://membrane.prod.internal`
* `DATA_PROVIDER`: Optional. The data provider to use. Can be either `'json'` or `'sirius'`. Default is `'sirius'`.
* `DISABLE_DATA_CACHE`: Optional. If set to `'true'`, data caching will be disabled. Defaults to `'false'`.
* `ENABLE_DEBUG`: Optional. Sets the log level to DEBUG. Defaults to a log level of INFO.
* `CREDENTIALS`: Required if `DATA_PROVIDER` is `'sirius'`. A JSON encoded string of the Membrane credentials. e.g. `'{"email": "publicapi@opgtest.com","password": "Password1"}'`
* `DYNAMODB_DATA_CACHE_TABLE_NAME`: Required if `DISABLE_DATA_CACHE` is false. The name of the DynamoDB table in which to cache responses.
* `DYNAMODB_AUTH_CACHE_TABLE_NAME`: Required if `DATA_PROVIDER` is 'sirius'. The name of the DynamoDB table in which to cache authentication tokens.
* `AWS_ENDPOINT_DYNAMODB`: Optional. For use when testing locally. Set the value to the URL for Localstack's DynamoDB. Defaults to AWS's SDK's defaults.
* `DISABLE_SIRIUS_LOOKUP`: Optional. If set to `'true'`, the Sirius data provider will always return an Upstream Exception. Defaults to `'false'`.

### Packaging for deployment to Lambda

From within `opg-sirius-api-gateway/lambdas`

```bash
pip3 install -r requirements.txt  --target ./vendor
zip -r9 ../lambda.zip .
```

This will install the requirements defined in requirements.txt, into `./lib`

And then it will create `lambda.zip` in the root of the repository. All required modules installed by pip will be included
within the zip file.

### Local development

From within `opg-sirius-api-gateway/lambdas`

```bash
python3 -m virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

To run the unit tests:
```bash
source .venv/bin/activate
pytest
```

### Getting secrets into your Lambda function

Secrets can be kept in AWS Secrets Manager.

Credentials for Sirius, stored in secrets manager can be pushed into a lambda function as the environment variable `CREDENTIALS` when the lambda function is provisioned by Terraform.
