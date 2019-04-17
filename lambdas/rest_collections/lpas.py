import os
import logging
from . import InvalidInputError
from data_providers import SiriusProvider, JsonProvider,Response
from data_providers.cache import CacheProviderWrapper
from datetime import datetime, timezone

# --------------------------------------------
# Responsible for:
#   Creating the appropriate data provider
#   looking up the relevant LPA
#   Responding with the correctly filtered response


class LpasCollection:

    @classmethod
    def _calculate_age(cls, str_date):
        d = datetime.fromisoformat(str_date)
        return (datetime.utcnow().replace(tzinfo=timezone.utc) - d).seconds

    @classmethod
    def _prepare_response(cls, collection):

        # If we don't get a 'Response' back, or the response is empty
        if not isinstance(collection, Response) or collection.is_empty():
            return None, 0  # (empty) data and (dummy) age

        age = cls._calculate_age(collection.meta_datetime)

        return collection.payload.pop(), age  # data and age

    # --------------------

    def __init__(self):
        if 'DATA_PROVIDER' in os.environ and os.environ['DATA_PROVIDER'] == 'json':
            self._provider = JsonProvider.factory()
        else:
            self._provider = SiriusProvider.factory()

        if 'DISABLE_DATA_CACHE' in os.environ:
            logging.warning('Data caching is disabled')
        else:
            self._provider = CacheProviderWrapper(self._provider)

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
