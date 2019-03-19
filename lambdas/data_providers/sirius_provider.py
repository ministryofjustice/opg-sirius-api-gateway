import os
from data_providers.sirius import SiriusAuthenticator
from requests import Request, Session
from .model import Response

# --------------------------------------------
# Responsible for looking up a given LPA from
# Sirius, and returning the unamended data.


class SiriusProvider:

    @staticmethod
    def factory():
        return SiriusProvider(SiriusAuthenticator.factory(), os.environ['URL_MEMBRANE'])

    # --------------------

    def __init__(self, authenticator, membrane_url):
        self._authenticator = authenticator
        self._membrane_url = membrane_url

    def get_lpa_by_sirius_uid(self, sirius_uid):
        pass

    def get_lpa_by_lpa_online_tool_id(self, online_tool_id):
        s = Session()

        url = self._membrane_url + '/api/public/v1/lpas?lpa-online-tool-id=%s' % online_tool_id

        req = Request('GET', url).prepare()

        # Decorate the request with an authentication token
        req = self._authenticator.authorise_request(req)

        resp = s.send(req, verify=False, timeout=(3.05, 5))

        if resp.status_code == 200:
            return Response.from_sirius_factory(online_tool_id, resp.text)
