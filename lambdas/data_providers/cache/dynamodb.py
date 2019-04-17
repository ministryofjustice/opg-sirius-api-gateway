import os
import boto3
import json
import math
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from data_providers import Response, UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError


class CacheProviderWrapper:

    def __init__(self, data_provider):
        self._data_provider = data_provider

        if 'AWS_ENDPOINT_DYNAMODB' in os.environ:
            # For local development
            dynamodb_endpoint_url = os.environ['AWS_ENDPOINT_DYNAMODB']
            logging.debug('AWS_ENDPOINT_DYNAMODB set %s' % self._dynamodb_endpoint_url)
        else:
            # Should be none in AWS
            dynamodb_endpoint_url = None

        if 'DYNAMODB_DATA_CACHE_TABLE_NAME' in os.environ:
            dynamodb_cache_table = os.environ['DYNAMODB_DATA_CACHE_TABLE_NAME']
        else:
            raise RuntimeError('DYNAMODB_DATA_CACHE_TABLE_NAME not set')

        dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodb_endpoint_url)
        self.cache_table = dynamodb.Table(dynamodb_cache_table)  # Is lazy

    def __getattr__(self, name):
        """
        Proxies the request on to the real data provider.
        """
        def method(*args):

            if isinstance(args, tuple) and len(args) > 0:
                # args[0] is the string that represents the item being looked up
                current_cache_item = self._lookup_in_cache(args[0])
            else:
                raise ValueError('Missing ident passed to caching wrapper')

            # -----------------------------------------------
            # Perform the lookup against the real provider

            result = None

            try:
                # Pass the request to the actual data provider
                result = getattr(self._data_provider, name)(*args)

            # Catch the following and allow a cached version
            except UpstreamTimeoutError:
                pass
            except UpstreamExceptionError:
                pass
            except InternalExceptionError:
                pass

            # If something went wrong, and we have a cached version, return that
            if result is None and isinstance(current_cache_item, Response):
                logging.info('Error processing request; returning item from cache: %s', current_cache_item)
                return current_cache_item

            # -----------------------------------------------
            # Handle the response

            # If we got a Response back from the request
            if isinstance(result, Response):

                meta_data_only = False

                # If we also got a Response from the cache
                if isinstance(current_cache_item, Response):
                    logging.debug('%s found in cache', args[0])

                    # And the hashes match
                    if result.meta_hash == current_cache_item.meta_hash:
                        # Then we only need to update the meta-data
                        meta_data_only = True

                self._cache_result(result, meta_data_only=meta_data_only)

            return result

        return method

    def _lookup_in_cache(self, cache_id):
        response = self.cache_table.get_item(
            Key={'id': cache_id}
        )

        if 'Item' in response:
            response = response['Item']

            if 'payload' in response and 'meta_hash' in response and 'cached' in response:
                return Response(
                    ident=cache_id,
                    meta_hash=response['meta_hash'],
                    meta_datetime=response['cached'],
                    payload=json.loads(response['payload']),
                )

    def _cache_result(self, result, meta_data_only):
        if isinstance(result, Response):

            # When should DynamoDB expire the item
            expires = datetime.today() + relativedelta(months=1)

            expression = 'SET cached=:datatime, expires=:expires'
            expression_attribute_values = {
                ':datatime': result.meta_datetime,
                ':expires': math.floor(expires.timestamp()),
            }

            # If we're pushing everything, add teh additional fields
            if not meta_data_only:
                logging.debug('Putting item in cache %s', result.ident)
                expression += ', meta_hash=:hash, payload=:payload'

                expression_attribute_values[':hash'] = result.meta_hash
                expression_attribute_values[':payload'] = json.dumps(result.payload)
            else:
                logging.debug('Updating cached item %s', result.ident)

            self.cache_table.update_item(
                Key={'id': result.ident},
                UpdateExpression=expression,
                ExpressionAttributeValues=expression_attribute_values
            )
