import os
import pytest
from datetime import datetime, timezone
from data_providers import JsonProvider


class TestJsonProvider(object):

    def test_file_not_found(self):
        p = JsonProvider('/does-not-exist.json')

        with pytest.raises(FileNotFoundError):
            p.get_lpa_by_lpa_online_tool_id('A00000000001')

    # ----------------------------------------------------
    # LPA Online tool ID lookup

    def test_get_lpa_by_lpa_online_tool_id_with_invalid_id(self):
        path = os.path.join(os.path.dirname(__file__), 'unit-test-data.json')
        p = JsonProvider(path)

        missing_lookup_id = 'A00005000001'
        result = p.get_lpa_by_lpa_online_tool_id(missing_lookup_id)

        assert result is None

    def test_get_lpa_by_lpa_online_tool_id_with_valid_id(self):
        path = os.path.join(os.path.dirname(__file__), 'unit-test-data.json')
        p = JsonProvider(path)

        lookup_id = 'A00000000001'
        result = p.get_lpa_by_lpa_online_tool_id(lookup_id)

        assert isinstance(result, dict)
        assert 'payload' in result
        assert 'metadata' in result

        assert 'onlineLpaId' in result['payload']
        assert result['payload']['onlineLpaId'] == lookup_id

        # The returned date should be approx 'now'
        assert 'date' in result['metadata']

        date = datetime.fromisoformat(result['metadata']['date'])
        diff = datetime.utcnow().replace(tzinfo=timezone.utc) - date
        assert diff.seconds < 2, 'Returns date is too different from expected (now)'

    # ----------------------------------------------------
    # Sirius uuid lookup

    def test_get_lpa_by_sirius_uid_with_invalid_id(self):
        path = os.path.join(os.path.dirname(__file__), 'unit-test-data.json')
        p = JsonProvider(path)

        missing_lookup_id = '700005000001'
        result = p.get_lpa_by_sirius_uid(missing_lookup_id)

        assert result is None

    def test_get_lpa_by_sirius_uid_with_valid_id(self):
        path = os.path.join(os.path.dirname(__file__), 'unit-test-data.json')
        p = JsonProvider(path)

        lookup_id = '700000000002'
        result = p.get_lpa_by_sirius_uid(lookup_id)

        assert isinstance(result, dict)
        assert 'payload' in result
        assert 'metadata' in result

        assert 'uid' in result['payload']
        assert result['payload']['uid'] == lookup_id

        # The returned date should be approx 'now'
        assert 'date' in result['metadata']

        date = datetime.fromisoformat(result['metadata']['date'])
        diff = datetime.utcnow().replace(tzinfo=timezone.utc) - date
        assert diff.seconds < 2, 'Returns date is too different from expected (now)'
