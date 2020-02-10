# 9. API Domain Structure

Date: 2020-02-03

## Status

Proposed

## Context

We need to establish a domain structure which

* Is product agnostic
* Is consistent across the opg-data service

## Decision

We will adopt the pattern:

https://[pr].[env].[integration].[api-domain]

### examples

#### root:

* https://api.opg.service.justice.gov.uk

#### integration:

* https://deputy-reporting.api.opg.service.justice.gov.uk

#### environments per integration:

* https://pre.deputy-reporting.api.opg.service.justice.gov.uk
* https://dev.deputy-reporting.api.opg.service.justice.gov.uk

#### pr raised on an environment per integration:

* https://pr-1234.dev.deputy-reporting.api.opg.service.justice.gov.uk

## Consequences
