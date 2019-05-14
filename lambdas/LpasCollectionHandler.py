import includes
from rest_collections import InvalidInputError, LpasCollection
from HandlerBase import HandlerBase
import json


class LpasCollectionHandler(HandlerBase):
    """
    Handles requests for the LPA Collection.
    """

    def handle(self, event, context):
        if 'resource' not in event:
            raise InvalidInputError("'resource' missing from event")

        if 'pathParameters' not in event:
            raise InvalidInputError("'pathParameters' missing from event")

        # -------------------------------------
        # Lookup LPA

        c = LpasCollection()
        lpa, age = c.get_lpa(**event['pathParameters'])

        # -------------------------------------
        # Respond

        response = {}

        if lpa is None:
            response["statusCode"] = 404
            response["body"] = {}
        else:
            # -------------------------------------
            # Determine if / what fields the service can return

            fields = []

            if event['resource'].startswith('/lpa-online-tool'):
                fields = ['onlineLpaId', 'receiptDate', 'registrationDate', 'rejectedDate', 'status']

            # TODO: Determine if we want to filter /use-an-lpa at all
            # elif event['resource'].startswith('/use-an-lpa'):
            #    fields = ['uId']

            # Filter the return fields
            if len(fields) > 0:
                lpa = {k: lpa[k] for k in fields if k in lpa}

            response["statusCode"] = 200
            response["body"] = lpa
            response["headers"] = {'Age': age}

        # ---

        response["body"] = json.dumps(response["body"])

        return response


id_handler = LpasCollectionHandler.get_handler()
