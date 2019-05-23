import pytest
from unittest import mock
from LpasCollectionHandler import *


class TestLpasCollectionHandler(object):
    """
    Tests only the specific login within LpasCollectionHandler; not anything within HandlerBase.
    """

    def test_calling_without_expected_path_parameter(self):
        """
        We expect an exception tyo be raised if lpa_online_tool_id or sirius_uid is not passed.
        """
        handler = LpasCollectionHandler()
        with pytest.raises(InvalidInputError):
            handler.handle({'pathParameters': {}}, {})

    @mock.patch('response_formatters.format_lpa_collection_by_id', autospec=True)
    def test_with_a_lpa_online_tool_id(self, response_formatter):
        """
        We expect the correct functions on the data provider and formatter to be called for a lpa_online_tool_id.
        """
        mock_data_provider = mock.MagicMock()

        mock_returning_data_provider = mock.MagicMock()
        mock_returning_data_provider.return_value = mock_data_provider
        HandlerBase.get_data_provider_with_cache = mock_returning_data_provider

        handler = LpasCollectionHandler()
        handler.handle({'pathParameters': {
            'lpa_online_tool_id': '123',
        }}, {})

        mock_returning_data_provider.assert_called_once()
        mock_data_provider.get_lpa_by_lpa_online_tool_id.assert_called_once()
        response_formatter.assert_called_once()

    @mock.patch('response_formatters.format_lpa_collection_by_id', autospec=True)
    def test_with_a_sirius_uid(self, response_formatter):
        """
        We expect the correct functions on the data provider and formatter to be called for a sirius_uid.
        """
        mock_data_provider = mock.MagicMock()

        mock_returning_data_provider = mock.MagicMock()
        mock_returning_data_provider.return_value = mock_data_provider
        HandlerBase.get_data_provider_with_cache = mock_returning_data_provider

        handler = LpasCollectionHandler()
        handler.handle({'pathParameters': {
            'sirius_uid': '123',
        }}, {})

        mock_returning_data_provider.assert_called_once()
        mock_data_provider.get_lpa_by_sirius_uid.assert_called_once()
        response_formatter.assert_called_once()
