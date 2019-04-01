import os
from . import InvalidInputError
from data_providers import SiriusProvider, JsonProvider
from datetime import datetime, timezone

# --------------------------------------------
# Responsible for:
#   Creating the appropriate data provider
#   looking up the relevant LPA
#   Responding with the correctly filtered response


class LpasCollection:

    @staticmethod
    def factory():
        if 'DATA_PROVIDER' in os.environ and os.environ['DATA_PROVIDER'] == 'json':
            return LpasCollection(JsonProvider.factory())
        else:
            #return LpasCollection(SiriusProvider.factory())
            return LpasCollection(JsonProvider.factory())

    @classmethod
    def _calculate_age(cls, str_date):
        d = datetime.fromisoformat(str_date)
        return (datetime.utcnow().replace(tzinfo=timezone.utc) - d).seconds

    @classmethod
    def _prepare_response(cls, collection):
        # For the LPA collection lookup, we're expecting an array of 1 item back.
        if collection is None \
                or 'payload' not in collection.data \
                or type(collection.data['payload']) is not list \
                or len(collection.data['payload']) != 1:
            return None, 0  # (empty) data and (dummy) age

        age = cls._calculate_age(collection.data['meta']['datetime'])

        return collection.data['payload'].pop(), age  # data and age

    # --------------------

    def __init__(self, provider):
        self._provider = provider

    def get_lpa(self, lpa_online_tool_id=None, sirius_uid=None):

        if lpa_online_tool_id is not None and sirius_uid is not None:
            # Input violation: Must be one, and only one, of 'lpa_online_tool_id' or 'sirius_uid'
            raise InvalidInputError("Must be either 'lpa_online_tool_id' or 'sirius_uid'; not both")

        elif lpa_online_tool_id is not None:
            collection = self._provider.get_lpa_by_lpa_online_tool_id(lpa_online_tool_id)
            return self._prepare_response(collection)

        elif sirius_uid is not None:
            collection = self._provider.get_lpa_by_sirius_uid(sirius_uid)
            return self._prepare_response(collection)

        else:
            raise InvalidInputError("Either 'lpa_online_tool_id' or 'sirius_uid' is required")
