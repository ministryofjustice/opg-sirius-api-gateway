import json
import hashlib
from datetime import datetime, timezone


class Response(object):

    @staticmethod
    def factory(ident, payload_json):

        return Response(
            ident=ident,
            payload=json.loads(payload_json),
            meta_datetime=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            meta_hash=hashlib.sha1(payload_json.encode()).hexdigest()
        )

    # --------------------------------

    def __init__(self, ident, payload, meta_datetime, meta_hash):
        self.ident = ident
        self.payload = payload
        self.meta_datetime = meta_datetime
        self.meta_hash = meta_hash

    def get_data(self):
        return {
            'id': self.ident,
            'payload': self.payload,
            'meta': {
                'hash': self.meta_hash,
                'datetime': self.meta_datetime,
            }
        }

    # Determines if the payload response is empty
    def is_empty(self):
        return not (isinstance(self.payload, list) or isinstance(self.payload, dict)) or len(self.payload) == 0
