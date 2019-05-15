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

    If this class is used, we assume we want a result to be cached.
    For requests we don't want to be cached, e.g. POSTs, use the data provider directly.
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
    # We use `__getattr__` to catch all method calls to the cache wrapper

    def __getattr__(self, method_name):
        """
        THis catches all function calls to this class, where the function name isn't defined.

        We take the requested function and proxy it on to the real data provider.
        This classes then cached the Response, before passing that Response onto the calling code.
        If the real data provider throws an exception, and this class has a suitable cached response, that is returned.

        This method allows new methods to be added to the data provider without having to
        explicitly define them here.

        :param method_name:
        :return: Response
        """

        # Checks the the request we've caught maps to a method on the data provider
        if not callable(getattr(self._data_provider, method_name, None)):
            raise Exception("Class '%s' has no function '%s'" % (type(self._data_provider), method_name))

        # We return a method which the calling code invokes.
        # This allows the calling code to be identical whether or not it's calling the data
        # provider directly, or via this cache wrapper.
        #
        # args contains a tuple of the arguments passed to the data provider by the calling code.
        def method(*args):

            # We use the first parameter as the cache id.
            # The assumption being that this is a ID, or a query string.
            if isinstance(args, tuple) and len(args) > 0:

                # To limit the complexity of using a magic function call system, we wrap the
                # actual proxying logic within another function. This function is what's passed to
                # `_lookup_with_cache`, which therefore doesn't need any concept of how that function works.
                def f():
                    return getattr(self._data_provider, method_name)(*args)

                return self._lookup_with_cache(args[0], f)

            else:
                raise ValueError('Missing cache_id')

        return method

    # ---------------------------------------------------------------------

    def _lookup_with_cache(self, cache_id, lookup_function):
        """
        Performs the lookup using the passed function `lookup_function`.

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
                if result.response_hash == current_cache_item.response_hash:
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

            if 'payload' in response \
                    and 'response_hash' in response \
                    and 'cached' in response \
                    and 'response_code' in response:

                return Response(
                    ident=cache_id,
                    code=response['response_code'],
                    response_hash=response['response_hash'],
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

            # If we're pushing everything, add the additional fields
            if not meta_data_only:
                logging.debug('Putting item in cache %s', result.ident)
                expression += ', response_code=:code, response_hash=:hash, payload=:payload'

                expression_attribute_values[':code'] = result.code
                expression_attribute_values[':hash'] = result.response_hash
                expression_attribute_values[':payload'] = json.dumps(result.payload)
            else:
                logging.debug('Updating cached item %s', result.ident)

            self.cache_table.update_item(
                Key={'id': result.ident},
                UpdateExpression=expression,
                ExpressionAttributeValues=expression_attribute_values
            )
