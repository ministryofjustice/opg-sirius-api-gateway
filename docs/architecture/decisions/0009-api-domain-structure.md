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

[account-type].[api-domain]/[restapi-name]

#### [account-type]

* dev
* preprod
* prod

#### [api-domain]

* api.sirius.opg.digital

#### examples

* https://dev.api.sirius.opg.digital/health
* https://preprod.api.sirius.opg.digital/health
* https://api.sirius.opg.digital/health

## Consequences
