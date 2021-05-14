
def format_lpa_collection_by_id(event, response):
    if response.is_empty():
        response.code = 404
        response.payload = {}
        return response

    lpa = response.payload.pop()

    fields = []

    if event['resource'].startswith('/lpa-online-tool'):
        fields = ['onlineLpaId', 'receiptDate', 'registrationDate', 'rejectedDate', 'cancellationDate', 'invalidDate', 'withdrawnDate', 'status', 'dispatchDate']

    # Filter the return fields
    if len(fields) > 0:
        lpa = {k: lpa[k] for k in fields if k in lpa}

    # Remove styling from Sirius uIds
    lpa = format_sirius_uid(lpa)

    response.payload = lpa

    return response


# Recursively removes dashes from Sirius UIDs.
def format_sirius_uid(lpas):
    for k, v in lpas.items():
        if isinstance(v, dict):
            lpas[k] = format_sirius_uid(v)
        elif isinstance(v, list):
            for i, j in enumerate(v):
                v[i] = format_sirius_uid(j)
        elif k == 'uId':
            lpas[k] = v.replace('-', '')
    return lpas
