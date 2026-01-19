# ADR-0020: Ingestion Task Model & Observability

## Status

**Status**: Accepted  
**Date**: 2026-01-19

## Context

PKMS ingestion is responsible for transforming raw user files into addressable, searchable, and viewable knowledge artifacts.

As PKMS evolves, ingestion is no longer a single synchronous operation. Instead, it must support:

- Incremental processing (identity → integrity → indexing → enrichment)
- Asynchronous execution (background workers, file watchers)
- Explicit user intent (e.g. inbox-driven workflows)
- Partial availability (addressable before searchable)
- Failure handling without system-wide blockage

In earlier designs, ingestion was implicitly assumed to be:

> “Scan everything, process everything, block until complete.”

This approach does not scale cognitively, operationally, or ergonomically for a personal knowledge system intended for daily use.

Therefore, PKMS requires a **formal ingestion task model** with **observable state**, allowing both humans and tools to understand *what is happening right now* and *why*.

---

## Decision

### 1\. Ingestion is modeled as explicit tasks

All ingestion work SHALL be represented as **explicit tasks**, not implicit side effects.

A task represents:

- A unit of intent (“ingest this file”)
- With a defined scope (identity, integrity, indexing, etc.)
- With observable lifecycle state

Tasks MAY be created by:

- User actions (e.g. moving a file into `_INBOX`)
- File system watchers
- CLI / API triggers
- Internal scheduling logic

### 2\. Ingestion is decomposed into stages

Ingestion is **not monolithic**. It is decomposed into stages with increasing cost and capability.

At minimum, PKMS distinguishes:

| Stage          | Responsibility                            | Cost               |
| -------------- | ----------------------------------------- | ------------------ |
| **Identity**   | Extract stable identifiers (name-id, uid) | Very low           |
| **Integrity**  | File size, mtime, hashes (e.g. sha256)    | Medium             |
| **Indexing**   | Parse content, extract text, metadata     | High               |
| **Enrichment** | Embeddings, previews, derived artifacts   | Optional / Highest |

Stages are **independently schedulable** and MAY be executed out of order when safe.

### 3\. Ingestion tasks have observable state

Each ingestion task MUST expose a **well-defined state** that is inspectable.

Minimum task states:

| State       | Meaning                           |
| ----------- | --------------------------------- |
| `PENDING`   | Task accepted but not yet running |
| `RUNNING`   | Task currently executing          |
| `COMPLETED` | Task finished successfully        |
| `FAILED`    | Task failed with error            |
| `CANCELLED` | Task explicitly aborted           |

Additional domain-specific states MAY exist (e.g. `WAITING_DEPENDENCY`).

### 4\. Ingestion state must be externally inspectable

Ingestion state MUST NOT be hidden inside memory-only logic.

State MUST be observable via at least one of:

- Database records
- Filesystem artifacts (e.g. `.pkms.lock`, `.pkms.state`)
- Task registry / runtime state
- UI / CLI introspection

This enables:

- User trust (“what is the system doing?”)
- Debuggability
- Recovery from crashes
- Restartable ingestion

The exact storage mechanism is an implementation detail, but **observability is mandatory**.

---

### 5\. Inbox-based ingestion expresses user intent

PKMS introduces **explicit ingestion zones**, such as:

- `_INBOX/`
- `_PENDING/`
- `_REJECTED/`

Placing a file into `_INBOX` expresses **explicit user intent**:

> “This file should be ingested now.”

This design ensures:

- Ingestion does not need to “scan the world” by default
- User intent is visible and reversible
- File watchers and schedulers can prioritize correctly

Files outside these zones are not ignored, but are treated as **lower priority** or **background candidates**.

### 6\. Skipping is not failure

A file may be **skipped** for ingestion reasons such as:

- Already ingested and unchanged
- Lower priority than active tasks
- Awaiting user action or normalization

Skipping MUST be explicit and explainable.

Skipping does NOT imply:

- Rejection
- Error
- Loss of knowledge

It only means:

> “This is not the current ingestion priority.”

### 7\. Partial ingestion is a first-class outcome

A file MAY exist in PKMS with only partial ingestion completed.

Examples:

- Identity ingested → addressable
- Identity + indexing ingested → searchable
- Identity + indexing + preview → viewable

This directly supports the resolver semantics defined in ADR-0019.

### 8\. Ingestion failures are localized and recoverable

Failure of one ingestion task MUST NOT:

- Block other tasks
- Corrupt existing records
- Break addressing or historical knowledge

Failures should result in:

- Explicit FAILED state
- Diagnostic information
- Optional relocation (e.g. `_REJECTED/`)
- Clear recovery path


### 9\. Ingestion is decoupled from schema finalization

The ingestion task model MUST remain stable even as:

- Database schema evolves
- Revision support is introduced
- Async execution model changes

Tasks describe **intent and progress**, not schema structure.

## Rationale

### 1\. Observability builds trust

Users trust systems they can *see*.

A silent background process that “might be doing something” creates anxiety and friction.

Explicit tasks turn ingestion into a cooperative process rather than a black box.

### 2\. Intent-first design matches human workflows

Humans think in actions:

> “I want this file ingested now.”

—not—

> “Please reconcile filesystem state with database invariants.”

Inbox-based workflows align system behavior with human intent.

### 3\. Progressive capability beats all-or-nothing

Addressing before indexing, indexing before enrichment—this progression ensures:

- Fast feedback
- Early usefulness
- Graceful degradation

This is critical for large or slow-to-process files.

### 4\. Async-first prevents future architectural pain

Designing ingestion as task-based from the beginning avoids:

- Forced refactors
- Blocking UI
- Hard-to-debug race conditions

Async is not an optimization—it is a correctness requirement for PKMS.

## Consequences

### Positive

- Clear mental model for ingestion
- Debuggable, inspectable system
- Natural support for async workers
- Strong alignment with user intent
- Foundation for future automation

### Trade-offs

- More moving parts
- Requires task registry or state storage

- Slightly higher implementation complexity

These costs are accepted to avoid long-term brittleness.

---

## Non-Goals

This ADR does NOT specify:

- Exact queue implementation
- Threading vs asyncio vs multiprocessing
- UI representation details
- Database schema layout

These are implementation choices guided—but not dictated—by this ADR.

---

## Summary

**Ingestion in PKMS is an observable, intent-driven, task-based process.**

By modeling ingestion as explicit tasks with visible state, PKMS ensures that:

- Users understand what the system is doing
- Partial progress is valuable
- Failures are local and recoverable
- Addressing and searching remain robust

This ADR establishes ingestion as a *first-class, inspectable subsystem* rather than a background side effect.
