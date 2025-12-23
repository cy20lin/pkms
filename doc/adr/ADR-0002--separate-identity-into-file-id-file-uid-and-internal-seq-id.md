# ADR-0002: Separate Identity into file_id, file_uid, and internal seq id

**Status**: Accepted
**Date**: 2025-12-22

## Context

PKMS manages heterogeneous resources:

* Editable files (md, odt)
* Snapshot files (html, pdf)
* Potential future replicas across devices

A single identifier is insufficient to capture:

* Human-readable continuity
* Content identity
* Database stability

## Decision

Adopt **three layers of identity**:

| Name       | Scope            | Purpose                                     |
| ---------- | ---------------- | ------------------------------------------- |
| `id`       | DB-internal      | Stable primary key                          |
| `file_id`  | User-visible     | Short ID: Human-controlled logical identity |
| `file_uid` | Content-derived  | Long ID: Detect duplicates / replicas       |

Note that the value of `file_uid` is optional for now, its purpose and implementation may change in the future.

## Rationale

* Avoids filename-based coupling
* Supports future versioning and replication
* Aligns with git-like content identity concepts

## Consequences

* Slightly more schema complexity
* Clear separation of concerns