import json
import hashlib
from datetime import datetime, timezone


class Response(object):

    @staticmethod
    def factory(ident, code, payload_json):

        return Response(
            ident=ident,
            code=code,
            payload=json.loads(payload_json),
            response_hash=hashlib.sha1((repr(code) + payload_json).encode()).hexdigest(),
            generated_datetime=datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        )

    # --------------------------------

    def __init__(self, ident, code, payload, generated_datetime, response_hash):
        self.ident = ident
        self.code = code
        self.payload = payload
        self.generated_datetime = generated_datetime
        self.response_hash = response_hash

    def get_data(self):
        return {
            'id': self.ident,
            'code': self.code,
            'payload': self.payload,
            'meta': {
                'hash': self.response_hash,
                'datetime': self.generated_datetime,
            }
        }

    # Determines if the payload response is empty
    def is_empty(self):
        return not (isinstance(self.payload, list) or isinstance(self.payload, dict)) or len(self.payload) == 0
