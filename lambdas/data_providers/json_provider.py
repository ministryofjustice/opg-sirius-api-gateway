import json
from datetime import datetime, timezone

# --------------------------------------------
# Responsible for looking up a given LPA from
# JSON, and returning the unamended data.


class JsonProvider:
    def __init__(self, data_path):
        self._lpas = None
        self._data_path = data_path

    def _get_data(self):
        if not isinstance(self._lpas, dict):
            # path = os.path.join(os.path.dirname(__file__), 'example.json')  # File is relative to this script
            with open(self._data_path) as f:
                self._lpas = json.load(f)
                print("Loaded JSON testing data")

        return self._lpas

    def get_lpa_by_sirius_uid(self, sirius_uid):
        for lpa in self._get_data():
            if 'uid' in lpa and lpa['uid'] == sirius_uid:
                return {
                    'metadata': {'date': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()},
                    'payload': lpa
                }

    def get_lpa_by_lpa_online_tool_id(self, online_tool_id):
        for lpa in self._get_data():
            if 'onlineLpaId' in lpa and lpa['onlineLpaId'] == online_tool_id:
                return {
                    'metadata': {'date': datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()},
                    'payload': lpa
                }


if __name__ == '__main__':
    from pprint import pprint
    provider = JsonProvider()
    result = provider.get_lpa_by_lpa_online_tool_id('A00000000002')
    pprint(result)
