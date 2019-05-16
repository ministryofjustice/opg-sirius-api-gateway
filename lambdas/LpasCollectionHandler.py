import includes
from HandlerBase import HandlerBase, InvalidInputError
import response_formatters


class LpasCollectionHandler(HandlerBase):
    """
    Handles requests for the LPA Collection.
    """

    def handle(self, event, context):

        raise InvalidInputError

        if 'lpa_online_tool_id' in event['pathParameters']:

            response = self.get_data_provider_with_cache().get_lpa_by_lpa_online_tool_id(
                event['pathParameters']['lpa_online_tool_id']
            )

            return response_formatters.format_lpa_collection_by_id(event, response)

        elif 'sirius_uid' in event['pathParameters']:

            response = self.get_data_provider_with_cache().get_lpa_by_sirius_uid(
                event['pathParameters']['sirius_uid']
            )

            return response_formatters.format_lpa_collection_by_id(event, response)

        else:
            raise InvalidInputError("Either 'lpa_online_tool_id' or 'sirius_uid' is required")


id_handler = LpasCollectionHandler.get_handler()
