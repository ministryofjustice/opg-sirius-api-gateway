import os
from data_providers.authentication import SiriusAuthenticator, SiriusAuthenticationError
from requests import Request, Session, exceptions
from .response import Response
from . import UpstreamExceptionError, UpstreamTimeoutError, InternalExceptionError
import logging

# --------------------------------------------
# Responsible for looking up a given LPA from
# Sirius, and returning the unamended data.


class SiriusProvider:

    @staticmethod
    def factory():
        disable_lookup = 'DISABLE_SIRIUS_LOOKUP' in os.environ and os.environ['DISABLE_SIRIUS_LOOKUP'] == 'true'
        return SiriusProvider(SiriusAuthenticator.factory(), os.environ['URL_MEMBRANE'], disable_lookup)

    # --------------------

    def __init__(self, authenticator, membrane_url, force_return_upstream_exception_error):
        self._authenticator = authenticator
        self._membrane_url = membrane_url
        self._force_return_upstream_exception_error = force_return_upstream_exception_error

    def get_lpa_by_sirius_uid(self, sirius_uid):
        url = self._membrane_url + '/api/public/v1/lpas?uid=%s' % sirius_uid
        return self._get_lpa(sirius_uid, url)

    def get_lpa_by_lpa_online_tool_id(self, online_tool_id):
        url = self._membrane_url + '/api/public/v1/lpas?lpa-online-tool-id=%s' % online_tool_id
        return self._get_lpa(online_tool_id, url)

    def request_code(self, actor_uid, case_uid):
        url = self._membrane_url + '/api/public/v1/lpas/requestCode'
        data = {'actor_uid': actor_uid, 'case_uid': case_uid}

        try:
            resp, cached_token = self._attempt_post(url=url, json=data, accept_cached_token=True)

            # If we get a 401 Unauthorized, try again with the cached token
            if resp.status_code == 401 and cached_token is True:
                logging.warning('Request code failed with cached token. Refreshing token.')
                resp, cached_token = self._attempt_post(url=url, json=data, accept_cached_token=False)

            if resp.status_code == 204:
                return ()

            raise UpstreamExceptionError('Sirius returned an unexpected response %d - %s' % (resp.status_code, resp.text))

        except SiriusAuthenticationError:
            raise InternalExceptionError('Sirius authentication error')

        except exceptions.Timeout:
            raise UpstreamTimeoutError

        except exceptions.RequestException as e:
            raise UpstreamExceptionError(e)


    def _get_lpa(self, id_value, url):
        """
        Performs the lookup of the requested LPA.

        If the first look fails with a 401 Unauthorised, and the attempt was made with a cached auto token,
        we make one further attempt with a fresh auth token.
        """

        logging.info("Sirius lookup of %s" % id_value)

        if self._force_return_upstream_exception_error:
            logging.warning("The Sirius data provider is currently set to always return an UpstreamExceptionError. "
                            "Returning straight away.")
            raise UpstreamExceptionError('Provider disabled.')

        try:
            resp, cached_token = self._attempt_get(url=url, accept_cached_token=True)

            # If we get a 401 Unauthorized, try again with the cached token
            if resp.status_code == 401 and cached_token is True:
                logging.warning('Lookup failed with cached token. Refreshing token.')
                resp, cached_token = self._attempt_get(url=url, accept_cached_token=False)

            # If we get a 200, all is good. Return the result.
            if resp.status_code == 200:
                return Response.factory(id_value, resp.status_code, resp.text)

            # If we reach here, all has failed.
            raise UpstreamExceptionError('Sirius returned an unexpected response %d - %s' % (resp.status_code, resp.text))

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

    def _attempt_post(self, url, json, accept_cached_token):
        s = Session()

        req = Request('POST', url, json=json, headers={'host': 'membrane'}).prepare()

        req, cached = self._authenticator.authorise_request(req, accept_cached_token=accept_cached_token)

        return s.send(req, verify=False, timeout=(3.05, 5)), cached
