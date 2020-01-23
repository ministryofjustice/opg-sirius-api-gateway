# Hypermedia Controls using HAL

HAL, short for "Hypertext Application Language", is an [open specification describing a generic structure for RESTful resources](http://stateless.co/hal_specification.html). The structure it proposes readily achieves the Richardson Maturity Model's Level 3 by ensuring that each resource contains relational links, and that a standard, identifiable structure exists for embedding other resources

> Adopting HAL will make your API explorable, and its documentation easily discoverable from within the API itself. In short, it will make your API easier to work with and therefore more attractive to client developers.

HAL presents two hypermedia types, one for XML and one for JSON. Typically, the type is only relevant for resources returned by the API, as relational links are not usually submitted when creating, updating, or deleting resources.

The generic mediatype that HAL defines for JSON APIs is application/hal+json.

Resources
For JSON resources, the minimum you must do is provide a _links property containing a self relational link. As an example:

#### Adding _links

```json
GET /articles/123
Host: api.example.com
Accept: application/vnd.opg-data.v1+json

returns

{
    "data": {
        "id": 123,
        "title": "Article 123 Title"
        "_links": {
            "self": {
                "href": "http://example.org/api/articles/123"
            },
            "previous": {
                "href": "http://example.org/api/articles/122"
            },
            "next": {
                "href": "http://example.org/api/articles/124"
            },
            "comments": {
                "href": "http://example.org/api/articles/123/comments"
            },
            "add_comment": {
                "href": "http://example.org/api/articles/123/comments"
            },
            "image": {
                "href": "http://example.org/api/articles/123/image"
            },
        }
    }
}
```

If you are including other resources embedded in the resource you are representing, you will provide an _embedded property, containing the named resources. Each resource will be structured as a HAL resource and contain at least a _links property with a self relational link.

```json
GET /articles/123
Host: api.example.com
Accept: application/vnd.opg-data.v1+json

returns

{
    "data": {
        "id": 123,
        "title": "Article 123 Title"
        "_links": {
            "self": {
                "href": "http://example.org/api/articles/123"
            }
        }
        "_embedded": {
            "comments": [
                {
                    "id": "123123",
                    "title": "Someone's Comment"
                    "_links": {
                        "self": {
                            "href": "http://example.org/api/articles/123/comments/123123"
                        }
                    }
                },
                {
                    "id": "456456",
                    "title": "Someone else's comment"
                    "_links": {
                        "self": {
                            "href": "http://example.org/api/articles/123/comments/456456"
                        }
                    }
                }
            ]
        }
    }
}
```


## References

* http://stateless.co/hal_specification.html