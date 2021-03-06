import json
from .response import Response

# --------------------------------------------
# Responsible for looking up a given LPA from
# JSON, and returning the unamended data.


class JsonProvider:

    @staticmethod
    def factory(data_path='test-data.json'):
        return JsonProvider(data_path)

    # --------------------

    def __init__(self, data_path):
        self._lpas = None
        self._data_path = data_path

    def _get_data(self):
        if not isinstance(self._lpas, dict):
            with open(self._data_path) as f:
                self._lpas = json.load(f)
                print("Loaded JSON testing data")

        return self._lpas

    def get_lpa_by_sirius_uid(self, sirius_uid):
        for lpa in self._get_data():
            # Sirius expects the lookup to be sans dashes.
            # So we strip out the dashes if there are any when looking for a match.
            if 'uId' in lpa and lpa['uId'].replace('-', '') == sirius_uid:
                return Response.factory(sirius_uid, 200, json.dumps([lpa]))

        # Sirius returns an empty list if no LPA is found
        return Response.factory(sirius_uid, 200, json.dumps([]))

    def get_lpa_by_lpa_online_tool_id(self, online_tool_id):
        for lpa in self._get_data():
            if 'onlineLpaId' in lpa and lpa['onlineLpaId'] == online_tool_id:
                return Response.factory(online_tool_id, 200, json.dumps([lpa]))

        # Sirius returns an empty list if no LPA is found
        return Response.factory(online_tool_id, 200, json.dumps([]))
