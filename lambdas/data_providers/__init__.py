from datetime import datetime, timezone


def get_datetime():
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()


from .json_provider import JsonProvider
from .sirius_provider import SiriusProvider
