import os
import json
import logging
import traceback
from rest_collections import InvalidInputError
from data_providers import UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError


class HandlerBase(object):
    """
    Base class for implementing Lambda handlers as classes.
    Used across multiple Lambda functions (included in each zip file).
    Add additional features here common to all your Lambdas, like logging.
    """

    @classmethod
    def get_handler(cls, *args, **kwargs):

        # -------------------------------
        # Setup

        logger = logging.getLogger()

        if 'ENABLE_DEBUG' in os.environ and os.environ['ENABLE_DEBUG'] == 'true':
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        # -------------------------------

        def handler(event, context):
            try:
                return cls(*args, **kwargs).handle(event, context)
            except InvalidInputError as e:
                logging.error('InvalidInputError: %s' % e)
                return {'statusCode': 400, 'body': json.dumps({
                    'error': 'Bad request: %s' % e
                })}

            except InternalExceptionError as e:
                logging.error('InternalExceptionError: %s' % e)
                return {'statusCode': 500, 'body': json.dumps({
                    'error': 'An internal exception occurred. See Gateway logs for details.'
                })}

            except UpstreamExceptionError as e:
                logging.error('UpstreamExceptionError: %s' % e)
                return {'statusCode': 502, 'body': json.dumps({
                    'error': 'The upstream data provider returned an exception. See Gateway logs for details.'
                })}

            except UpstreamTimeoutError:
                logging.warning('UpstreamTimeoutError')
                return {'statusCode': 504, 'body': json.dumps({
                    'error': 'The upstream data provider timed out'
                })}

            except Exception:
                traceback.print_exc()
                return {'statusCode': 500, 'body': json.dumps({
                    'error': 'An unknown exception occurred'
                })}

        return handler

    def handle(self, event, context):
        raise NotImplementedError
