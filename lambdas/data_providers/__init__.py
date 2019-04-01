class InternalExceptionError(Exception):
    pass


class UpstreamExceptionError(Exception):
    pass


class UpstreamTimeoutError(Exception):
    pass


from .json_provider import JsonProvider
from .sirius_provider import SiriusProvider
from .model import Response
