import os
import json
import requests
import urllib3
from . import SiriusAuthenticationError
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SiriusAuthenticator:

    """
    Given a Request object, decorate it with the required token header.
    In its current form a new authentication token will be acquired for each data lookup.
    """

    @staticmethod
    def factory():
        credentials = json.loads(os.environ['CREDENTIALS'])
        return SiriusAuthenticator(os.environ['URL_MEMBRANE'], credentials)

    # --------------------

    def __init__(self, membrane_url, credentials):
        self._membrane_url = membrane_url
        self._credentials = credentials

    def authorise_request(self, req):
        req.headers['HTTP-SECURE-TOKEN'] = self._get_auth_token()
        return req

    def _get_auth_token(self):
        data = {'user': self._credentials}

        url = self._membrane_url + '/auth/sessions'

        r = requests.post(url, json=data, allow_redirects=False, verify=False, timeout=(3.05, 5))

        if r.status_code == 201:
            details = r.json()
            if 'authentication_token' in details:
                return details['authentication_token']

        raise SiriusAuthenticationError()
