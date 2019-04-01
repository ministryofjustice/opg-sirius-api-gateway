import os
import pytest
from datetime import datetime, timezone
from data_providers import JsonProvider, Response


class TestJsonProvider(object):

    def test_file_not_found(self):
        p = JsonProvider.factory('/does-not-exist.json')

        with pytest.raises(FileNotFoundError):
            p.get_lpa_by_lpa_online_tool_id('A00000000001')

    # ----------------------------------------------------
    # LPA Online tool ID lookup

    def test_get_lpa_by_lpa_online_tool_id_with_invalid_id(self):
        path = os.path.join(os.path.dirname(__file__), 'unit-test-data.json')
        p = JsonProvider.factory(path)

        missing_lookup_id = 'A00005000001'
        result = p.get_lpa_by_lpa_online_tool_id(missing_lookup_id)

        assert isinstance(result, Response)
        assert result.is_empty()

    def test_get_lpa_by_lpa_online_tool_id_with_valid_id(self):
        path = os.path.join(os.path.dirname(__file__), 'unit-test-data.json')
        p = JsonProvider.factory(path)

        lookup_id = 'A00000000001'
        result = p.get_lpa_by_lpa_online_tool_id(lookup_id)

        assert isinstance(result, Response)
        assert not result.is_empty()

        assert 'payload' in result.get_data()
        assert 'meta' in result.get_data()

        meta = result.get_data()['meta']
        payload = result.get_data()['payload']

        # ---------------------
        # Test the payload

        assert isinstance(payload, list)
        assert len(payload) == 1

        # The real data is in a list, so pop it out.
        payload = payload.pop()

        assert 'onlineLpaId' in payload
        assert payload['onlineLpaId'] == lookup_id

        # ---------------------
        # Test the metadata

        # The returned date should be approx 'now'
        assert 'datetime' in meta

        date = datetime.fromisoformat(meta['datetime'])
        diff = datetime.utcnow().replace(tzinfo=timezone.utc) - date
        assert diff.seconds < 2, 'Returns date is too different from expected (now)'

    # ----------------------------------------------------
    # Sirius uuid lookup

    def test_get_lpa_by_sirius_uid_with_invalid_id(self):
        path = os.path.join(os.path.dirname(__file__), 'unit-test-data.json')
        p = JsonProvider.factory(path)

        missing_lookup_id = '700005000001'
        result = p.get_lpa_by_sirius_uid(missing_lookup_id)

        assert isinstance(result, Response)
        assert result.is_empty()

    def test_get_lpa_by_sirius_uid_with_valid_id(self):
        path = os.path.join(os.path.dirname(__file__), 'unit-test-data.json')
        p = JsonProvider.factory(path)

        lookup_id = '700000000002'
        result = p.get_lpa_by_sirius_uid(lookup_id)

        assert isinstance(result, Response)
        assert not result.is_empty()

        assert 'payload' in result.get_data()
        assert 'meta' in result.get_data()

        meta = result.get_data()['meta']
        payload = result.get_data()['payload']

        # ---------------------
        # Test the payload

        assert isinstance(payload, list)
        assert len(payload) == 1

        # The real data is in a list, so pop it out.
        payload = payload.pop()

        assert 'uId' in payload
        assert payload['uId'] == lookup_id

        # ---------------------
        # Test the metadata

        # The returned date should be approx 'now'
        assert 'datetime' in meta

        date = datetime.fromisoformat(meta['datetime'])
        diff = datetime.utcnow().replace(tzinfo=timezone.utc) - date
        assert diff.seconds < 2, 'Returns date is too different from expected (now)'
