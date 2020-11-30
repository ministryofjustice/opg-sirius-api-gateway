import includes
import response_formatters
from HandlerBase import HandlerBase, InvalidInputError

class LpasRequestCodeHandler(HandlerBase):
    def handle(self, event, context):
        self.get_data_provider_with_cache().request_code(event['actor_uid'], event['case_uid'])

        return Response(code=204, payload='')

handler = LpasRequestCodeHandler.get_handler()
