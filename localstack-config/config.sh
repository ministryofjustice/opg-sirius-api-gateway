#!/bin/sh

endpoint=${AWS_ENDPOINT_DYNAMODB:-"gateway-localstack:14569"}

#
#  Setup DynamoDB
#
/usr/local/bin/waitforit -address=tcp://$endpoint -timeout 60 -retry 6000 -debug

if [ $? -ne 0 ]; then
    echo "DynamoDB failed to start"
else
    aws dynamodb create-table \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --table-name opg-gateway-cache-auth \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=10 \
    --region eu-west-1 \
    --endpoint http://$endpoint

    aws dynamodb create-table \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --table-name opg-gateway-cache-data \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=10,WriteCapacityUnits=10 \
    --region eu-west-1 \
    --endpoint http://$endpoint

    aws dynamodb update-time-to-live \
    --table-name opg-gateway-cache-data \
    --time-to-live-specification "Enabled=true, AttributeName=expires" \
    --region eu-west-1 \
    --endpoint http://$endpoint
fi
