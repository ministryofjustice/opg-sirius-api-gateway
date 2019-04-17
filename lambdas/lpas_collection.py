import includes
from pprint import pprint
from rest_collections import InvalidInputError, LpasCollection
from data_providers import UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError
import traceback
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def id_handler(event, context):

    try:
        if 'resource' not in event:
            raise InvalidInputError("'resource' missing from event")

        if 'pathParameters' not in event:
            raise InvalidInputError("'pathParameters' missing from event")

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
            # -------------------------------------
            # Determine if / what fields the service can return

            fields = []

            if event['resource'].startswith('/lpa-online-tool'):
                fields = ['onlineLpaId', 'receiptDate', 'registrationDate', 'rejectedDate', 'status']

            # TODO: Determine if we want to filter /use-an-lpa at all
            # elif event['resource'].startswith('/use-an-lpa'):
            #    fields = ['uId']

            # Filter the return fields
            if len(fields) > 0:
                lpa = {k: lpa[k] for k in fields if k in lpa}

            response["statusCode"] = 200
            response["body"] = lpa
            response["headers"] = {'Age': age}

        # ---

        response["body"] = json.dumps(response["body"])

        return response

    except InvalidInputError as e:
        logging.error('InvalidInputError: %s' % e)
        return {'statusCode': 400, 'body': {
            'error': 'Bad request: %s' % e
        }}

    except InternalExceptionError as e:
        logging.error('InternalExceptionError: %s' % e)
        return {'statusCode': 500, 'body': {
            'error': 'An internal exception occurred. See Gateway logs for details.'
        }}

    except UpstreamExceptionError as e:
        logging.error('UpstreamExceptionError: %s' % e)
        return {'statusCode': 502, 'body': {
            'error': 'The upstream data provider returned an exception. See Gateway logs for details.'
        }}

    except UpstreamTimeoutError:
        logging.warning('UpstreamTimeoutError')
        return {'statusCode': 504, 'body': {
            'error': 'The upstream data provider timed out'
        }}

    except Exception:
        traceback.print_exc()
        return {'statusCode': 500, 'body': {
            'error': 'An unknown exception occurred'
        }}
