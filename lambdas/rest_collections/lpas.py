from . import InvalidInputError
from data_providers import SiriusProvider, JsonProvider

# --------------------------------------------
# Responsible for:
#   Creating the appropriate data provider
#   looking up the relevant LPA
#   Responding with the correctly filtered response


class LpasCollection:

    @staticmethod
    def factory():
        #return LpasCollection(SiriusProvider.factory())
        return LpasCollection(JsonProvider.factory())

    # --------------------

    def __init__(self, provider):
        self._provider = provider

    def get_lpa(self, lpa_online_tool_id=None, sirius_uid=None):

        if lpa_online_tool_id is not None and sirius_uid is not None:
            # Input violation: Must be one, and only one, of 'lpa_online_tool_id' or 'sirius_uid'
            raise InvalidInputError("Must be either 'lpa_online_tool_id' or 'sirius_uid'; not both")

        elif lpa_online_tool_id is not None:
            lpa = self._provider.get_lpa_by_lpa_online_tool_id(lpa_online_tool_id)
            if lpa is not None:
                return lpa['payload']
            return lpa

        elif sirius_uid is not None:
            lpa = self._provider.get_lpa_by_sirius_uid(sirius_uid)
            if lpa is not None:
                return lpa['payload']
            return lpa

        else:
            raise InvalidInputError("Either 'lpa_online_tool_id' or 'sirius_uid' is required")
