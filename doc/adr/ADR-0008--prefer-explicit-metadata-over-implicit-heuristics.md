# ADR-0008: Prefer Explicit Metadata Over Implicit Heuristics

**Status**: Accepted
**Date**: 2025-12-22

## Context

Implicit inference (e.g. guessing title, mutability, importance) is fragile.

## Decision

Prefer:

* Explicit fields (`title`, `importance`, `file_kind`)
* Deterministic fallbacks

## Rationale

* Predictability
* Easier debugging
* Future automation-friendly

## Consequences

* Some fields may be imperfect initially
* Can be refined incrementally