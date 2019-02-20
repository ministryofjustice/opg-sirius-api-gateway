#!/bin/sh

echo "Pulling LambCI lambda container... "
docker pull lambci/lambda:python3.7
echo "LambCI lambda container is ready."

echo "Starting Mock API Gateway"
python -m flask run --host=0.0.0.0
