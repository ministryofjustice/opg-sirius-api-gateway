from . import InvalidInputError
from data_providers import JsonProvider, SiriusProvider

# --------------------------------------------
# Responsible for:
#   Creating the appropriate data provider
#   looking up the relevant LPA
#   Responding with the correctly filtered response


def get_lpa(lpa_online_tool_id=None, sirius_uid=None):

    provider = JsonProvider()

    if lpa_online_tool_id is not None and sirius_uid is not None:
        # Input violation: Must be one, and only one, of 'lpa_online_tool_id' or 'sirius_uid'
        raise InvalidInputError("Must be either 'lpa_online_tool_id' or 'sirius_uid'; not both")

    elif lpa_online_tool_id is not None:
        return provider.get_lpa_by_lpa_online_tool_id(lpa_online_tool_id)

    elif sirius_uid is not None:
        return provider.get_lpa_by_sirius_uid(sirius_uid)

    else:
        raise InvalidInputError("Either 'lpa_online_tool_id' or 'sirius_uid' is required")


if __name__ == '__main__':
    from pprint import pprint
    result = get_lpa({'lpa_online_tool_id': 'A00000000001'})
    pprint(result)
