
# ADR-0022: Introduce Stamper for Progressive File Metadata Extraction

## Status

**Status**: Accepted  
**Date**: 2026-01-19

## Context

PKMS manages files through an ingestion pipeline that supports:

- Stable addressing (URI resolution)
- Search and preview
- Asynchronous, observable ingestion
- Incremental enrichment of metadata

Initially, several responsibilities were conflated inside the **Screener** and **Indexer**, including:

- Extracting identifiers from filenames
- Reading filesystem metadata
- Computing file hashes
- Preparing metadata required for addressing and search

This coupling led to multiple issues:

- Ingestion stages were not clearly separable
- Fast operations (e.g. filename parsing) were delayed by slow ones (e.g. hashing)
- Addressing and search readiness were tightly coupled
- It was difficult to reason about partial ingestion states
- Re-ingestion or selective updates were hard to implement cleanly

To support **progressive ingestion**, **async tasking**, and **clear responsibility boundaries**, PKMS introduces a dedicated concept: **Stamper**.

## Decision

PKMS SHALL introduce a **Stamper** component responsible for extracting and updating **file stamps** — structured metadata derived from files — independent of screening and indexing.

A **Stamp** represents metadata produced by one or more stampers and may be populated incrementally over time.

Stampers are:

- **Pure metadata extractors**
- **Side-effect free** (no indexing, no DB writes by default)
- **Composable and incremental**
- **Order-agnostic** unless explicitly constrained

Stampers operate as part of the ingestion pipeline and may run asynchronously with different priorities.

## Responsibilities

### Stamper Responsibilities

A Stamper MAY:

- Read filenames
- Read filesystem metadata (size, mtime, ctime)
- Read file contents if required
- Compute content hashes (e.g. SHA-256, BLAKE3)
- Extract embedded metadata (frontmatter, ODT metadata, etc.)

A Stamper MUST NOT:

- Perform screening decisions
- Perform indexing or parsing for search
- Write directly to persistent storage
- Assume other stampers have already run (unless declared)

### Examples of Stampers

| Stamper              | Responsibility                               |
| ---                  | ---                                          |
| `NameIdentityStamper`| Extract name-based ID from filename          |
| `StatStamper`        | size, mtime, ctime, inode                    |
| `IntegrityStamper`   | size, sha256, blake3                         |
| `MetadataStamper`    | uid, title from embedded metadata            |
| `ContentHintStamper` | lightweight content signals (language, mime) |

## FileStamp Model

A **FileStamp** is a composite structure that may include:

- Identity fields (name-id, uid)
- Integrity fields (hashes)
- Filesystem fields
- Provenance fields (collection, relative path)
- Derived hints

FileStamp is **progressively filled** as stampers complete.

Not all fields are required for all system capabilities.

| Capability | Required Stamp Fields      |
| ---        | ---                        |
| Addressing | name-id OR hash            |
| Resolver   | identity + location        |
| Search     | indexed text (later stage) |
| Integrity  | size and hashes            |

## Relationship to Other Components

### Screener

- Screener consumes **FileStamp**
- Makes admission decisions based on stamp data
- No longer responsible for extracting metadata

### Indexer

- Indexer consumes **admitted files**
- Operates after sufficient stamps exist
- Focused on parsing and content transformation only

### Upserter

- Writes stamp and index results to storage
- May update partial records incrementally

### Ingestion Pipeline

```text
File → Stampers (fast → slow)
     → Screener
     → Indexer
     → Upserter
```

Each stage is independently observable and schedulable.

## Rationale

### 1\. Progressive Ingestion

Separating stampers enables:

- Early addressing before indexing
- Partial system visibility
- Better UX for long-running ingestion

### 2\. Performance and Prioritization

- Fast stampers can run immediately (filename, stat)
- Expensive stampers can be deferred or throttled
- Async queues can prioritize by stamper type

### 3\. Clear Mental Model

Stampers answer:

> “What can we know about this file **without deciding anything yet**?”

This simplifies reasoning and debugging.

### 4\. Future Extensibility

- New stampers can be added without changing screeners or indexers
- Supports revision tracking and re-stamping
- Enables selective re-ingestion (e.g. recompute hashes only)

## Consequences

### Positive

- Cleaner separation of concerns
- Better async ingestion model
- Clear ingestion state visibility
- More resilient addressing semantics

### Trade-offs

- More components to reason about
- Requires explicit orchestration
- Slightly higher conceptual overhead

This trade-off is accepted in favor of long-term maintainability and correctness.

## Non-Goals

This ADR does NOT:

- Define exact DB schema
- Mandate specific stamp fields
- Specify task scheduling policy
- Solve access control or encryption

These concerns are handled by separate ADRs.

## Summary

Introducing **Stamper** formalizes a missing layer in PKMS:

> **Metadata before meaning, facts before decisions.**

It enables PKMS to ingest files progressively, observably, and safely — while keeping addressing, screening, and indexing decoupled.
