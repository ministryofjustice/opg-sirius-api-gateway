# 7. Error Handling And Status Codes

Date: 2020-01-27

## Status

Proposed

## Context

If a valid request comes in for data, we show data. If creating a resource, we show the created resource, along with HATEOAS links showing what a client may do with it.

## Decision

If something goes wrong, we use two simultaneous approaches

* Return an appropriate HTTP status code
* Return one or more custom error codes and messages

### HTTP status codes

Without overdoing it, here is a simple set of error codes that we will implement:

* 200 - Generic everything is OK
* 201 - Created something OK
* 202 - Accepted but is being processed async (eg video transcoding)
* 301 - Moved Permanently (although we would provide the new link in with HATEOAS also)
* 400 - Generic bad request (generally invalid syntax)
* 401 - Unauthorised (no current user and there should be)
* 403 - Forbidden - The current user is forbidden from accessing this data (in this way)
* 404 - That URL is not a valid route, or the item resource does not exist
* 405 - Method not allowed
* 410 - Data has been deleted, deactivated, suspended etc
* 413 - Payload too large
* 415 - Unsupported media type
* 500 - Something unexpected happened and it is the API's fault
* 503 - Service Unavailable - please try again later (although the client might choose to queue and retry any request which returns a 5xx)

### Custom error codes and messages

JSON-API states:
> A server MAY choose to stop processing as soon as a problem is encountered, or it MAY continue processing and encounter multiple problems. For instance, a server might process multiple attributes and then return multiple validation problems in a single response.

With `opg-data` API **we will always endeavour to provide an array of all errors** in a single response, rather than feeding errors out singly, causing the consumer to discover a new error with each subsequent request. Painful.

### <a name="errors-in-20x"></a> 200 and 201 means success - with ONE exception

A 200 or 201 status code offers certainty to the API consumer that their operation was **A SUCCESS**. There should **never** be an error code/message returned as a response to a 20x.

**With ONE exception**... (appropriated from Twitter):

> In some cases you may see the errors detailed above in a response that returned a 200 status code. In those cases, the endpoint is designed to return the data that it can, while providing detailed errors about what it could not return.

So, for GET queries where a range of resources are attempted, we return those resources that could be successfully retrieved, and provide error messages about those that couldn't be.

### Error formatting

See [JSON-API](https://jsonapi.org/format/#errors)

> Error objects **MUST** be returned as an array keyed by errors in the top level of a JSON:API document.

Below are some of the suggested response members

The following members are required:

* code
* title

## Examples

### 404 Not Found

```json
PATCH /clients/invalidID HTTP/1.1
Host: api.example.com
Accept: application/vnd.opg-data.v1+json

{
    "data": {
        "type": "clients",
        "id": "invalidID",
        "attributes": {
            "first_name": "Bob",
            "last_name": "Jones"
        }
    }
}
```

```json
HTTP/1.1 404 Not Found
Host: api.example.com
Content-Type: application/vnd.opg-data.v1+json

{
    "errors": [
        {
            "id": "A123BCD",
            "links": {
                "about": "https://api.example.com/help/errors/no-resource"
            },
            "code": "OPGDATA-API-NO-RESOURCE",
            "title": "No resource at this URI",
            "detail": "You requested a resource which doesn't exist",
            "source": {
                "parameter": "id"
            }
        }
    ]
}
```

### 403 Forbidden

```json
PATCH /clients/123123abc HTTP/1.1
Host: api.example.com
Accept: application/vnd.opg-data.v1+json

{
    "data": {
        "type": "clients",
        "id": "123123abc",
        "attributes": {
            "admin_rights", "elevated",
            "payment_status", "paid"
        }
    }
}
```

```json
HTTP/1.1 403 Forbidden
Host: api.example.com
Content-Type: application/vnd.opg-data.v1+json

{
    "errors": [
        {
            "id": "A123BCD",
            "links": {
                "about": "https://api.example.com/help/errors/forbidden"
            },
            "code": "OPGDATA-API-FORBIDDEN",
            "title": "User Lacks Permissions",
            "detail": "You are not authorised to perform the selected action(s) on this resource",
            "source": {
                "parameter": "/data/attributes/admin_rights"
            }
        },
        {
            "id": "B456DEF",
            "links": {
                "about": "https://api.example.com/help/errors/forbidden"
            },
            "code": "OPGDATA-API-FORBIDDEN",
            "title": "User Lacks Permissions",
            "detail": "You are not authorised to perform the selected action(s) on this resource",
            "source": {
                "pointer": "/data/attributes/payment_status"
            }
        }
    ]
}
```

For more details, see [https://jsonapi.org/format/#errors](https://jsonapi.org/format/#errors)

## Consequences

* Standardised unambiguous error reporting, using the established JSON-API format, aiming to point our consumer to the source of the error as quickly as possible.
* Returning multiple errors as an array is very helpful to the consumer

