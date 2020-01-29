# API Versioning Strategy

Our chosen strategy is defined in ADR [2. API versioning strategy](../decisions/0002-api-versioning-strategy.md)

## <a name="semver"></a> Semantic Versioning Numbering

We will be using semantic versioning [https://semver.org](https://semver.org) -  all breaking changes will be signified by the first number:

[breaking].[non-breaking features].[fixes]

To that end, clients only need to reference the first number in requests:

```bash
GET /articles/123 HTTP/1.1
Host: api.example.com
Accept: application/vnd.opg-data.v1+json
```

(will bring back any version from 1.0.0 to 1.9.9, whichever is the latest)

## An Exploration of Common Solutions To Versioning

### Option 1. Version in the URI (path, or param)

```bash
GET /v1/articles/123 HTTP/1.1
GET /articles/123?version=v1 HTTP/1.1
```

#### Notable users:

* Twitter, Dropbox (path)
* Amazon (query parameter)

#### Pros:

* Common convention that is simple and easy to understand
* "Copy-paste" friendly (Although no RESTful/Hypermedia API is ever going to be copy-paste friendly because there will always be headers involved)

#### Cons:

* It's not technically RESTful... a URI in REST should represent the resource only. A version is not the resource, it is an attribute of the resource
* This approach implies that an item in one version of the API is really a different resource than the same item in a different version of the API. Which is wrong.
* It forces API clients to do weird things to keep bookmarked links up to date. RESTfully, a URI to a resource should never change. If the client stores/bookmarks URI references, then wants to support an upgraded version of the API they they have a painful choice: choose to rewrite those bookmarks based on some out of band knowledge, support both the old and new version of the API, or force the user to start over from scratch.
* Not future-proof architecturally. We may choose to implement future versions of the API with a different server or codebase - which would probably mean cumbersome proxy trickery.

### Option 2. Hostname Versioning

`GET https://api-v1.example.com/articles/123`

#### Pros

* Simple and easy to understand
* Now easy to serve different versions with different servers.

#### Cons

* All the same cons as Option 1

### Option 3. Put the version in the body

```bash
POST /articles/123 HTTP/1.1

{
    "version" : "v1"
}
```

#### Notable users:

* Netflix, Paypal

This solves the problem of URLs changing over time.

It's fine if the body is JSON, but if posting with a content-type such as image/png or even text/csv then the version probably has to go back in the querystring again and you're right back with the issues above!

#### Pros

* Keeps the URL the same when the param is in the body
* A bit more RESTful than putting version in the URI

#### Cons

* No consistency about where the param is placed - Having a parameter that shifts around depending on the content-type is confusing and ugly
* Many PHP frameworks just ignore the querystring on anything other than a GET request

### Option 4. Custom Header

If the version can't go in the URI or the body, that leaves headers.

```bash
GET /articles/123 HTTP/1.1
ApiVersion: v1
Vary: ApiVersion
```

#### Notable users:

* Azure

Without the `Vary` header, it's hard for cache systems like Varnish to know that anything is different between two requests for the same resource at two different versions, and you could be served the wrong response, completely defeating the point.

#### Pros

* Quite RESTful

#### Cons

* a less common pattern which might require more explanation for developers
* Cache systems can get confused
* non-standard headers might cause trouble with firewalls

### <a name="options-5"></a> Option 5. Content negotiation using the Accept header

#### Notable users

* Github

The `Accept` header is designed to ask the server to respond with a specific resource in a different format. If we can RESTfully ask for our data to come back with different content types, then why not use the same header to ask for versions too?

It is becoming more common to recognise that a specific format of a resource is the combination of content type AND version.

This empowers the API client to tell the API what format of a resource it needs to accomplish its goal.

Thus, the client says "I need the resource at this URI, in this content type, at this version".

The API either serves it, or responds with a HTTP 415 if it can't fulfil the request.

Using content negotiation to manage versions requires the introduction of nonstandard media types. There is really no way around this. This is probably no bad thing: the new, nonstandard, media types do a much better job describing the sort of media the client is requesting.

```bash
Accept: application/json

becomes

Accept: application/vnd.opg-data.v1+json
```

#### Pros

* Simple for API consumers (if they know about headers)
* HATEOAS-friendly
* Cache-friendly
* RESTfully Keeps a URI for a resource the same
* It opens up the possibility of adding resource-specific versioning in the future, eg `application/vnd.opg-data.donor.v1+json` would be a JSON representation of a donor resource at version 1

#### Cons

* API developers must be made aware about how the Accept header is being used
* Browsers may have trouble understanding nonstandard content-types. However, browsers are almost certainly not the target consumer of the services.

## Further reading

* [https://thereisnorightway.blogspot.com/2011/02/versioning-and-types-in-resthttp-api.html](https://thereisnorightway.blogspot.com/2011/02/versioning-and-types-in-resthttp-api.html)
* [http://barelyenough.org/blog/2008/05/versioning-rest-web-services/](http://barelyenough.org/blog/2008/05/versioning-rest-web-services/)
* [https://nordicapis.com/introduction-to-api-versioning-best-practices/](https://nordicapis.com/introduction-to-api-versioning-best-practices/)
* [https://blog.restcase.com/restful-api-versioning-insights/](https://blog.restcase.com/restful-api-versioning-insights/)
* [http://barelyenough.org/blog/tag/rest-versioning/](http://barelyenough.org/blog/tag/rest-versioning/)