# Lambda functions

Each function should have its own Python file in the root of this directory.

## Requirements

* Python 3.7
* pip3

### Installing dependencies

From within `opg-sirius-api-gateway/lambdas`

```bash
pip3 install -r requirements.txt  --target ./vendor
```

This will install the requirements defined in requirements.txt, into `./lib`

### Compressing files for upload to AWS

From within `opg-sirius-api-gateway/lambdas`

```bash
zip -r9 ../lambda.zip .
```

This will create `lambda.zip` in the root of the repository. All required modules installed by pip will be included
within the zip file.
