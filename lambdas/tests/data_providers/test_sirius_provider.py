import os
import json
import responses
from data_providers import SiriusProvider, Response

class TestSiriusProvider(object):

    def setup_method(self, method):
        credentials = {'email': 'test@example.com', 'password': 'password'}
        os.environ['CREDENTIALS'] = json.dumps(credentials)
        os.environ['URL_MEMBRANE'] = 'https://example.com'

    def teardown_method(self, method):
        # Remove the environment variables after each method
        if 'CREDENTIALS' in os.environ:
            del os.environ['CREDENTIALS']
        if 'URL_MEMBRANE' in os.environ:
            del os.environ['URL_MEMBRANE']

    def test_the_thing(self):

        with responses.RequestsMock() as rsps:

            ident = 'A00000000001'
            test_token = '~token~'

            # For the auth
            rsps.add(
                rsps.POST, os.environ['URL_MEMBRANE'] + '/auth/sessions',
                status=201, json={'authentication_token': test_token}
            )

            # For the data lookup
            rsps.add(
                rsps.GET, os.environ['URL_MEMBRANE'] + '/api/public/v1/lpas?lpa-online-tool-id=%s' % ident,
                status=200, json=[]
            )

            p = SiriusProvider.factory()

            result = p.get_lpa_by_lpa_online_tool_id(ident)

            assert isinstance(result, Response)
            assert result.is_empty()
