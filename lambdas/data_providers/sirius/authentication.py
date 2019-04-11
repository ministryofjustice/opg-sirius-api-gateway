import os
import json
import requests
import urllib3
import boto3
import logging
from . import SiriusAuthenticationError
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SiriusAuthenticator:

    """
    Given a Request object, decorate it with the required token header.

    Typically you should call authorise_request() with accept_cached_token = True in the first instance.
    If the returned token turns out to be stale, then recall authorise_request() with accept_cached_token = False.
    """

    @staticmethod
    def factory():
        if 'CREDENTIALS' not in os.environ:
            raise RuntimeError('CREDENTIALS not set')

        if 'URL_MEMBRANE' not in os.environ:
            raise RuntimeError('URL_MEMBRANE not set')

        if 'DYNAMODB_AUTH_CACHE_TABE_NAME' not in os.environ:
            raise RuntimeError('DYNAMODB_AUTH_CACHE_TABE_NAME not set')

        if 'AWS_ENDPOINT_DYNAMODB' in os.environ:
            # For local development
            dynamodb_endpoint_url = os.environ['AWS_ENDPOINT_DYNAMODB']
            logging.debug('AWS_ENDPOINT_DYNAMODB set %s' % dynamodb_endpoint_url)
        else:
            # Should be none in AWS
            dynamodb_endpoint_url = None

        credentials = json.loads(os.environ['CREDENTIALS'])

        return SiriusAuthenticator(os.environ['URL_MEMBRANE'],
                                   credentials,
                                   os.environ['DYNAMODB_AUTH_CACHE_TABE_NAME'],
                                   dynamodb_endpoint_url)

    # ----------------------------------------------

    def __init__(self, membrane_url, credentials, dynamodb_cache_table, dynamodb_endpoint_url):
        self._membrane_url = membrane_url
        self._credentials = credentials
        self._dynamodb_cache_table = dynamodb_cache_table
        self._dynamodb_endpoint_url = dynamodb_endpoint_url

    def authorise_request(self, req, accept_cached_token):

        """
        Acquires an authentication token and decorates the request with it.
            If `accept_cached_token` = True, we may return a token from the cache.
            It may be stale. If authentication fails this method should be recalled with `accept_cached_token` = False

            If `accept_cached_token` = True, but there's no token in DynamoDB, then we'll automatically recall
            this method with `accept_cached_token` = True.

            Whenever a new token is generated, it is stored in the cache.
        """

        session = boto3.Session()
        dynamodb = session.resource('dynamodb', endpoint_url=self._dynamodb_endpoint_url)
        cache_table = dynamodb.Table(self._dynamodb_cache_table)  # Is lazy

        if accept_cached_token is True:

            # We are looking up the token in DynamoDB.
            # If there is no token, we return a fresh one.

            result = self._get_cached_auth_token(cache_table)

            # If we didn't get a cached token, automatically respond with a refresh token
            if result is False:
                logging.info('Failed to load a token from cache. Requesting a fresh one.')
                return self.authorise_request(req, False)
            else:
                # Else we set the header
                logging.info('Returning a cached token')
                req.headers['HTTP-SECURE-TOKEN'] = result

        else:
            logging.info('Returning a fresh token')
            req.headers['HTTP-SECURE-TOKEN'] = self._get_fresh_auth_token(cache_table)

        return req, accept_cached_token

    def _get_fresh_auth_token(self, cache_table):
        data = {'user': self._credentials}

        url = self._membrane_url + '/auth/sessions'

        r = requests.post(url, json=data, allow_redirects=False,
                          verify=False, timeout=(3.05, 5), headers={'host': 'membrane'})

        if r.status_code == 201:
            details = r.json()
            if 'authentication_token' in details:
                # Add the new key into the cache
                cache_table.put_item(
                    Item={
                        'id': 'token',
                        'token': details['authentication_token'],
                    }
                )
                return details['authentication_token']

        raise SiriusAuthenticationError()

    def _get_cached_auth_token(self, cache_table):

        """
        Looks for a cached token in DynamoDB
        """

        response = cache_table.get_item(
            Key={'id': 'token'}
        )

        if 'Item' not in response:
            return False

        item = response['Item']

        if 'token' not in item:
            return False

        return item['token']
