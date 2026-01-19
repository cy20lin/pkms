# ADR-0018: Ingestion State Model and Capability-Based Ingestion

## Status

**Status**: Accepted  
**Date**: 2026-01-19

## Context

PKMS manages user-owned files as long-lived knowledge artifacts.  
Files may be large, heterogeneous (Markdown, ODT, HTML, binary), and continuously evolving.

A naive ingestion model that assumes:

- synchronous processing
- full indexing before visibility
- world-scanning on every run

creates unacceptable trade-offs in usability, performance, and correctness.

Instead, PKMS must support:

- **Incremental ingestion**
- **Asynchronous execution**
- **Observable intermediate states**
- **Graceful degradation of capabilities**

This ADR defines a **capability-based ingestion state model**, which separates *what the system knows* from *what the system can currently do* with a file.

---

## Problem Statement

Ingestion in PKMS must satisfy the following constraints:

1. Users must be able to **express intent explicitly** (e.g. via filesystem actions).
2. The system must **not block globally** on slow operations (hashing, parsing).
3. Partial progress must be **observable and meaningful**.
4. Addressing (URI resolution) must work **before full indexing completes**.
5. Search and editing must **degrade safely** when ingestion is incomplete.
6. Schema evolution must be possible without invalidating earlier design decisions.

A binary “ingested / not ingested” model is insufficient.

## Decision

PKMS ingestion SHALL be modeled as **accumulation of capabilities**, not as a single linear pipeline.

A file is considered *known to the system* as soon as **identity capability** is established.  
Additional ingestion work progressively unlocks more system capabilities.

Ingestion is:

- **Asynchronous**
- **Task-based**
- **Inspectable**
- **Prioritized by user intent**

## Core Concepts

### 1\. Ingestion ≠ Indexing

Ingestion is a **superset** of indexing.

Indexing is only one possible ingestion capability and is not required for addressing or basic system awareness.

### 2\. Capability-Based Ingestion Model

Each file accumulates ingestion **capabilities** independently.

| Capability | Description | Enables |
| --- | --- | --- |
| Identity | Stable identifier(s) discovered | Addressing (URI resolution) |
| Stat | Filesystem metadata (mtime, size, ctime) | Change detection |
| Integrity | Content-derived identity (sha256, blake3) | Deduplication, history |
| Index | Parsed semantic content (text, structure) | Full-text search |
| View | Rendered representation (HTML, preview) | Human reading |

Capabilities are **orthogonal** and **monotonic** (once achieved, never silently removed).

There is no single `status = INGESTED`.

Instead, a file exists in a **capability lattice**:

- A file with `identity` exists for addressing
- A file with `identity + index` exists for search
- A file with historical capabilities may remain resolvable even if its physical location changes

The system must be able to answer:

> “What do we currently know about this file?”

## User Intent and Priority

### Inbox-Driven Ingestion

PKMS uses **filesystem semantics** to capture explicit user intent.

Example:

```
collection/
├── _INBOX/
│   └── note.odt
├── _REJECTED/
├── _PENDING/
```

Placing a file into `_INBOX/` indicates:

- High priority ingestion
- Explicit user intent
- Eligibility for immediate processing

This avoids global scanning and reduces ambiguity.

### Skip vs Defer

PKMS does **not skip ingestion silently**.

Instead:

- Tasks may be **deferred**
- Capabilities may be **pending**
- Progress must be **inspectable**

A file that is not fully ingested is still *present* in the system with reduced capabilities.

## Addressing Semantics

### Addressing Is Capability-Aware

Addressing (`pkms:///file/...`) operates on **identity capability only**.

Implications:

- A file may be resolvable even if:
  - Indexing is incomplete
  - The file has moved
  - The file has been deleted
- Addressing returns the **best-known fact**, not a guarantee of editability

This enables:

- Historical references
- Search result stability
- Non-blocking UX

Editing requires additional checks beyond addressing.

## Failure Modes

### Resolver Outcomes

| Situation | Resolver Result |
| --- | --- |
| Identity known, file missing | Historical record returned |
| Identity unknown | Not found |
| Identity known, integrity mismatch | Conflict / revision |
| Identity known, ingestion pending | Partial resolution |

Failures are **explicit states**, not silent errors.

## Observability Requirements

Ingestion MUST be observable:

- Task-level progress
- Capability-level completion
- Failure reasons

Observation mechanisms may include:

- Filesystem markers
- Database state
- UI indicators
- CLI inspection tools

The exact mechanism is an implementation detail.

## Relationship to Schema

Schema design SHALL:

- Allow partial population
- Avoid premature normalization
- Support future revision history

Schema finalization is **explicitly deferred** until ingestion semantics stabilize.

## Non-Goals

This ADR does **not** mandate:

- A specific task queue implementation
- A specific UI
- A specific storage backend
- Immediate revision support

These are deferred design decisions.

## Consequences

### Positive

- Clear separation of concerns
- Non-blocking ingestion
- Honest system behavior
- Strong alignment with user intent
- Future-proof schema evolution

### Trade-offs

- Increased conceptual complexity
- Requires careful tooling and documentation
- Partial visibility may confuse untrained users (acceptable for PKMS audience)

## Summary

PKMS ingestion is defined as a **progressive accumulation of knowledge about files**, not a binary state.

This model:

- Enables async processing
- Preserves addressing correctness
- Supports future revision and history
- Keeps the system honest about what it knows

Ingestion is observable, incremental, and user-intent-driven.
