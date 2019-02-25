import os
import json
from datetime import datetime

# --------------------------------------------
# Responsible for looking up a given LPA from
# JSON, and returning the unamended data.


class JsonProvider:
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), 'example.json')  # File is relative to this script
        with open(path) as f:
            self.json_data = json.load(f)
            print("Loaded JSON testing data")

    def get_lpa_by_sirius_uid(self, sirius_uid):
        for lpa in self.json_data:
            if 'uid' in lpa and lpa['uid'] == sirius_uid:
                return {
                    'metadata': {'date': datetime.utcnow().isoformat()+'Z'},
                    'payload': lpa
                }

    def get_lpa_by_lpa_online_tool_id(self, online_tool_id):
        for lpa in self.json_data:
            if 'onlineLpaId' in lpa and lpa['onlineLpaId'] == online_tool_id:
                return {
                    'metadata': {'date': datetime.utcnow().isoformat()+'Z'},
                    'payload': lpa
                }


if __name__ == '__main__':
    from pprint import pprint
    provider = JsonProvider()
    result = provider.get_lpa_by_lpa_online_tool_id('A00000000002')
    pprint(result)
