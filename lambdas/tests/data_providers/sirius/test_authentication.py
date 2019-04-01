import os
import json
import pytest
import responses
from requests import Request
from data_providers.sirius import SiriusAuthenticator, SiriusAuthenticationError


class TestSiriusAuthenticator(object):

    def teardown_method(self, method):
        # Remove the environment variables after each method
        if 'CREDENTIALS' in os.environ:
            del os.environ['CREDENTIALS']
        if 'URL_MEMBRANE' in os.environ:
            del os.environ['URL_MEMBRANE']

    def test_successful_authentication(self):
        credentials = {'email': 'test@example.com', 'password': 'password'}

        os.environ['CREDENTIALS'] = json.dumps(credentials)
        os.environ['URL_MEMBRANE'] = 'https://example.com'

        with responses.RequestsMock() as rsps:

            test_token = '~token~'

            rsps.add(
                rsps.POST, os.environ['URL_MEMBRANE'] + '/auth/sessions',
                status=201, json={'authentication_token': test_token}
            )

            a = SiriusAuthenticator.factory()

            r = a.authorise_request(Request())

            assert isinstance(r, Request)

            assert 'HTTP-SECURE-TOKEN' in r.headers
            assert r.headers['HTTP-SECURE-TOKEN'] == test_token

    def test_without_credentials(self):
        os.environ['URL_MEMBRANE'] = 'https://example.com'

        with pytest.raises(RuntimeError, match=r'.*CREDENTIALS.*'):
            SiriusAuthenticator.factory()

    def test_without_url(self):
        os.environ['CREDENTIALS'] = json.dumps({'email': 'test@example.com', 'password': 'password'})

        with pytest.raises(RuntimeError, match=r'.*URL_MEMBRANE.*'):
            SiriusAuthenticator.factory()
