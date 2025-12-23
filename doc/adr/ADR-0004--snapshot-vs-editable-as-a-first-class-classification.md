# ADR-0004: Snapshot vs Editable as a First-Class Classification

**Status**: Accepted
**Date**: 2025-12-22

## Context

Not all resources should be reindexed equally:

* Snapshots rarely change
* Editable documents change frequently

## Decision

Introduce `file_kind` with semantic values:

* `snapshot`
* `editable`

## Rationale

* Enables smarter reindexing strategies
* Avoids heuristic-based detection
* Explicit is better than implicit

## Consequences

* Indexers must classify file kind
* Reindex policy can evolve independently