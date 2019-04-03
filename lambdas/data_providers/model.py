import json
import hashlib
from datetime import datetime, timezone


class Response(object):

    @staticmethod
    def factory(ident, payload_json):

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

    # Determines if the payload response is empty
    def is_empty(self):
        return not isinstance(self.data, dict) \
                or 'payload' not in self.data \
                or not (isinstance(self.data['payload'], list) or isinstance(self.data['payload'], dict)) \
                or len(self.data['payload']) == 0
