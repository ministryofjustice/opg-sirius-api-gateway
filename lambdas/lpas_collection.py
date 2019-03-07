# Required to provide access to pip installed modules.
from pprint import pprint
from rest_collections import lpas, InvalidInputError, LpasCollection
import traceback
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), './vendor'))


def id_handler(event, context):

    try:
        if 'pathParameters' not in event:
            raise InvalidInputError("'pathParameters' missing from event")

        # -------------------------------------
        # Lookup LPA

        c = LpasCollection.factory()
        result = c.get_lpa(**event['pathParameters'])

        #keep = ['uId', 'onlineLpaId', 'receiptDate', 'registrationDate', 'rejectedDate', 'status']
        #lpa = {k: result['data'][k] for k in keep }

        lpa = result

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
