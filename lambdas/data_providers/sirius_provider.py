import os
from data_providers.sirius import SiriusAuthenticator, SiriusAuthenticationError
from requests import Request, Session, exceptions
from .model import Response
from . import UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError

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

    def get_lpa_by_lpa_online_tool_id(self, online_tool_id):

        try:
            s = Session()

            url = self._membrane_url + '/api/public/v1/lpas?lpa-online-tool-id=%s' % online_tool_id

            req = Request('GET', url, headers={'host': 'membrane'}).prepare()

            # Decorate the request with an authentication token
            req = self._authenticator.authorise_request(req)

            resp = s.send(req, verify=False, timeout=(3.05, 5))

            if resp.status_code == 200:
                return Response.factory(online_tool_id, resp.text)

        except SiriusAuthenticationError:
            raise InternalExceptionError('Sirius authentication error')

        except exceptions.Timeout:
            raise UpstreamTimeoutError

        except exceptions.RequestException as e:
            raise UpstreamExceptionError(e)
