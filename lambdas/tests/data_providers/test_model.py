import json
import hashlib
from datetime import datetime, timezone
from data_providers import Response


class TestProviderResponse(object):

    def test_is_empty_when_directly_instantiated(self):
        r = Response(
            ident='abc',
            payload=None,
            meta_datetime=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            meta_hash=hashlib.sha1('fake-json'.encode()).hexdigest()
        )
        assert r.is_empty()

    def test_is_empty_when_empty_with_none(self):
        r = Response.factory('123', json.dumps(None))
        assert r.is_empty()

    def test_is_empty_when_empty_with_list(self):
        r = Response.factory('123', json.dumps([]))
        assert r.is_empty()

    def test_is_empty_when_empty_with_dict(self):
        r = Response.factory('123', json.dumps({}))
        assert r.is_empty()

    def test_is_empty_when_it_is_not_emoty(self):
        r = Response.factory('123', json.dumps([
            {"test": True}
        ]))
        assert not r.is_empty()
