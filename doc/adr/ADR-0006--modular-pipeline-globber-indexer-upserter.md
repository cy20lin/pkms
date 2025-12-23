# ADR-0006: Modular Pipeline (Globber → Indexer → Upserter)

**Status**: Accepted
**Date**: 2025-12-22

## Context

PKMS must support:

* Multiple file types
* Different indexing strategies
* Incremental evolution

## Decision

Adopt a **three-stage pipeline**:

1. Globber – discover resources
2. Indexer – transform resource → IndexedDocument
3. Upserter – persist IndexedDocument

## Rationale

* Clear responsibility boundaries
* Testability
* Configuration-driven extensibility

## Consequences

* Slightly more boilerplate
* Long-term maintainability gain
