# ADR-0021: File Identity, Revision, and HEAD Semantics

## Status

**Status**: Accepted  
**Date**: 2026-01-19

## Context

PKMS manages *files as evolving knowledge artifacts*, not as immutable blobs.

Over time, a “file” may:

- Be edited in place
- Be moved across directories or collections
- Be regenerated (e.g. odt → html → edited)
- Exist temporarily without full indexing
- Be missing from disk while still meaningful to the user

At the same time, PKMS must support:

- Stable addressing (`pkms:///file/...`)
- Search over historical content
- Recovery from partial ingestion
- Future revision history

This introduces tension between:

- **Identity** (what the file *is*)
- **Revision** (how it has changed)
- **Physical storage** (where bytes currently live)

A clear semantic separation is required before finalizing schema or ingestion behavior.

## Decision

### 1\. File Identity is logical, not physical

PKMS defines **File Identity** as a *logical, stable identifier* representing a knowledge artifact over time.

- File identity persists across:
  - Content changes
  - Location changes
  - Re-ingestion
- File identity does **not** imply current physical existence

This identity is referenced by:

```text
pkms:///file/id:<name-id>.<ext>
pkms:///file/uid:<uuid>.<ext>
pkms:///file/sha256:<hash>.<ext>   (revision-level)
```

> Identity answers:  
> **“What knowledge artifact is this?”**

### 2\. Revisions represent concrete file states

A **Revision** represents a concrete, materialized state of a file at a point in time.

A revision may differ in:

- Content (hash)
- Size
- Location (URI / filesystem path)
- Metadata extracted during ingestion
Revisions are **append-only** in principle.

> Revisions answer:  
> **“What did this file look like at that moment?”**

### 3\. HEAD defines the active revision

Each file identity MAY have one revision designated as **HEAD**.

- HEAD represents the *current active version*
- Addressing and editing resolve to HEAD by default
- Search MAY return results derived from non-HEAD revisions

HEAD is a **pointer**, not a revision itself.

### 4\. Addressing resolves via identity → HEAD → location

Resolver semantics follow a strict priority:

1. Resolve **file identity**
2. Select **HEAD revision**
3. Resolve **current physical location**

If step (3) fails:

- Resolution still succeeds **semantically**
- Resolver returns a *non-materialized* target
- System may:
  - Offer recovery
  - Fall back to cached previews
  - Indicate “file currently unavailable”

This mirrors web search behavior (“cached copy”, “previous version”).

### 5\. Search operates on revisions, not only HEAD

Full-text search and embeddings operate on **revision data**, not strictly on HEAD.

This allows:

- Searching content that existed historically
- Returning results even if the file has moved or been deleted
- Graceful degradation when current bytes are unavailable

Search results MAY annotate:

- Whether the physical file is present

### 6\. File disappearance is not identity deletion

If a file disappears from disk:

- Its identity remains
- Its revisions remain
- HEAD may become “detached” or invalid

This is not considered data loss.

Deletion is an **explicit user intent**, not an inferred filesystem event.

### 7\. Revision creation is ingestion-driven

New revisions are created by ingestion stages such as:

- Integrity stamping (hash change)
- Indexing
- Format conversion

Not every ingestion step MUST create a revision, but **revision creation is explicit**, never implicit.

### 8\. Identity creation precedes revision creation

It is valid for a file to exist with:

- Identity only (no revision yet)
- Identity + partial revision data
- Identity + full revision(s)

This supports progressive ingestion and async workflows.

## Rationale

### 1\. Separating identity from bytes prevents fragile systems

Tying identity directly to filesystem state leads to:

- Broken links
- Lost knowledge
- Over-aggressive cleanup

Logical identity decouples *meaning* from *storage*.

### 2\. HEAD as pointer enables flexibility

Using HEAD instead of “latest row wins” enables:

- Rollbacks
- Alternate active revisions
- Future branching or pinning

Without complicating early implementations.

### 3\. Search-before-edit is more important than edit-before-search

Users tolerate stale search results far more than broken links.

This model ensures:

- Search degrades gracefully
- Editing is strict and explicit
- Addressing remains predictable

### 4\. Aligns with async ingestion

Identity-first, revision-later fits naturally with:

- Light stamper → heavy stamper → indexer
- Async task queues
- Partial availability

## Consequences

### Positive

- Stable URIs
- Graceful handling of missing files
- Natural support for revisions
- Search resilience
- Clear future expansion path

### Trade-offs

- More conceptual layers
- Requires discipline in resolver and upserter logic
- Schema evolution will be needed later

These are accepted to avoid irreversible design mistakes.

## Non-Goals

This ADR does NOT define:

- Exact database tables
- How many revisions to keep
- Garbage collection policy
- UI presentation of history

These are deferred intentionally.

## Summary

**PKMS treats files as evolving knowledge artifacts.**

- Identity is stable and logical
- Revisions capture materialized states
- HEAD defines the active view
- Addressing resolves even when bytes are missing
- Search is resilient to change

This ADR establishes the semantic foundation needed for async ingestion, robust addressing, and future revision-aware features—without prematurely locking schema or implementation details.
