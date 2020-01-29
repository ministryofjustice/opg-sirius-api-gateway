# Hypermedia as the Engine of Application State

One of the least well understood core tenets of the REST architectural style

HATEOAS is essentially about making your API self-documenting. Essentially, good RESTful APIs should:

* Expose resources - don't make your API consumer guess where your endpoints are
* what parameters are required
* what options are available at a given endpoint

_hat-ee-os_, _hate-O-A-S_,or _hate-ee-ohs_. However you say it, it basically means two things for our API:

* Content Negotiation
* Hypermedia controls

## Content Negotiation

Content Negotiation is something we are implementing as an integral part of [our approach to version control](../0002-api-versioning-strategy.md).

We use the `Accept` header to RESTfully ask for our data to come back with different document-types (representations).

URIs are not supposed to be a bunch of folders and filenames and an API is not just a list of JSON files. An API is a list of resources that can be represented in different formats according to the `Accept` header.

### The [Richardson Maturity Model](https://martinfowler.com/articles/richardsonMaturityModel.html)

0 You're using **HTTP as a transport** system (tunnelling mechanism) for remote interactions.
1 **Resources** Rather than hit a single endpoint the API has adopted a 'Divide and Conquer approach, you have multiple endpoints to represent resources, and you're talking to them
2 **HTTP Verbs and HTTP response codes** You interact with HTTP resources using HTTP verbs, rather than always using POST. If there's a problem of any sort, the API does not respond with a non-2xx response
3 **Hypermedia Controls**. HATEOAS. Tells the client what it can do with the resource object, or related actions that it might take, via URIs. Resources provide canonical links to themselves, as well as link to other, related resources.

## Hypermedia controls

* Self-Descriptive Control Flows: Make it easy for applications to understand the control flow, because instead of having to rely on information that is external to the actual service interactions, all the information required to proceed is contained in the response to a request
* Flexibility: By having self-descriptive control flows, an added advantage is that control flows can change on a per-instance basis
* Separate but Connected: Consumers of hypermedia services do not have to be aware of the implementation boundaries of individual services, as the links between them provide seamless interactions across various APIs
* Statelessness: The REST hypermedia constraint not just requires hypermedia links, but also requires interactions to be stateless. This means that all information required to process a request needs to be contained in the request itself. This constraint makes hypermedia much more robust, because it means that requests can be scattered across servers/services without the need for those requests to be associated through shared data on the server/service side. It is this additional constraint that allows hypermedia to be truly decentralized, because now there is no implicit assumption that all requests have to be processed by a single server/service that uses state information to handle the workflow across requests.


### Examples of non-HATEOAS non-RESTful endpoints:

```bash
GET /articles/show.json?id=123 HTTP/1.1
Host: api.example.com
```

```bash
GET /articles/show.xml?id=123 HTTP1.1
Host: api.example.com
```

Bad, because we're expecting users to somehow 'know' the following:

* that the `show` endpoint exists
* that they must append the desired content-type extension
* that they must use the id param

### HATEOAS-friendly, RESTful endpoint:

JSON:

```json
GET /articles/123 HTTP/1.1
Host: api.example.com
Accept: application/vnd.opg-data.v1+json

returns

{
    "data": {
        "type": "articles",
        "id": "123",
        "attributes": {
            "title": "Article 123"
        }
    }
}
```

YAML:

```yaml
GET /articles/123 HTTP/1.1
Host: api.example.com
Accept: application/vnd.opg-data.v1+yml

returns

---
data:
    type: articles
    id: '123'
    attributes:
        title: Article 123

```

* API respects the Accept Header, or else is free to choose a default content-type
* User does not need to know about the id param

## The HTTP `OPTIONS` verb:

Note that the URI to view a collection of a resource type, and to create a new instance of that resource are one and the same. The user needs to figure out that one is a `GET` and one a `POST`

Luckily the HTTP `OPTIONS` verb has us covered:

```bash
Request:
OPTIONS /articles/
Host: api.example.com

Response:
HTTP/1.1 200 OK
Host: api.example.com
Allow: GET,HEAD,POST
```

By inspecting the Allow header, an API client can work out what options are available at any given endpoint.

## Why On Earth Would We Bother With This??

* The Content Negotiation part is a freebie, that comes with our implementation of Version Control
* Why WOULDN'T we want to design a programmatically self-documenting API, which can grow, change and expand over time... rename URLS even.
* Simply put: Without implementing HATEOAS, our API is not RESTful

## References

* [https://martinfowler.com/articles/richardsonMaturityModel.html](https://martinfowler.com/articles/richardsonMaturityModel.html)
* [http://zacstewart.com/2012/04/14/http-options-method.html](http://zacstewart.com/2012/04/14/http-options-method.html)
* [https://dret.typepad.com/dretblog/2016/08/whypermedia-why-use-hypermedia.html](https://dret.typepad.com/dretblog/2016/08/whypermedia-why-use-hypermedia.html)
