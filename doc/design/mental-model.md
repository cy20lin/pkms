# PKMS Mental Model

## Table of Content

- [PKMS Mental Model](#pkms-mental-model)
  - [Table of Content](#table-of-content)
  - [Purpose](#purpose)
  - [High-Level View](#high-level-view)
  - [Core Concepts](#core-concepts)
    - [Resource](#resource)
    - [Owned Resource](#owned-resource)
    - [External Resource](#external-resource)
    - [Ownership Boundary](#ownership-boundary)
  - [Capability Breakdown](#capability-breakdown)
    - [1. Acquisition](#1-acquisition)
    - [2. Ingestion](#2-ingestion)
    - [3. Retrieval](#3-retrieval)
    - [4. Knowledge Linking](#4-knowledge-linking)
    - [5. Addressing \& Presentation](#5-addressing--presentation)
      - [Addressing / Resolution](#addressing--resolution)
      - [Presentation](#presentation)
  - [Separation of Concerns](#separation-of-concerns)
  - [Mental Model Overview](#mental-model-overview)
  - [Design Philosophy](#design-philosophy)
  - [Non-Goals (For Now)](#non-goals-for-now)
  - [Related Documents](#related-documents)

## Purpose

This document describes the **mental model** of the PKMS system.  
It explains *what the system is responsible for*, *how responsibilities are separated*, and *how different parts conceptually fit together*.

This document is intended for:

- Contributors who want to understand the system architecture
- LLM agents working on this repository
- Future maintainers revisiting design decisions

This is **not** an implementation guide.  
Detailed interfaces and schemas are defined elsewhere.

## High-Level View

At a high level, PKMS is a system that:

> **Acquires resources, ingests them into structured knowledge, enables retrieval, maintains relationships, and presents resources to humans and tools.**

This can be expressed as five core capabilities:

```text
Acquisition
   ↓
Ingestion
   ↓
Retrieval
   ↓
Knowledge Linking
   ↓
Addressing & Presentation
```

Each capability is conceptually independent and loosely coupled.

## Core Concepts

### Resource

A **Resource** is any piece of information PKMS manages.

Examples:

- HTML files
- Markdown documents
- PDFs
- Audio / video files
- Images
- Conversations fetched from remote services

A Resource may exist:

- As a local file
- As a snapshot of a remote system
- As a derived artifact

A Resource has:

- Identity (`file_id`, `file_uid`)
- Location (`file_uri`)
- Metadata
- Content (optional or extracted)

### Owned Resource

An **Owned Resource** is a resource stored in a storage system that PKMS fully trusts and controls.

Characteristics:

- Full read/write access
- Stable availability
- Deterministic re-processing
- Considered authoritative input for ingestion

Examples:

- Files in a user-controlled filesystem
- Files stored in a trusted, user-managed cloud storage
- Snapshots persisted locally after acquisition

PKMS **only ingests Owned Resources**.

### External Resource

An **External Resource** is a resource that exists outside PKMS’s ownership boundary.

Characteristics:

- Not fully trusted
- Not fully controlled
- May change without notice
- Access governed by external systems

Examples:

- Web pages on public websites
- Telegram conversations on Telegram servers
- SaaS-hosted documents

PKMS **never indexes External Resources directly**.

### Ownership Boundary

The **Ownership Boundary** is the most fundamental conceptual boundary in PKMS.

It separates:

- **External Resources** → not trusted, not indexed
- **Owned Resources** → trusted, ingestible, indexable

Crossing this boundary always requires an explicit operation.

## Capability Breakdown

### 1\. Acquisition

**Acquisition** brings resources from external systems into local storage.

Examples:

- Downloading web pages
- Fetching Telegram conversations
- Syncing remote folders
- Scheduled data collection

Key properties:

- External → Local
- Side-effect: creates or updates files
- Triggered manually or by scheduler (future)

Conceptually implemented by:

- Fetchers
- Schedulers
- Policies

Acquisition **does not index** or interpret content.

### 2\. Ingestion

**Ingestion** transforms local resources into indexed knowledge.

This is the core pipeline currently implemented in PKMS:

```text
Globber → Indexer → Upserter
```

- **Globber**: discovers files
- **Indexer**: extracts structured data
- **Upserter**: persists indexed data into storage (SQLite)

Key properties:

- Deterministic
- Re-runnable
- Config-driven
- Content-type aware

Ingestion defines the **stable contract boundary** of the system:  
`IndexedDocument`.

### 3\. Retrieval

**Retrieval** provides read-only access to indexed knowledge.

Examples:

- Full-text search
- Metadata filtering
- Future: semantic search
- Future: graph traversal

Key properties:

- No side effects
- Query-only
- Operates on indexed data, not raw files

Retrieval is intentionally separated from presentation or UI concerns.

### 4\. Knowledge Linking

**Knowledge Linking** manages explicit relationships between resources.

This layer models PKMS as a **knowledge graph**, not just a document store.

Examples:

- Resource A references Resource B
- Snapshot derived from another resource
- Multiple files represent the same conceptual entity

Conceptually:

```scss
(Resource) --[RelationType]--> (Resource)
```

Key properties:

- Typed relations
- Directional or bidirectional
- Stored and queryable
- Independent from file location

Knowledge linking is **not about opening files or URLs**.

### 5\. Addressing & Presentation

**Addressing & Presentation** connects PKMS resources to humans and external systems.

This includes:

#### Addressing / Resolution

- `pkms://` URIs
- Mapping logical identity → concrete action
- URI / URL handlers

#### Presentation

- Opening resources in a browser
- Viewing text or media
- Redirecting to external applications

Conceptual flow:

```text
PKMS URI
  ↓
Resolver
  ↓
Handler
  ↓
Action (open / view / edit / navigate)
```

This layer integrates PKMS with:

- OS
- Browsers
- Editors
- External tools

## Separation of Concerns

The PKMS mental model emphasizes **clear boundaries**:

| Layer                     | Responsibility                     |
| ------------------------- | ---------------------------------- |
| Acquisition               | Get data, Cross ownership boundary |
| Ingestion                 | Understand owned data              |
| Retrieval                 | Query indexed data                 |
| Knowledge Linking         | Relate data                        |
| Addressing & Presentation | Use data                           |

Each layer:

- Evolves independently
- Has explicit contracts
- Avoids leaking responsibilities

---

## Mental Model Overview

1. External Resources exist outside the PKMS trust boundary
2. Fetchers acquire External Resources and store them as Owned Resources
3. Ingestion pipelines operate only on Owned Resources
4. Indexed Documents form a stable contract for search, linking, and viewing

The PKMS system never directly indexes External Resources.
All indexing is performed on Owned Resources only.

## Design Philosophy

- **Configuration over code**
- **Explicit metadata over heuristics**
- **Stable contracts between subsystems**
- **Filesystem as a first-class boundary**
- **URI-based addressing, not implicit paths**

## Non-Goals (For Now)

- Real-time synchronization
- Automatic semantic inference
- Opinionated UI workflows
- Tight coupling to specific external services

## Related Documents

- `doc/design/pkms.md`
- `doc/design/use-cases.md`
- `doc/design/glossary.md`
- `doc/design/pkms-abstract-interfaces.md`
- `doc/adr/ADR-0003--treat-indexed-document-as-a-stable-contract-boundary.md`
- `doc/adr/ADR-0011--terminology-owned-resource-vs-external-resource.md`
- `doc/adr/ADR-0012--fetcher-as-ownership-boundary-crossing.md`
