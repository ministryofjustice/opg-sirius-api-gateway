#!/bin/sh

echo "Pulling LambCI lambda container... "
docker pull lambci/lambda:python3.7
echo "LambCI lambda container is ready."

echo "Ensuring the Lambda has its dependencies"
pip3 install -r /srv/lambdas/requirements.txt  --target /srv/lambdas/vendor

echo "Starting Mock API Gateway"
python -m flask run --host=0.0.0.0
