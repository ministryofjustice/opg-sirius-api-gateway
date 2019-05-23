import os
import json
import responses
import pytest
from data_providers import SiriusProvider, Response, UpstreamExceptionError
from unittest import mock


class TestSiriusProvider(object):

    @mock.patch('data_providers.authentication.SiriusAuthenticator', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_get_lpa_by_lpa_online_tool_id_with_first_time_valid_token(self, mock_authenticator):

        """
        Success Route. Looks up an LPA. Results in a 200 first time.
        We get back the expected result. The first requested token from the authenticator worked.
        """

        with responses.RequestsMock() as rsps:

            ident = 'A00000000001'

            # For the data lookup
            rsps.add(
                rsps.GET, os.environ['URL_MEMBRANE'] + '/api/public/v1/lpas?lpa-online-tool-id=%s' % ident,
                status=200, json=[]
            )

            # ---
            # Mock the authenticator

            def authorise_request_response(req, accept_cached_token):
                return req, False

            mock_authenticator.authorise_request = mock.MagicMock(side_effect=authorise_request_response)

            # ---

            p = SiriusProvider(mock_authenticator, os.environ['URL_MEMBRANE'])

            result = p.get_lpa_by_lpa_online_tool_id(ident)

            assert isinstance(result, Response)
            assert result.is_empty()
            mock_authenticator.authorise_request.assert_called_once()

    @mock.patch('data_providers.authentication.SiriusAuthenticator', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_get_lpa_by_lpa_online_tool_id_with_second_time_valid_token(self, mock_authenticator):

        """
        Success Route, but with the token needing refreshed.
        Results in a 200 on the second attempt, a 401 on the first.
        We get back the expected result. The *second* requested token from the authenticator worked.
        """

        with responses.RequestsMock() as rsps:

            ident = 'A00000000001'

            # ---

            # First we're going to return a 401
            # Then next a 200
            lookup_http_response_response_order = [401, 200]

            def lookup_http_response(request):
                return lookup_http_response_response_order.pop(0), {}, json.dumps({})

            rsps.add_callback(
                rsps.GET, os.environ['URL_MEMBRANE'] + '/api/public/v1/lpas?lpa-online-tool-id=%s' % ident,
                callback=lookup_http_response, content_type='application/json',
            )

            # ---

            # First we're going to say the token came from the cache
            # Then on the next call, that it didn't
            authorise_request_response_order = [True, False]

            def authorise_request_response(req, accept_cached_token):
                expected = authorise_request_response_order.pop(0)

                # Confirms that first we accept a token. Then on the second attempt we don't.
                assert accept_cached_token == expected
                return req, expected

            mock_authenticator.authorise_request = mock.MagicMock(side_effect=authorise_request_response)

            # ---

            p = SiriusProvider(mock_authenticator, os.environ['URL_MEMBRANE'])

            result = p.get_lpa_by_lpa_online_tool_id(ident)

            assert isinstance(result, Response)
            assert result.is_empty()
            assert mock_authenticator.authorise_request.call_count == 2

    @mock.patch('data_providers.authentication.SiriusAuthenticator', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_get_lpa_by_lpa_online_tool_id_with_no_valid_token(self, mock_authenticator):

        """
        Failure route. We get an unauthorised response on both attempts.
        Two attempts are made as the first token it returned from the cache. The second is fresh. Both fail.
        """

        with responses.RequestsMock() as rsps:

            ident = 'A00000000001'

            # First we're going to return a 401
            # Then next a 200
            lookup_http_response_response_order = [401, 401]

            def lookup_http_response(request):
                return lookup_http_response_response_order.pop(0), {}, json.dumps({})

            rsps.add_callback(
                rsps.GET, os.environ['URL_MEMBRANE'] + '/api/public/v1/lpas?lpa-online-tool-id=%s' % ident,
                callback=lookup_http_response, content_type='application/json',
            )

            # ---

            # First we're going to say the token came from the cache
            # Then on the next call, that it didn't
            authorise_request_response_order = [True, False]

            def authorise_request_response(req, accept_cached_token):
                return req, authorise_request_response_order.pop(0)

            mock_authenticator.authorise_request = mock.MagicMock(side_effect=authorise_request_response)

            # ---

            p = SiriusProvider(mock_authenticator, os.environ['URL_MEMBRANE'])

            # We expect an exception to be throw
            with pytest.raises(UpstreamExceptionError):
                p.get_lpa_by_lpa_online_tool_id(ident)

            # We expect two attempts at getting a valid session
            assert mock_authenticator.authorise_request.call_count == 2

    @mock.patch('data_providers.authentication.SiriusAuthenticator', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_get_lpa_by_lpa_online_tool_id_with_no_valid_token_and_no_cached_token(self, mock_authenticator):

        """
        Failure route. We get an unauthorised response after one attempt.
        Only one attempt is made as the first token returned is fresh.
        """

        with responses.RequestsMock() as rsps:

            ident = 'A00000000001'

            # For the data lookup
            rsps.add(
                rsps.GET, os.environ['URL_MEMBRANE'] + '/api/public/v1/lpas?lpa-online-tool-id=%s' % ident,
                status=401, json=[]
            )

            # ---
            # Mock the authenticator

            def authorise_request_response(req, accept_cached_token):
                return req, False

            mock_authenticator.authorise_request = mock.MagicMock(side_effect=authorise_request_response)

            # ---

            p = SiriusProvider(mock_authenticator, os.environ['URL_MEMBRANE'])

            # We expect an exception to be throw
            with pytest.raises(UpstreamExceptionError):
                p.get_lpa_by_lpa_online_tool_id(ident)

            # We expect only one attempt as the first token returned was 'fresh'.
            assert mock_authenticator.authorise_request.call_count == 1
