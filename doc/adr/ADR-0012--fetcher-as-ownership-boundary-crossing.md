# ADR-0012: Fetcher as Ownership Boundary Crossing

**Status**: Accepted
**Date**: 2025-12-24

## Context

The PKMS system interacts with resources hosted across different systems,
some of which are not controlled or trusted by the PKMS operator.

Directly indexing or operating on such resources introduces instability,
availability risks, and unclear ownership semantics.

A clear architectural boundary is required to separate trusted and untrusted
resources.

## Decision

The PKMS system SHALL treat the Fetcher component as the exclusive mechanism
for crossing the Ownership Boundary.

- Fetchers operate on External Resources
- Fetchers produce Owned Resources
- Core PKMS pipelines operate only on Owned Resources

## Rationale

- Enforces a clear trust boundary
- Prevents indexing unstable or mutable external systems
- Enables reproducibility and offline operation
- Aligns with snapshot-based knowledge management

## Consequences

- All ingestion pipelines assume Owned Resources as input
- Fetchers may be triggered manually or via scheduler
- External systems are never directly indexed