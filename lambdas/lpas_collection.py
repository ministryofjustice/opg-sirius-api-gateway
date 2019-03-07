# Required to provide access to pip installed modules.
from pprint import pprint
from rest_collections import lpas, InvalidInputError
import traceback
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), './vendor'))


def id_handler(event, context):

    try:
        if 'pathParameters' not in event:
            raise InvalidInputError("'pathParameters' missing from event")

        # -------------------------------------
        # Lookup LPA

        lpa = lpas.get_lpa(**event['pathParameters'])
        pprint(lpa)

        # -------------------------------------
        # Respond

        response = {}

        if lpa is None:
            response["statusCode"] = 404
            response["body"] = {}
        else:
            response["statusCode"] = 200
            response["body"] = lpa

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
