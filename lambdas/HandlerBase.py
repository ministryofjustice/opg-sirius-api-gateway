import os
import json
import logging
import traceback
from datetime import datetime, timezone
from wsgiref.handlers import format_date_time
from data_providers import UpstreamExceptionError, UpstreamTimeoutError, \
                InternalExceptionError, SiriusProvider, JsonProvider, Response
from data_providers.cache import CacheProviderWrapper


class InvalidInputError(Exception):
    pass


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
                # Sense check we have the expected inputs
                if 'resource' not in event:
                    raise InvalidInputError("'resource' missing from event")

                if 'pathParameters' not in event:
                    raise InvalidInputError("'pathParameters' missing from event")

                # Calls `handle(event, context)` on the instance
                response = cls(*args, **kwargs).handle(event, context)

                # Ensure we get the expected Response object
                if not isinstance(response, Response):
                    raise ValueError

                # Calculate the Age header.
                date = datetime.fromisoformat(response.generated_datetime)
                age = (datetime.utcnow().replace(tzinfo=timezone.utc) - date).seconds

                # Map the response into what the API Gateway expects.
                return {
                    'statusCode': response.code,
                    'body': json.dumps(response.payload),
                    'headers': {
                        'Age': age,
                        'Date': format_date_time(date.timestamp()),
                    },
                }

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
                    'error': 'The upstream data provider timed out.'
                })}

            except Exception:
                traceback.print_exc()
                return {'statusCode': 500, 'body': json.dumps({
                    'error': 'An unknown exception occurred'
                })}

        return handler

    def handle(self, event, context):
        raise NotImplementedError

    @classmethod
    def get_data_provider(cls):
        if 'DATA_PROVIDER' in os.environ and os.environ['DATA_PROVIDER'] == 'json':
            return JsonProvider.factory()
        else:
            return SiriusProvider.factory()

    @classmethod
    def get_data_provider_with_cache(cls):
        if 'DISABLE_DATA_CACHE' in os.environ:
            logging.warning('Data caching is disabled; returning data provider without cache')
            return cls.get_data_provider()
        else:
            return CacheProviderWrapper(cls.get_data_provider())
