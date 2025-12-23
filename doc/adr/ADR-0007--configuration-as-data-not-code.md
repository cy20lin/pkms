# ADR-0007: Configuration as Data, Not Code

**Status**: Accepted
**Date**: 2025-12-22

## Context

Users may want:

* Different collections
* Different indexers
* Different base paths

## Decision

All behavior is driven by a **versioned config file**, validated by pydantic v2.

## Rationale

* Reproducibility
* Clear contracts
* Easier automation and tooling

## Consequences

* Config schema must be carefully versioned
* Migration may be needed across versions