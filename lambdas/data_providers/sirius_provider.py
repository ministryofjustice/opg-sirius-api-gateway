import os
from data_providers.sirius import SiriusAuthenticator, SiriusAuthenticationError
from requests import Request, Session, exceptions
from .model import Response
from . import UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError
import logging

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

        logging.info("Sirius lookup of %s" % online_tool_id)

        try:
            url = self._membrane_url + '/api/public/v1/lpas?lpa-online-tool-id=%s' % online_tool_id

            resp, cached_token = self._attempt_get(url=url, accept_cached_token=True)

            # If we get a 401 Unauthorized, try again with the cached token
            if resp.status_code == 401 and cached_token is True:
                logging.warning('Lookup failed with cached token. Refreshing token.')
                resp, cached_token = self._attempt_get(url=url, accept_cached_token=False)

            # If we get a 200, all is good. Return teh result.
            if resp.status_code == 200:
                return Response.factory(online_tool_id, resp.text)

            # If we reach here, all has failed.
            raise UpstreamExceptionError('Sirius returned an unexpected response %d - %s', resp.status_code, resp.text)

        except SiriusAuthenticationError:
            raise InternalExceptionError('Sirius authentication error')

        except exceptions.Timeout:
            raise UpstreamTimeoutError

        except exceptions.RequestException as e:
            raise UpstreamExceptionError(e)

    def _attempt_get(self, url, accept_cached_token):
        s = Session()

        req = Request('GET', url, headers={'host': 'membrane'}).prepare()

        req, cached = self._authenticator.authorise_request(req, accept_cached_token=accept_cached_token)

        return s.send(req, verify=False, timeout=(3.05, 5)), cached
