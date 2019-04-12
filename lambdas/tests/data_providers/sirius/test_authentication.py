import os
import json
import pytest
import responses
from unittest import mock
from requests import Request
from data_providers.sirius import SiriusAuthenticator, SiriusAuthenticationError


class TestSiriusAuthenticator(object):

    # -------------------------------------
    # Factory tests

    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'DYNAMODB_AUTH_CACHE_TABE_NAME': 'tabme-name'})
    def test_factory_without_credentials(self):
        with pytest.raises(RuntimeError, match=r'.*CREDENTIALS.*'):
            SiriusAuthenticator.factory()

    @mock.patch.dict('os.environ', {'DYNAMODB_AUTH_CACHE_TABE_NAME': 'tabme-name'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_factory_without_url(self):
        with pytest.raises(RuntimeError, match=r'.*URL_MEMBRANE.*'):
            SiriusAuthenticator.factory()

    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_factory_db_table_name(self):
        with pytest.raises(RuntimeError, match=r'.*DYNAMODB_AUTH_CACHE_TABE_NAME.*'):
            SiriusAuthenticator.factory()

    # -------------------------------------
    # Object tests

    @mock.patch('data_providers.sirius.authentication.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'DYNAMODB_AUTH_CACHE_TABE_NAME': 'tabme-name'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_valid_creds_fresh_token(self, mock_boto3):

        """
        We have valid creds and want a fresh token.
        Authentication succeeds
        """

        with responses.RequestsMock() as rsps:
            test_token = '~token~'

            rsps.add(
                rsps.POST, os.environ['URL_MEMBRANE'] + '/auth/sessions',
                status=201, json={'authentication_token': test_token}
            )

            authenticator = SiriusAuthenticator.factory()

            r, cached_token = authenticator.authorise_request(Request(), accept_cached_token=False)

            # We expect a fresh token.
            assert cached_token is False

            assert isinstance(r, Request)
            assert 'HTTP-SECURE-TOKEN' in r.headers
            assert r.headers['HTTP-SECURE-TOKEN'] == test_token

            # Check we didn't try to access the cache (the wanted a fresh token)
            mock_boto3.resource.return_value.Table.return_value.get_item.assert_not_called()

            # Check the returned token was stored in DynamoDB.
            mock_boto3.resource.return_value.Table.return_value.put_item.assert_called_once_with(
                Item={'id': 'token','token': test_token}
            )

    @mock.patch('data_providers.sirius.authentication.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'DYNAMODB_AUTH_CACHE_TABE_NAME': 'tabme-name'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_invalid_creds_fresh_token(self,mock_boto3):

        """
        We have invalid creds and want a fresh token.
        Authentication fails
        """

        with responses.RequestsMock() as rsps:

            rsps.add(
                rsps.POST, os.environ['URL_MEMBRANE'] + '/auth/sessions',
                status=401, json={}
            )

            authenticator = SiriusAuthenticator.factory()

            with pytest.raises(SiriusAuthenticationError):
                authenticator.authorise_request(Request(), accept_cached_token=False)

            # Check we didn't didn't do anything with the cache
            mock_boto3.resource.return_value.Table.return_value.get_item.assert_not_called()
            mock_boto3.resource.return_value.Table.return_value.put_item.assert_not_called()

    @mock.patch('data_providers.sirius.authentication.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'DYNAMODB_AUTH_CACHE_TABE_NAME': 'tabme-name'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_invalid_creds_cache_miss_token(self,mock_boto3):

        """
        We have invalid creds and want a cached token. But there's no token in the cache.
        Authentication fails
        """

        with responses.RequestsMock() as rsps:

            rsps.add(
                rsps.POST, os.environ['URL_MEMBRANE'] + '/auth/sessions',
                status=401, json={}
            )

            authenticator = SiriusAuthenticator.factory()

            with pytest.raises(SiriusAuthenticationError):
                authenticator.authorise_request(Request(), accept_cached_token=True)

            # Check that we looked up the item in the cache.
            mock_boto3.resource.return_value.Table.return_value.get_item.assert_called_once()

            # But as nothing was return, we try to get a fresh token.

            # But as that fails, we don't try and add anything to the cache.
            mock_boto3.resource.return_value.Table.return_value.put_item.assert_not_called()

    @mock.patch('data_providers.sirius.authentication.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'DYNAMODB_AUTH_CACHE_TABE_NAME': 'tabme-name'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_valid_creds_cache_miss_token(self,mock_boto3):

        """
        We have valid creds and want a cached token. But there's no token in the cache.
        As we have valid creds though, we get a fresh one back instead.
        Authentication succeeds
        """

        with responses.RequestsMock() as rsps:
            test_token = '~token~'

            rsps.add(
                rsps.POST, os.environ['URL_MEMBRANE'] + '/auth/sessions',
                status=201, json={'authentication_token': test_token}
            )

            authenticator = SiriusAuthenticator.factory()
            r, cached_token = authenticator.authorise_request(Request(), accept_cached_token=True)

            # Check that we looked up the item in the cache.
            mock_boto3.resource.return_value.Table.return_value.get_item.assert_called_once()

            # But as nothing was return, we try to get a fresh token.

            # Which works, so we should call put_item
            mock_boto3.resource.return_value.Table.return_value.put_item.assert_called_once_with(
                Item={'id': 'token','token': test_token}
            )

            # As we couldn't get a token from the cache, we got a fresh one. Thus cached_token = false.
            assert cached_token is False

            assert isinstance(r, Request)
            assert 'HTTP-SECURE-TOKEN' in r.headers
            assert r.headers['HTTP-SECURE-TOKEN'] == test_token

    @mock.patch('data_providers.sirius.authentication.boto3', autospec=True)
    @mock.patch.dict('os.environ', {'URL_MEMBRANE': 'https://example.com'})
    @mock.patch.dict('os.environ', {'DYNAMODB_AUTH_CACHE_TABE_NAME': 'tabme-name'})
    @mock.patch.dict('os.environ', {'CREDENTIALS': json.dumps({'email': 'test@example.com', 'password': 'password'})})
    def test_cache_hit_token(self,mock_boto3):

        """
        We want a cached token and there is one available. That token is returned.
        Authentication succeeds
        """

        with responses.RequestsMock() as rsps:
            test_token = '~token~'

            # Return a valid item from the cache.
            mock_boto3.resource.return_value.Table.return_value.get_item.return_value = {
                'Item': {'id': 'token', 'token': test_token}
            }

            authenticator = SiriusAuthenticator.factory()

            r, cached_token = authenticator.authorise_request(Request(), accept_cached_token=True)

            # We expect a fresh token.
            assert cached_token is True

            assert isinstance(r, Request)
            assert 'HTTP-SECURE-TOKEN' in r.headers
            assert r.headers['HTTP-SECURE-TOKEN'] == test_token

            # Nothing new should have tried to be put into teh cache
            mock_boto3.resource.return_value.Table.return_value.put_item.assert_not_called()
