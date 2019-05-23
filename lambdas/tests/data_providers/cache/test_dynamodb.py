import json
import math
import pytest
import datetime
from unittest import mock
from data_providers.cache import CacheProviderWrapper
from data_providers import Response, UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError


class TestCacheProviderWrapper(object):

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_get_lpa_by_lpa_online_tool_id_is_proxied_no_cache(self, mock_boto3):

        test_id = 'A54236784213'

        mock_sirius_provider = mock.MagicMock()

        test_response = Response.factory(
            ident='700098765432',
            code=200,
            payload_json=json.dumps({'Testing': 'One'})
        )

        mock_sirius_provider.get_lpa_by_lpa_online_tool_id.return_value = test_response

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        result = wrapper.get_lpa_by_lpa_online_tool_id(test_id)

        assert isinstance(result, Response)
        assert result is test_response

        # Check the request was passed on to the real data provider
        mock_sirius_provider.get_lpa_by_lpa_online_tool_id.assert_called_once_with(test_id)

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_get_lpa_by_sirius_uid_is_proxied_no_cache(self, mock_boto3):

        test_id = '700012348745'

        mock_sirius_provider = mock.MagicMock()

        test_response = Response.factory(
            ident='700098765432',
            code=200,
            payload_json=json.dumps({'Testing': 'One'})
        )

        mock_sirius_provider.get_lpa_by_sirius_uid.return_value = test_response

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        result = wrapper.get_lpa_by_sirius_uid(test_id)

        assert isinstance(result, Response)
        assert result is test_response

        # Check the request was passed on to the real data provider
        mock_sirius_provider.get_lpa_by_sirius_uid.assert_called_once_with(test_id)

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_failing_data_provider_successful_cache_lookup(self, mock_boto3):

        mock_sirius_provider = mock.MagicMock()

        # The real data provider returning none will result in the cached version returned
        mock_sirius_provider.get_lpa_by_sirius_uid.return_value = None

        # ---

        test_id = '700012348745'
        payload = {'Testing': True}
        response_hash = 'xxx'
        cached = '2019-04-17T20:08:50.349878+00:00'
        code = 200

        mock_boto3.resource.return_value.Table.return_value.get_item.return_value = {
            'Item': {
                'payload': json.dumps(payload),
                'response_hash': response_hash,
                'cached': cached,
                'response_code': code,
            }
        }

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        result = wrapper.get_lpa_by_sirius_uid(test_id)

        # We should see the response that the cache returned
        assert isinstance(result, Response)
        assert result.ident == test_id
        assert result.payload == payload
        assert result.response_hash == response_hash
        assert result.generated_datetime == cached
        assert result.code == code

        # This should still have been called
        mock_sirius_provider.get_lpa_by_sirius_uid.assert_called_once_with(test_id)

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_failing_data_provider_and_unsuccessful_cache_lookup(self, mock_boto3):
        """
        If neither the data provider of the cache can return a result, and exception is thrown.

        Note: Even if an LPA is not found, the data provider should still return a valid result.
                It returning anything other than a `Response` is an exception.
        """

        mock_sirius_provider = mock.MagicMock()

        # The real data provider returning none will result in the cached version returned
        mock_sirius_provider.get_lpa_by_sirius_uid.return_value = None

        # And the cache will also return no result
        mock_boto3.resource.return_value.Table.return_value.get_item.return_value = {}

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        # No result from the data provider, and nothing in the cache, throws an error exception.
        with pytest.raises(ValueError):
            wrapper.get_lpa_by_sirius_uid('700012348745')

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_successful_cache_and_provider_lookup(self, mock_boto3):

        mock_sirius_provider = mock.MagicMock()

        test_response = Response.factory(
            ident='700098765432',
            code=200,
            payload_json=json.dumps({'Testing': 'One'})
        )

        # The real provider will return a response. We should see this returned, not the cached version.
        mock_sirius_provider.get_lpa_by_sirius_uid.return_value = test_response

        # ---

        test_id = '700012348745'
        payload = {'Testing': 'Two'}
        response_hash = 'xxx'
        cached = '2019-04-17T20:08:50.349878+00:00'

        mock_boto3.resource.return_value.Table.return_value.get_item.return_value = {
            'Item': {
                'payload': json.dumps(payload),
                'response_hash': response_hash,
                'cached': cached,
            }
        }

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        result = wrapper.get_lpa_by_sirius_uid(test_id)

        # We should see the response that the cache returned
        assert isinstance(result, Response)

        # Response should match the one from the real data provider
        assert result.ident == test_response.ident
        assert result.payload == test_response.payload
        assert result.response_hash == test_response.response_hash
        assert result.generated_datetime == test_response.generated_datetime

        # And not the one from the cache
        assert not result.ident == test_id
        assert not result.payload == payload
        assert not result.response_hash == response_hash
        assert not result.generated_datetime == cached

        # These should have been called
        mock_boto3.resource.return_value.Table.return_value.get_item.assert_called_once()
        mock_sirius_provider.get_lpa_by_sirius_uid.assert_called_once_with(test_id)

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_data_provider_exception_upstream_timeout_error(self, mock_boto3):

        mock_sirius_provider = mock.MagicMock()
        mock_sirius_provider.get_lpa_by_lpa_online_tool_id.side_effect = UpstreamTimeoutError()

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        with pytest.raises(UpstreamTimeoutError):
            wrapper.get_lpa_by_lpa_online_tool_id('A54236784213')

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_data_provider_exception_upstream_exception_error(self, mock_boto3):

        mock_sirius_provider = mock.MagicMock()
        mock_sirius_provider.get_lpa_by_lpa_online_tool_id.side_effect = UpstreamExceptionError()

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        with pytest.raises(UpstreamExceptionError):
            wrapper.get_lpa_by_lpa_online_tool_id('A54236784213')

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_data_provider_exception_internal_exception_error(self, mock_boto3):

        mock_sirius_provider = mock.MagicMock()
        mock_sirius_provider.get_lpa_by_lpa_online_tool_id.side_effect = InternalExceptionError()

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        with pytest.raises(InternalExceptionError):
            wrapper.get_lpa_by_lpa_online_tool_id('A54236784213')

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch('data_providers.cache.dynamodb.datetime', autospec=True, wraps=datetime)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_adding_new_cache_item(self, mock_datetime, mock_boto3):
        """
        If an item isn't already in the cache, the whole response should be inserted.
        """

        # This is used to determine the expiry timestamp DynamoDB should expect.
        zeroed_timestamp = datetime.datetime.fromtimestamp(0)   # Set now().timestamp() to 0
        mock_datetime.now.return_value = zeroed_timestamp

        # ---

        mock_sirius_provider = mock.MagicMock()

        test_response = Response.factory(
            ident='700098765432',
            code=200,
            payload_json=json.dumps({'Testing': 'One'})
        )

        mock_sirius_provider.get_lpa_by_lpa_online_tool_id.return_value = test_response

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        result = wrapper.get_lpa_by_lpa_online_tool_id(test_response.ident)

        assert isinstance(result, Response)

        # ---

        # Expect all fields.
        expression_attribute_values = {
            ':datatime': test_response.generated_datetime,
            ':expires': math.floor((zeroed_timestamp + CacheProviderWrapper.CACHE_TTL).timestamp()),
            ':code': 200,
            ':hash': test_response.response_hash,
            ':payload': json.dumps(test_response.payload),
        }

        mock_boto3.resource.return_value.Table.return_value.update_item.assert_called_once_with(
            Key={'id': test_response.ident},
            UpdateExpression='SET cached=:datatime, expires=:expires, response_code=:code, response_hash=:hash, payload=:payload',
            ExpressionAttributeValues=expression_attribute_values
        )

    @mock.patch('data_providers.cache.dynamodb.boto3', autospec=True)
    @mock.patch('data_providers.cache.dynamodb.datetime', autospec=True, wraps=datetime)
    @mock.patch.dict('os.environ', {'DYNAMODB_DATA_CACHE_TABLE_NAME': 'dynamodb-table'})
    def test_updating_existing_cache_item(self, mock_datetime, mock_boto3):
        """
        If an item is already in the cache, only metadata will be updated. i.e. not the payload.
        """

        # This is used to determine the expiry timestamp DynamoDB should expect.
        zeroed_timestamp = datetime.datetime.fromtimestamp(0)   # Set now().timestamp() to 0
        mock_datetime.now.return_value = zeroed_timestamp

        # ---

        # Response the data provider will return

        test_response = Response.factory(
            ident='700098765432',
            code=200,
            payload_json=json.dumps({'Testing': 'One'})
        )

        mock_sirius_provider = mock.MagicMock()
        mock_sirius_provider.get_lpa_by_lpa_online_tool_id.return_value = test_response

        # ---

        # Cache response. If the new hash matches, it'll be considered an update.

        mock_boto3.resource.return_value.Table.return_value.get_item.return_value = {
            'Item': {
                'payload': json.dumps({'Testing': 'Two'}),
                'response_hash': test_response.response_hash,         # Note we ensure the hashes match
                'cached': '2019-04-17T20:08:50.349878+00:00',
                'response_code': 200,
            }
        }

        # ---

        wrapper = CacheProviderWrapper(mock_sirius_provider)

        result = wrapper.get_lpa_by_lpa_online_tool_id(test_response.ident)

        assert isinstance(result, Response)

        # ---

        # Expect only metadata fields.
        expression_attribute_values = {
            ':datatime': test_response.generated_datetime,
            ':expires': math.floor((zeroed_timestamp + CacheProviderWrapper.CACHE_TTL).timestamp()),
        }

        mock_boto3.resource.return_value.Table.return_value.update_item.assert_called_once_with(
            Key={'id': test_response.ident},
            UpdateExpression='SET cached=:datatime, expires=:expires',
            ExpressionAttributeValues=expression_attribute_values
        )
