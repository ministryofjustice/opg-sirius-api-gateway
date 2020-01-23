# 4. Content Negotiation

Date: 2020-01-22

## Status

Proposed

## Context

The `Accept` header is designed to ask the server to respond with a specific resource in a different format. If we can RESTfully ask for our data to come back with different content types, then why not use the same header to ask for versions too?

It is becoming more common to recognise that a specific format of a resource is the combination of content type AND version.

## Decision

For the reasons explored in [2. API versioning strategy](0002-api-versioning-strategy.md), 
* We will implement versioning via the Content Negotiation using the Accept header, as per option 5, below. This seems the most future proof, most RESTful solution.
* This necessitates our own vendor content type. Examples:
  * `application/vnd.opg-data.v1+json` (v1 presented as JSON)
  * `application/vnd.opg-data.v1+yml` (v1 presented as YAML)
  * `application/vnd.opg-data.v1` (v1 presented as JSON)
  * `application/vnd.opg-data` (latest version, presented as JSON)
  * `application/json` (latest version, as JSON)

## Consequences

What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated.

## Note

As detailed in [OPG-Data API Specification](0003-opg-data-api-specification.md), our API specification borrows heavily from the [JSON-API](http://jsonapi.org/format/). Where our documentation does not specify otherwise, it should be assumed that the JSON:API standard applies.