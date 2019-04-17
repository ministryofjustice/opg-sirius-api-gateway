import json
import hashlib
from datetime import datetime, timezone


class Response(object):

    @staticmethod
    def factory(ident, payload_json):

        return Response(
            ident=ident,
            payload=json.loads(payload_json),
            payload_hash=hashlib.sha1(payload_json.encode()).hexdigest(),
            generated_datetime=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        )

    # --------------------------------

    def __init__(self, ident, payload, generated_datetime, payload_hash):
        self.ident = ident
        self.payload = payload
        self.generated_datetime = generated_datetime
        self.payload_hash = payload_hash

    def get_data(self):
        return {
            'id': self.ident,
            'payload': self.payload,
            'meta': {
                'hash': self.payload_hash,
                'datetime': self.generated_datetime,
            }
        }

    # Determines if the payload response is empty
    def is_empty(self):
        return not (isinstance(self.payload, list) or isinstance(self.payload, dict)) or len(self.payload) == 0
