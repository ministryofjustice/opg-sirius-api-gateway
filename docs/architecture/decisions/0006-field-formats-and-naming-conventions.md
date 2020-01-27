# 6. Field Formats And Naming Conventions

Date: 2020-01-27

## Status

Proposed

## Context

We desire consistency across the API, so should provide a set of sensible naming conventions which we will adhere to and require our clients to do likewise

## Decision

### Naming conventions

Our field naming standard is closely follows the [JSON API](https://jsonapi.org/format/#document-member-names) v1.0 definition, and this spec should be consulted for a full list of allowed, disallowed, and reserved characters.

In brief, field names:

* Are case sensitive
* Must contain at least one character, and begin with an a character
* Use only [non-reserved](https://jsonapi.org/format/#document-member-names-reserved-characters), URL-safe characters

The following additional standards are also in force in `application/vnd.opg-data.v1`:

* Field names are all lower case
* Must begin with an an alpha chatacter [a-z]
* We use an underscore to separate compound field names
* U+0020 SPACE, “ “ is not permissible in a field name

### Field data formats

* integers are integers
* boolean are represented by `true` and `false`
* null values are represented by `null`
* empty arrays are always shown, represented by `[]`

```json
{
    "data": {
        "id": "123XYZalways_a_string",
        "integer": 1,
        "string": "Like so",
        "boolean": true,
        "boolean": false,
        "explicit_empty_arrays_are_shown": [],
        "explicit_null_for_everything_else": null,
        "use_underscores_in_naming": true,
        "fields_all_lower_case": true,
        "fields_Are_Case_Sensitive": true
    }
}
```

## Consequences

Consistency is greatly improved
