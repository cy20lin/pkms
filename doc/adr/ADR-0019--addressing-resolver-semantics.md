# ADR-0019: Addressing & Resolver Semantics

## Status

**Status**: Accepted  
**Date**: 2026-01-19

## Context

PKMS provides a custom URI scheme (`pkms:///`) to **address**, **resolve**, and **reference** knowledge artifacts (files, documents, revisions) managed by the system.

Addressing is a **foundational capability** of PKMS and must remain reliable even when:

- Ingestion is incomplete
- Indexing has not yet occurred
- Files have been moved, renamed, or deleted
- Historical data exists but current content is unavailable

In earlier iterations, addressing and searching were implicitly coupled, often assuming:

> “If something cannot be indexed or searched, it effectively does not exist.”

This assumption breaks down for long-lived knowledge systems, where **identity and reference stability** must outlive storage layout, ingestion state, and indexing availability.

Therefore, PKMS requires a **clear semantic separation** between:

- **Addressing** (resolving “what is this?”)
- **Searching** (finding things by content or metadata)
- **Viewing / Editing** (interacting with current file content)

This ADR defines the **semantic contract** of addressing and resolution in PKMS.

## Decision

### 1\. Addressing is identity-based, not content-based

PKMS addressing resolves **file identity**, not guaranteed file existence or freshness.

A PKMS URI identifies:

- A **logical knowledge artifact**
- With a stable selector (`id`, `uid`, `sha256`, `isbn`, etc.)
- Independent of current file location or ingestion completeness

Resolution answers:

> “What does PKMS know about this identifier right now?”

—not—

> “Is this file currently present and editable?”

### 2\. Resolver MUST operate with partial ingestion data

The resolver MUST function correctly when only a subset of ingestion capabilities is available.

Resolver input MAY resolve successfully with only:

- Identity data (e.g. `id`, `uid`)
- Historical metadata
- Cached or stale records

Resolver MUST NOT require:

- Indexing
- Full-text content
- File readability
- Current filesystem presence

### 3\. Resolution outcomes are graded, not binary

Resolution is **not** a boolean success/failure operation.

The resolver MUST be able to distinguish at least the following outcomes:

| Category | Meaning |
| --- | --- |
| **Resolved (Current)** | Identity exists and current location is known |
| **Resolved (Historical)** | Identity exists, but file is missing or moved |
| **Resolved (Partial)** | Identity exists, but metadata is incomplete |
| **Not Found** | Identity has never existed in PKMS |
| **Conflict** | Identity exists but integrity checks contradict expectations |

These outcomes are **semantic results**, not exceptions.

Exceptions are reserved for:

- Invalid URI syntax
- Unsupported schemes or selectors

### 4\. Addressing is independent of searching

The resolver MUST NOT depend on:

- Full-text search (FTS)
- Embedding or vector indexes
- Indexing completion

Conversely:

- Search results MAY include records that are no longer addressable for editing
- Search results MAY reference historical or partial records

This mirrors real-world systems such as:

- Web search caches
- Versioned documentation
- Archival knowledge bases

### 5\. Resolver returns “best-known facts”

Resolver output MUST represent **best-known information**, not guarantees.

A resolved target may include:

- Identity
- Last known URI
- Known capabilities
- Known metadata (title, kind, timestamps)
- Indicators of staleness or incompleteness

Example (conceptual):

```python
ResolvedTarget(
    identity="id:2000-01-01-0001",
    file_uri="file:///path/to/old/location",
    available_capabilities=["identity", "index"],
    is_current=False,
)
```

The resolver does **not** attempt to repair, re-ingest, or relocate content.

### 6\. Editing requires stronger guarantees than resolving

Addressing alone does NOT imply editability.

Editing requires:

- Successful addressing
- AND current file availability
- AND integrity expectations met

Therefore:

- A URI may resolve successfully
- But still be non-editable

This distinction is intentional and visible to users.

### 7\. Addressing is stable across ingestion evolution

Resolver semantics MUST remain stable even as:

- Ingestion becomes asynchronous
- Schema evolves
- New capabilities (revisions, embeddings) are introduced

The resolver contract is **forward-compatible**:

> Future ingestion improvements may enhance resolution quality,  
> but must not break existing resolution semantics.

## Rationale

### 1\. Addressing is the backbone of trust

If users cannot rely on references remaining meaningful over time, the system fails its core purpose as a knowledge system.

Even incomplete or stale resolution is preferable to silence or failure.

### 2\. Partial knowledge is still knowledge

PKMS explicitly embraces partial truth:

- A file that “once existed” still has value
- Historical metadata is better than absence
- Stale content is acceptable for search and recall

This aligns with how human memory and real-world archives work.

### 3\. Separating concerns prevents cascading failures

Coupling resolver logic to indexing or ingestion creates failure chains:

> “Indexing failed → resolver fails → links break → system feels unreliable”

Decoupling ensures failures are **localized and explainable**.

### 4\. Users care about intent, not pipeline internals

From the user’s perspective:

- “I know this thing exists”
- “I want to find it”
- “I want to edit it”

These are distinct intents and must not collapse into one brittle operation.

## Consequences

### Positive

- Stable long-term links
- Graceful degradation
- Clear separation of responsibilities
- Better UX for partial or async ingestion
- Enables historical views and revision tracking

### Trade-offs

- Resolver logic becomes more nuanced

- UI must communicate resolution state clearly

- Requires discipline to avoid shortcut assumptions in other components

These trade-offs are accepted to preserve correctness and long-term usability.

## Non-Goals

This ADR does NOT specify:

- How ingestion is scheduled
- How indexing is implemented
- How files are repaired or re-ingested
- How revisions are stored

These are addressed in separate ADRs.

## Summary

**Addressing in PKMS is a semantic contract, not a filesystem lookup.**

The resolver answers:

> “What does PKMS know about this identifier?”

—not—

> “Is this file immediately usable?”

By explicitly embracing partial knowledge, historical truth, and graded resolution, PKMS ensures that its knowledge graph remains coherent, trustworthy, and resilient over time.
