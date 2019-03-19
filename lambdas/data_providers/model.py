import json
import hashlib
from datetime import datetime, timezone


class Response(object):

    @staticmethod
    def from_sirius_factory(ident, payload_json):

        return Response({
            'id': ident,
            'payload': json.loads(payload_json),
            'meta': {
                'hash': hashlib.sha1(payload_json.encode()).hexdigest(),
                'datetime': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            }
        })

    # --------------------------------

    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data
