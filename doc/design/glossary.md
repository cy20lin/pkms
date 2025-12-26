# PKMS Glossary

This glossary defines **canonical terms** used throughout the PKMS project.  
Terms are written to establish **shared mental models** and **stable vocabulary** across design documents, ADRs, code, and future discussions.

## Table of Contents

- [PKMS Glossary](#pkms-glossary)
  - [Table of Contents](#table-of-contents)
  - [Core Concepts](#core-concepts)
    - [PKMS (Personal Knowledge Management System)](#pkms-personal-knowledge-management-system)
  - [Resource \& Ownership](#resource--ownership)
    - [Resource](#resource)
    - [Owned Resource](#owned-resource)
    - [External Resource](#external-resource)
    - [Resource Storage](#resource-storage)
    - [Resource Collection](#resource-collection)
  - [Lifecycle \& Processes](#lifecycle--processes)
    - [Resource Acquisition](#resource-acquisition)
    - [Fetcher](#fetcher)
    - [Scheduler](#scheduler)
    - [Resource Ingestion](#resource-ingestion)
    - [Ingestion Pipeline](#ingestion-pipeline)
    - [Globber](#globber)
    - [Indexer](#indexer)
    - [Upserter](#upserter)
  - [Data Models \& Identity](#data-models--identity)
    - [IndexedDocument](#indexeddocument)
    - [FileLocation](#filelocation)
    - [file\_id](#file_id)
    - [file\_uid](#file_uid)
    - [Internal Sequence ID](#internal-sequence-id)
  - [Classification \& Semantics](#classification--semantics)
    - [Snapshot](#snapshot)
    - [Editable Resource](#editable-resource)
  - [Retrieval \& Knowledge](#retrieval--knowledge)
    - [Searcher](#searcher)
    - [Knowledge Linking](#knowledge-linking)
    - [Relation Graph](#relation-graph)
  - [Resolution Layer](#resolution-layer)
    - [Resolution](#resolution)
    - [Resolver](#resolver)
    - [PKMS URI](#pkms-uri)
    - [URI Resolver](#uri-resolver)
    - [Representation](#representation)
    - [Preview Representation](#preview-representation)
    - [Viewer](#viewer)
    - [Browser Viewer](#browser-viewer)
    - [Native Viewer](#native-viewer)
    - [Handler](#handler)
  - [Architecture \& Design](#architecture--design)
    - [Configuration as Data](#configuration-as-data)
    - [Contract Boundary](#contract-boundary)
    - [Local-First](#local-first)
  - [Notes](#notes)

## Core Concepts

### PKMS (Personal Knowledge Management System)

A local-first system for acquiring, storing, indexing, searching, linking, and viewing personal resources in a structured and evolvable way.

PKMS treats **filesystem-stored resources** as first-class citizens and builds structured knowledge on top of them.

## Resource & Ownership

### Resource

A Resource represents any unit of information entity that can be acquired, indexed,
searched, linked, or viewed by the PKMS system.

Examples:

- HTML snapshot webpage
- Markdown note
- PDF
- Audio / video file
- Chat conversation snapshot
- Image
- Git Repo

A resource:

- Exists physically in storage (e.g. filesystem)
- May be indexed, searched, linked, and viewed
- May have multiple representations or versions

### Owned Resource

An Owned Resource is a resource whose storage and lifecycle are fully controlled
by the PKMS operator.

Ownership implies:

- Full read and write access
- Authority over creation, update, deletion, and backup
- Trust in data integrity and availability
- Responsibility for failure handling

Owned Resources may reside on:

- Local filesystems
- User-managed or team-managed servers
- Rented or managed cloud storage services

Ownership is defined by control and trust, not physical location.

### External Resource

An External Resource is a resource hosted or managed by a third-party system
outside the control of the PKMS operator.

External Resources are untrusted by default and typically require explicit
acquisition before being ingested into PKMS.

Examples:

- Web services
- Messaging platforms (e.g. Telegram)
- Third-party SaaS applications

### Resource Storage

The physical location where resources are stored.

Currently:

- Local filesystem (FS): for owned resources
- Remote Server: for external resources

Future:

- Multiple local devices
- Remote or synced storage

### Resource Collection

A logical grouping of resources that share:

- A base location (path or URI)
- Globbing rules
- Indexing configuration
- Ingestion policy

Collections are **configuration-level concepts**, not database tables.

A Collection describing a set of LocalResource that could be further processed and Ingested into PKMS Database.

## Lifecycle & Processes

### Resource Acquisition

The process of transforming an External Resource into an Owned Resource
by fetching, exporting, or snapshotting it into Owned Resource Storage.

Examples:

- Downloading a webpage snapshot
- Fetching Telegram conversations

Acquisition concerns:

- *Where data comes from*
- *Where data goes to*
- *When and how it is fetched*

### Fetcher

A component responsible for Resource Acquisition.

Characteristics:

- Pulls data from a Remote Resource
- Writes resources into Local Resource Storage
- Does **not** index or modify the database

Examples:

- Webpage fetcher
- Telegram conversation fetcher

### Scheduler

A component that arranges and triggers Actions (such as fetching resource, ingestion) based on time or policy.

Examples:

- Periodic sync
- Daily snapshot
- Manual trigger
- Ingestion after resource update

### Resource Ingestion

The process of discovering, indexing, and upserting Owned Resources into the PKMS index and database. To make the Owned Resources queryable for user.

In PKMS, ingestion is a **pipeline**, not a single step, typically consists of:

- Glob
- Index
- Upsert

### Ingestion Pipeline

The ordered process:

```text
Glob -> Index -> Upsert
```

- Discovers resources
- Extracts structured information
- Persists indexed data

This pipeline is deterministic and repeatable.

### Globber

A component that discovers resources from storage.

Responsibilities:

- Enumerate files based on base path / URI
- Apply glob patterns
- Produce a list of candidate resources

Does **not** read file contents.

### Indexer

A component that transforms a resource into structured indexed data.

Responsibilities:

- Read resource content
- Extract metadata and text
- Produce an `IndexedDocument`

Different Indexers may exist for different resource types.

### Upserter

A component that persists indexed data into storage.

Responsibilities:

- Insert or update records
- Enforce identity rules
- Maintain timestamps and integrity fields

Currently, the upserter targets SQLite.

## Data Models & Identity

### IndexedDocument

A **stable contract object** representing the indexed form of a resource.

Characteristics:

- Produced by Indexers
- Consumed by Upserters
- Versioned and schema-governed

This is a **hard boundary** between ingestion logic and storage.

### FileLocation

A structured description of a resource’s location.

Includes:

- scheme: Currently `"file"`
- authority: Currently `"file"`
- base_path: the Base path to the file
- relative_path: the relative path to the base

---

### file\_id

A human-readable, filename-derived identifier.

Characteristics:

- Appears in filenames
- Case-insensitive
- Optimized for human use
- Not guaranteed immutable

---

### file\_uid

A content-based or metadata-based unique identifier.

Characteristics:

- Stable across renames
- Generated via hash / UUID / CUID
- Used for precise identity tracking

---

### Internal Sequence ID

A database-generated identifier used internally.

Characteristics:

- Implementation detail
- Not exposed to users
- Used for joins and performance

---

## Classification & Semantics

### Snapshot

A resource that represents a **frozen capture** of content.

Examples:

- Webpage snapshot
- Exported chat history
- Archived HTML

Snapshots are typically:

- Read-only
- Not re-indexed unless explicitly requested

---

### Editable Resource

A resource expected to change over time.

Examples:

- Markdown notes
- Text documents

Editable resources are:

- Re-indexed when modified
- Considered mutable

---

## Retrieval & Knowledge

### Searcher

A component responsible for querying indexed data.

Examples:

- Full-text search
- Metadata search

Searchers do not open files.

### Knowledge Linking

The layer that manages relationships between resources.

Examples:

- Links between documents
- References via PKMS URI
- Graph-style relationships

This layer is **orthogonal to storage and indexing**.

### Relation Graph

A structured representation of relationships between resources.

Future-oriented concept:

- Supports backlinks
- Enables knowledge navigation

## Resolution Layer

### Resolution

Resolution is the process of interpreting a symbolic reference (typically a URI) and mapping it to a concrete action.

Resolution may involve:

- Resolving identifiers to resources
- Selecting appropriate representations
- hoosing viewers or handlers
- Dispatching actions to external systems (browser, OS, applications)

Resolution does not process or analyze content itself.

### Resolver

A Resolver is a component responsible for performing resolution.

Examples:

- URI Resolver
- Resource Resolver
- Representation Resolver

Resolvers operate on identifiers and metadata, not raw content.

### PKMS URI

A scheme-based identifier used to reference resources.

Examples:

- `pkms://file/<file_id>`
- `pkms://uid/<file_uid>`

URIs abstract away physical storage details.

### URI Resolver

A component that resolves PKMS URIs into actionable targets.

Targets may include:

- Filesystem paths
- Database records
- External applications

### Representation

A Representation is a derived, presentable form of a Resource, suitable for a specific viewing or interaction context.

Key properties:

- Derived from an Owned Resource
- May be transient or cached
- Does not change the underlying resource
- Chosen based on intent and context

Examples:

- HTML preview generated from Markdown
- HTML rendering of a PDF
- Transcoded audio waveform + transcript
- Resized image for preview

A resource may have multiple representations.

### Preview Representation

A Preview Representation is a representation optimized for fast, inline viewing—typically in a web browser.

Characteristics:

- Read-only
- Lightweight
- Focused on continuity of user experience
- May omit full fidelity or advanced features

Preview representations are commonly used in search result browsing.

### Viewer

A Viewer is a component responsible for presenting a representation to the user.

Viewers do not decide what to show—only how to show it.

Examples:

- Browser Viewer
- Native Application Viewer
- Embedded Media Viewer

### Browser Viewer

A Browser Viewer presents a representation using a web browser.

Typical use cases:

- Previewing search results
- Inline reading
- Lightweight inspection before opening native applications

Browser viewers typically operate on HTML-based representations.

### Native Viewer

A Native Viewer delegates presentation to a system-installed application.

Examples:

- Opening a PDF in a PDF reader
- Playing media in a media player
- Editing a document in a text editor

Native viewers operate on the original resource or a system-supported representation.

### Handler

A Handler is a component that executes the resolved action.

Handlers may:

- Invoke viewers
- Open files
- Launch external applications
- Trigger system-level behaviors

Handlers are selected during resolution and perform side effects.

## Architecture & Design

### Configuration as Data

A design principle where system behavior is driven by declarative configuration rather than code changes.

Implemented via:

- JSON / JSONC
- Pydantic models

### Contract Boundary

A stable interface between system components.

Examples:

- IndexedDocument
- Configuration models

Contracts reduce coupling and enable future evolution.

### Local-First

A design principle where:

- Data is owned locally
- Core functionality works offline
- External systems are optional, not required

## Notes

- This glossary is **normative**, not descriptive.

- New terms should be added via ADR or design documents.

- Renaming a term is considered a breaking conceptual change.
