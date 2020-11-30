from data_providers import Response
import includes
from HandlerBase import HandlerBase, InvalidInputError

class LpasRequestCodeHandler(HandlerBase):
    def handle(self, event, context):
        self.get_data_provider_with_cache().request_code(event['body'])

        return Response.factory(ident=0, code=200, payload_json='{}')

handler = LpasRequestCodeHandler.get_handler()
