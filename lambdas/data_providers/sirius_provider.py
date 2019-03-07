from data_providers.sirius import SiriusAuthenticator
from requests import Request, Session
from . import get_datetime

# --------------------------------------------
# Responsible for looking up a given LPA from
# Sirius, and returning the unamended data.


class SiriusProvider:

    @staticmethod
    def factory():
        return SiriusProvider(SiriusAuthenticator.factory())

    # --------------------

    def __init__(self, authenticator):
        self._authenticator = authenticator

    def get_lpa_by_sirius_uid(self, sirius_uid):
        pass

    def get_lpa_by_lpa_online_tool_id(self, online_tool_id):
        s = Session()

        url = 'https://membrane/api/case/1'
        url = 'https://localhost:8081/api/case/1'

        req = Request('GET', url).prepare()

        # Decorate the request with an authentication token
        req = self._authenticator.authorise_request(req)

        resp = s.send(req, verify=False, timeout=5)

        if resp.status_code == 200:
            return {
                'metadata': {'date': get_datetime()},
                'payload': resp.json()
            }
