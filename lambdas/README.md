# Lambda functions

Each function should have its own Python file in the root of this directory.

## Requirements

* Python 3.7
* pip3

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
