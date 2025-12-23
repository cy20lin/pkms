# ADR-0005: Use URI Instead of Path in Persistent Models

**Status**: Accepted
**Date**: 2025-12-22

## Context

PKMS resources may:

* Reside locally
* Be accessed remotely in the future
* Be referenced by non-file schemes

## Decision

Persist **URIs**, not raw filesystem paths:

* `file_uri`
* `origin_uri`

## Rationale

* URI is a superset of URL and URN
* Avoids early commitment to http/file semantics
* Enables future scheme handlers (e.g. `pkms://`)

## Consequences

* Slightly more verbose representation
* Requires normalization discipline