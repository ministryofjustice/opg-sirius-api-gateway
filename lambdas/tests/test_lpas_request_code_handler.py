import pytest
from unittest import mock
from LpasRequestCodeHandler import *

class TestLpasRequestCodeHandler(object):
    def test_called(self):
        mock_data_provider = mock.MagicMock()

        mock_returning_data_provider = mock.MagicMock()
        mock_returning_data_provider.return_value = mock_data_provider
        HandlerBase.get_data_provider_with_cache = mock_returning_data_provider

        handler = LpasRequestCodeHandler()
        handler.handle({'body': '{"some": "json"}'}, {})

        mock_returning_data_provider.assert_called_once()
        mock_data_provider.request_code.assert_called_once()
