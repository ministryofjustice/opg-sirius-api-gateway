import os
import boto3
import json
import math
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dateutil.relativedelta import relativedelta
from data_providers import Response, UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError


class CacheProviderWrapper:
    """
    Wraps around a data provider, providing a caching layer.

    *A cached result is only returned if the upstream provided return an error.*

    The original version of this class used `def __getattr__(self, name)` as opposed to explicitly
    defining all of the methods on a data provider. The end result however seemed overaly 'magic', with
    no simply way to control if/when/how different methods on the provider would use the cache.

    """

    # TTL used for DynamoDB
    # Note DynamoDB doesn't guarantee it'll be deleted exactly as the TTL expires; just soon after.
    CACHE_TTL = relativedelta(hours=48)

    def __init__(self, data_provider):
        self._data_provider = data_provider

        if 'AWS_ENDPOINT_DYNAMODB' in os.environ:
            # For local development
            dynamodb_endpoint_url = os.environ['AWS_ENDPOINT_DYNAMODB']
            logging.debug('AWS_ENDPOINT_DYNAMODB set %s' % dynamodb_endpoint_url)
        else:
            # Should be none in AWS
            dynamodb_endpoint_url = None

        if 'DYNAMODB_DATA_CACHE_TABLE_NAME' in os.environ:
            dynamodb_cache_table = os.environ['DYNAMODB_DATA_CACHE_TABLE_NAME']
        else:
            raise RuntimeError('DYNAMODB_DATA_CACHE_TABLE_NAME not set')

        dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodb_endpoint_url)
        self.cache_table = dynamodb.Table(dynamodb_cache_table)  # Is lazy

    # ---------------------------------------------------------------------
    # Concrete methods that map to those in the upstream providers
    #   If a method's result should never be cached, don't route it via _lookup_with_cache()

    def get_lpa_by_sirius_uid(self, sirius_uid):
        def f():    # Map to the real method
            return self._data_provider.get_lpa_by_sirius_uid(sirius_uid)
        return self._lookup_with_cache(sirius_uid, f)

    def get_lpa_by_lpa_online_tool_id(self, online_tool_id):
        def f():    # Map to the real method
            return self._data_provider.get_lpa_by_lpa_online_tool_id(online_tool_id)
        return self._lookup_with_cache(online_tool_id, f)

    # ---------------------------------------------------------------------

    def _lookup_with_cache(self, cache_id, lookup_function):
        """
        Performs the lookup using teh passed function `lookup_function`.

        If an exception is thrown upstream that matches one of those
        allowed, we will return a cached result, if we have one.

        Every successful result returned from the upstream provider will be put into the cache.

        :param cache_id: A string that uniquely represents the lookup being performed.
        :param lookup_function: The function that performs the 'real' lookup
        :return: Response or None
        """

        thread_pool = ThreadPoolExecutor(1)

        # Perform the DynamoDB lookup in a thread
        current_cache_item_task = thread_pool.submit(self._lookup_in_cache, cache_id)

        # -----------------------------------------------
        # Perform the lookup against the real provider

        result = None

        # Returned if something completely unknown happens.
        exception = ValueError('Unable to perform the request, or get it from the cache, or catch a know exception')

        try:
            # Pass the request to the actual data provider
            result = lookup_function()

        # Catch the following and allow a cached version
        except UpstreamTimeoutError as e:
            exception = e
        except UpstreamExceptionError as e:
            exception = e
        except InternalExceptionError as e:
            exception = e

        # Pull the result out of the thread
        current_cache_item = current_cache_item_task.result()

        # If something went wrong...
        if result is None:
            if isinstance(current_cache_item, Response):
                # If we have a cached version
                logging.warning('Error processing request; returning item from cache: %s', current_cache_item.ident)
                return current_cache_item

            else:
                # Else re-raise the exception
                raise exception

        # -----------------------------------------------
        # Handle the response

        # If we got a Response back from the request
        if isinstance(result, Response):

            meta_data_only = False

            # If we also got a Response from the cache
            if isinstance(current_cache_item, Response):
                logging.debug('%s found in cache', cache_id)

                # And the hashes match
                if result.payload_hash == current_cache_item.payload_hash:
                    # Then we only need to update the meta-data
                    meta_data_only = True

            # Cache the result
            self._cache_result(result, meta_data_only=meta_data_only)

        return result

    def _lookup_in_cache(self, cache_id):
        """
        Looks up the given `cache_id` in DynamoDB

        :return: Response
        """
        response = self.cache_table.get_item(
            Key={'id': cache_id}
        )

        if 'Item' in response:
            response = response['Item']

            if 'payload' in response and 'payload_hash' in response and 'cached' in response:
                return Response(
                    ident=cache_id,
                    payload_hash=response['payload_hash'],
                    generated_datetime=response['cached'],
                    payload=json.loads(response['payload']),
                )

    def _cache_result(self, result, meta_data_only):
        """
        Stores the passed `Response` object in DynamoDB

        :param result: The Response object to be cached
        :param meta_data_only: True iff only the meta data needs updating. Otherwise the whole Response is stored
        """
        if isinstance(result, Response):

            # When should DynamoDB expire the item
            expires = datetime.now() + self.CACHE_TTL

            expression = 'SET cached=:datatime, expires=:expires'
            expression_attribute_values = {
                ':datatime': result.generated_datetime,
                ':expires': math.floor(expires.timestamp()),
            }

            # If we're pushing everything, add teh additional fields
            if not meta_data_only:
                logging.debug('Putting item in cache %s', result.ident)
                expression += ', payload_hash=:hash, payload=:payload'

                expression_attribute_values[':hash'] = result.payload_hash
                expression_attribute_values[':payload'] = json.dumps(result.payload)
            else:
                logging.debug('Updating cached item %s', result.ident)

            self.cache_table.update_item(
                Key={'id': result.ident},
                UpdateExpression=expression,
                ExpressionAttributeValues=expression_attribute_values
            )
