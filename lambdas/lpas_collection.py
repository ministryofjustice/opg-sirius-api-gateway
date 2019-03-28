import includes
from pprint import pprint
from rest_collections import InvalidInputError, LpasCollection
from data_providers import UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError
import traceback
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        logger.error('InvalidInputError: %s' % e)
        return {'statusCode': 400, 'body': {
            'error': 'Bad request: %s' % e
        }}

    except InternalExceptionError as e:
        logger.error('InternalExceptionError: %s' % e)
        return {'statusCode': 500, 'body': {
            'error': 'An internal exception occurred. See Gateway logs for details.'
        }}

    except UpstreamExceptionError as e:
        logger.error('UpstreamExceptionError: %s' % e)
        return {'statusCode': 502, 'body': {
            'error': 'The upstream data provider returned an exception. See Gateway logs for details.'
        }}

    except UpstreamTimeoutError:
        logger.warning('UpstreamTimeoutError')
        return {'statusCode': 504, 'body': {
            'error': 'The upstream data provider timed out'
        }}

    except Exception as e:
        traceback.print_exc()
        return {'statusCode': 500, 'body': {
            'error': 'An unknown exception occurred'
        }}


if __name__ == '__main__':
    response = id_handler({
        'pathParameters': {
            # 'sirius_uid': '700000000001',
            'lpa_online_tool_id': 'A00000000001'
        },
        'resource': '/lpa-online-tool',
    }, {})
    pprint(response)
