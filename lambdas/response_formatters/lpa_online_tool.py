
def format_lpa_collection_by_id(event, response):
    if response.is_empty():
        response.code = 404
        response.payload = {}
        return response

    lpa = response.payload.pop()

    fields = []

    if event['resource'].startswith('/lpa-online-tool'):
        fields = ['onlineLpaId', 'receiptDate', 'registrationDate', 'rejectedDate', 'status']

    # Filter the return fields
    if len(fields) > 0:
        lpa = {k: lpa[k] for k in fields if k in lpa}

    response.payload = lpa

    return response
