import includes
from pprint import pprint
from rest_collections import InvalidInputError, LpasCollection
import traceback
import json


def id_handler(event, context):

    try:
        if 'resource' not in event:
            raise InvalidInputError("'resource' missing from event")

        if 'pathParameters' not in event:
            raise InvalidInputError("'pathParameters' missing from event")

        # -------------------------------------
        # Determine what fields the service can return

        fields = []

        if event['resource'].startswith('/lpa-online-tool'):
            fields = ['onlineLpaId', 'receiptDate', 'registrationDate', 'rejectedDate', 'status']

        elif event['resource'].startswith('/use-my-lpa'):
            fields = ['uId']

        # -------------------------------------
        # Lookup LPA

        c = LpasCollection.factory()
        lpa, age = c.get_lpa(**event['pathParameters'])

        # -------------------------------------
        # Respond

        response = {}

        if lpa is None:
            response["statusCode"] = 404
            response["body"] = {}
        else:
            # Filter the return fields
            lpa = {k: lpa[k] for k in fields if k in lpa}

            response["statusCode"] = 200
            response["body"] = lpa
            response["headers"] = {'Age': age}

        # ---

        response["body"] = json.dumps(response["body"])

        return response

    except InvalidInputError as e:
        return {
            'statusCode': 400,
            'body': {
                'error': 'Bad request: %s' % e,
            }
        }

    except Exception as e:
        traceback.print_exc()
        return {
            'statusCode': 500,
            'body': {
                'error': 'An unknown exception occurred',
            }
        }


if __name__ == '__main__':
    response = id_handler({
        'pathParameters': {
            # 'sirius_uid': '700000000001',
            'lpa_online_tool_id': 'A00000000001'
        }
    }, {})
    pprint(response)
