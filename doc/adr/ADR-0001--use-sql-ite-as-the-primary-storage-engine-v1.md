# ADR-0001: Use SQLite as the Primary Storage Engine (v1)

**Status**: Accepted
**Date**: 2025-12-22

## Context

PKMS needs a local-first, low-friction storage backend to:

* Store indexed metadata and extracted text
* Support incremental updates (upsert)
* Be portable across devices
* Require minimal operational overhead

The system is expected to evolve, but v1 prioritizes **reliability, debuggability, and simplicity** over scalability.

## Decision

Use **SQLite** as the primary persistence layer for v1.

## Rationale

* SQLite is universally available and zero-config
* Excellent fit for local-first workflows
* Supports transactional upsert semantics
* Can coexist with Python tooling naturally
* Enables inspection/debugging with standard tools

## Consequences

**Positive**:

* Simple deployment
* Easy backup and migration
* Clear data ownership (single file)

**Negative**:

* Limited concurrency
* Not designed for distributed writes

## Future Considerations

* Meilisearch / external search engines may be added later as *secondary indexes*
* SQLite remains the system of record
