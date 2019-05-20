import pytest
from unittest import mock
from HandlerBase import *
from datetime import datetime, timezone
from data_providers import UpstreamExceptionError, UpstreamTimeoutError, \
                InternalExceptionError, SiriusProvider, JsonProvider, Response


class TestHandlerBase(object):

    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'DYNAMODB_AUTH_CACHE_TABLE_NAME': 'tabme-name'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_getting_sirius_data_provider(self):
        """
        We expect Sirius to be the default provider returned.
        """
        provider = HandlerBase.get_data_provider()
        assert isinstance(provider, SiriusProvider)

    @mock.patch.dict('os.environ', {'DATA_PROVIDER': 'json'})
    def test_getting_json_data_provider(self):
        """
        We expect the JSON to be returned.
        """
        provider = HandlerBase.get_data_provider()
        assert isinstance(provider, JsonProvider)

    def test_handle_cannot_be_called_directly(self):
        """
        We expect `handle()` to be overridden.
        """
        handler = HandlerBase()
        with pytest.raises(NotImplementedError):
            handler.handle({}, {})

    def test_logging_level_defaults_to_info(self):
        """
        INFO should be the default log level
        """
        HandlerBase.get_handler()
        assert logging.getLogger().level is logging.INFO

    @mock.patch.dict('os.environ', {'ENABLE_DEBUG': 'true'})
    def test_logging_level_can_be_set_to_debug(self):
        """
        Log level should be set to DEBUG if `ENABLE_DEBUG` is True.
        """
        HandlerBase.get_handler()
        assert logging.getLogger().level is logging.DEBUG

    def test_missing_event_param_resource(self):
        """
        If no event resource is passed, we expect a 400 back.
        """
        response = HandlerBase.get_handler()({}, {})

        assert response == {'statusCode': 400, 'body': json.dumps({
            'error': "Bad request: 'resource' missing from event"
        })}

    def test_missing_event_param_path_parameters(self):
        """
        If a event resource is passed, but no pathParameters, we expect a 400.
        """
        response = HandlerBase.get_handler()({'resource': 'test'}, {})

        assert response == {'statusCode': 400, 'body': json.dumps({
            'error': "Bad request: 'pathParameters' missing from event"
        })}

    def test_handle_returning_something_unexpected(self):
        """
        We expect a ValueError to be raised, resulting in a 500 back.
        """
        # Mock the handle function
        HandlerBase.handle = mock.MagicMock()

        response = HandlerBase.get_handler()({'resource': 'test', 'pathParameters': 'test'}, {})

        assert response == {'statusCode': 500, 'body': json.dumps({
            'error': "An unknown exception occurred"
        })}

    def test_cachting_an_internal_exception(self):
        # Mock the handle function
        mock_handler = mock.MagicMock(side_effect=InternalExceptionError('-message-'))
        HandlerBase.handle = mock_handler

        response = HandlerBase.get_handler()({'resource': 'test', 'pathParameters': 'test'}, {})

        assert response == {'statusCode': 500, 'body': json.dumps({
            'error': "An internal exception occurred. See Gateway logs for details."
        })}

    def test_cachting_an_upstream_exception_exception(self):
        # Mock the handle function
        mock_handler = mock.MagicMock(side_effect=UpstreamExceptionError('-message-'))
        HandlerBase.handle = mock_handler

        response = HandlerBase.get_handler()({'resource': 'test', 'pathParameters': 'test'}, {})

        assert response == {'statusCode': 502, 'body': json.dumps({
            'error': "The upstream data provider returned an exception. See Gateway logs for details."
        })}

    def test_cachting_an_upstream_timeout_exception(self):
        # Mock the handle function
        mock_handler = mock.MagicMock(side_effect=UpstreamTimeoutError('-message-'))
        HandlerBase.handle = mock_handler

        response = HandlerBase.get_handler()({'resource': 'test', 'pathParameters': 'test'}, {})

        assert response == {'statusCode': 504, 'body': json.dumps({
            'error': "The upstream data provider timed out."
        })}

    def test_handle_returning_a_valid_response(self):
        """
        We expect our response object to be returned, with the relevant headers.
        """
        test_datetinme = '2019-05-20T10:00:40.513493+00:00'

        input = Response(
            ident='1',
            code= 200,
            payload={'Test': True},
            generated_datetime=test_datetinme,
            response_hash='xxx'
        )

        # Mock the handle function
        mock_handler = mock.MagicMock()
        mock_handler.return_value = input
        HandlerBase.handle = mock_handler

        response = HandlerBase.get_handler()({'resource': 'test', 'pathParameters': 'test'}, {})

        assert isinstance(response, dict)
        assert 'statusCode' in response and response['statusCode'] is 200
        assert 'body' in response and response['body'] == json.dumps(input.payload)
        assert 'headers' in response and 'Age' in response['headers'] and 'Date' in response['headers']
        assert response['headers']['Date'] == 'Mon, 20 May 2019 10:00:40 GMT'

        # Age will vary so we need to calculator it
        date = datetime.fromisoformat(test_datetinme)
        age = (datetime.utcnow().replace(tzinfo=timezone.utc) - date).seconds

        assert isinstance(response['headers']['Age'], int) and response['headers']['Age'] > 0
        assert age-2 <= response['headers']['Age'] <= age+2     # Allow some wiggle room
