import os
import json
import responses
from data_providers import SiriusProvider, Response
from unittest import mock


class TestSiriusProvider(object):

    @mock.patch('data_providers.sirius.SiriusAuthenticator', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_a_lookup(self, mock_authenticator):
        with responses.RequestsMock() as rsps:

            ident = 'A00000000001'

            # For the data lookup
            rsps.add(
                rsps.GET, os.environ['URL_MEMBRANE'] + '/api/public/v1/lpas?lpa-online-tool-id=%s' % ident,
                status=200, json=[]
            )

            # ---
            # Mock the authenticator

            def side_effect(req, accept_cached_token):
                return req, accept_cached_token

            mock_authenticator.authorise_request = mock.MagicMock(side_effect=side_effect)

            # ---

            p = SiriusProvider(mock_authenticator, os.environ['URL_MEMBRANE'])

            result = p.get_lpa_by_lpa_online_tool_id(ident)

            assert isinstance(result, Response)
            assert result.is_empty()
            mock_authenticator.authorise_request.assert_called_once()
