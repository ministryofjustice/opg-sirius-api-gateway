from flask import Flask, jsonify, request
import docker
import os
import json

app = Flask(__name__)
dockerClient = docker.from_env()


@app.errorhandler(404)
def page_not_found(e):
    # Map a 404 to a 501, indicating that the requested route isn't implemented.
    # A 404 is reserved for no match on a given ID.
    return 'No such route', 501


@app.route('/v1/lpa-online-tool/lpas/<lpa_online_tool_id>')
def route_lpa_online_tool_lookup(lpa_online_tool_id):
    event = generate_event_payload_lpa_lookup(
        resource='/lpa-online-tool/lpas/{lpa_online_tool_id}',
        path=request.path,
        method=request.method,
        headers=request.headers,
        path_parameters={'lpa_online_tool_id': lpa_online_tool_id}
    )

    return lpa_lookup(event)


@app.route('/v1/use-my-lpa/lpas/<sirius_uid>')
def route_use_my_lpa_lookup(sirius_uid):
    event = generate_event_payload_lpa_lookup(
        resource='/use-my-lpa/lpas/{sirius_uid}',
        path=request.path,
        method=request.method,
        headers=request.headers,
        path_parameters={'sirius_uid': sirius_uid}
    )

    return lpa_lookup(event)


def lpa_lookup(event):
    result = invoke_lambda('lpas_collection.id_handler', event)
    return map_lambda_response(result)


def map_lambda_response(lambda_input):

    # From: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    # {
    #     "isBase64Encoded": true | false,
    #     "statusCode": httpStatusCode,
    #     "headers": {"headerName": "headerValue", ...},
    #     "multiValueHeaders": {"headerName": ["headerValue", "headerValue2", ...], ...},
    #     "body": "..."
    # }

    result = json.loads(lambda_input)

    if 'statusCode' not in result:
        return app.make_response(("'statusCode' missing from lambda response", 500))

    if 'body' not in result:
        return app.make_response(("'body' missing from lambda response", 500))

    if 'isBase64Encoded' in result:
        return app.make_response(("'isBase64Encoded' is present in lambda response, but unsupported in this mock", 500))

    if 'multiValueHeaders' in result:
        return app.make_response(("'multiValueHeaders' is present in lambda response, but unsupported in this mock", 500))

    headers = {}
    if 'headers' in result:
        headers = result['headers']

    # NB: 'body' is returned from Lambda as a JSON encoded strong, with JSON.
    return app.make_response((jsonify(json.loads(result['body'])), result['statusCode'], headers))


def generate_event_payload_lpa_lookup(resource, path, method, headers, path_parameters):

    # From https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    # {
    #    "resource": "Resource path",
    #    "path": "Path parameter",
    #    "httpMethod": "Incoming request's method name"
    #    "headers": {String containing incoming request headers}
    #    "multiValueHeaders": {List of strings containing incoming request headers}
    #    "queryStringParameters": {query string parameters }
    #    "multiValueQueryStringParameters": {List of query string parameters}
    #    "pathParameters":  {path parameters}
    #    "stageVariables": {Applicable stage variables}
    #    "requestContext": {Request context, including authorizer-returned key-value pairs}
    #    "body": "A JSON string of the request payload."
    #    "isBase64Encoded": "A boolean flag to indicate if the applicable request payload is Base64-encode"
    # }

    return {
        'resource': resource,
        'path': path,
        'httpMethod': method,
        'headers': {key: value for key, value in headers},
        'multiValueHeaders': {},
        'queryStringParameters': {},
        'multiValueQueryStringParameters': {},
        'pathParameters': path_parameters,
        'stageVariables': {},
        'requestContext': {},
        'body': '',
        'isBase64Encoded': False,
    }


def invoke_lambda(handler, event):
    lambda_path_on_host = os.environ['LAMBDAS_PATH']

    container = dockerClient.containers.run(
        image="lambci/lambda:python3.7",
        command=[handler, json.dumps(event)],
        volumes={lambda_path_on_host: {'bind': '/var/task', 'mode': 'ro'}},
        stderr=True,
        detach=True,
    )

    # Wait for the container to finish
    container.wait()

    # Send the Lambda's logs to Docker's SDTOUT
    err = container.logs(stdout=False, stderr=True)
    app.logger.info("\n"+err.decode("utf-8"))

    # Return lambda's response
    return container.logs(stdout=True, stderr=False)


# ----------------------------------------------
# Example event from a real API Gateway call

# {
#     "event": {
#         "resource": "/lpa-status",
#         "path": "/lpa-status",
#         "httpMethod": "GET",
#         "headers": null,
#         "multiValueHeaders": null,
#         "queryStringParameters": null,
#         "multiValueQueryStringParameters": null,
#         "pathParameters": null,
#         "stageVariables": null,
#         "requestContext": {
#             "path": "/lpa-status",
#             "accountId": "0000000000",
#             "resourceId": "zlm35c",
#             "stage": "test-invoke-stage",
#             "domainPrefix": "testPrefix",
#             "requestId": "85d933bf-346b-11e9-98df-e3d8bbc598b2",
#             "identity": {
#                 "cognitoIdentityPoolId": null,
#                 "cognitoIdentityId": null,
#                 "apiKey": "test-invoke-api-key",
#                 "cognitoAuthenticationType": null,
#                 "userArn": "arn:aws:iam::0000000000:root",
#                 "apiKeyId": "test-invoke-api-key-id",
#                 "userAgent": "aws-internal/3 aws-sdk-java/1.11.481 Linux/4.9.137-0.1.ac.218.74.329.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.192-b12 java/1.8.0_192",
#                 "accountId": "0000000000",
#                 "caller": "0000000000",
#                 "sourceIp": "test-invoke-source-ip",
#                 "accessKey": "XXXX",
#                 "cognitoAuthenticationProvider": null,
#                 "user": "0000000000"
#             },
#             "domainName": "testPrefix.testDomainName",
#             "resourcePath": "/lpa-status",
#             "httpMethod": "GET",
#             "extendedRequestId": "VW5c3FXmjoEFY9A=",
#             "apiId": "ddm5i7lhe7"
#         },
#         "body": null,
#         "isBase64Encoded": false
#     }
# }
