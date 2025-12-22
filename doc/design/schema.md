# Schema Documentation — files Table

> This document defines the identity contract, storage semantics, and indexing intent
for PKMS file-level resources.

## Table: `files`

This table represents file-like resources indexed by PKMS.
A “file” here is a logical resource unit, not strictly limited to filesystem files.
Examples include:

- Markdown documents
- PDF / HTML snapshots
- Audio / video files
- Images
- Exported web captures (SingleFile, Readability, etc.)

## Identity Model

PKMS uses three layers of identity, each serving a different purpose.

| Field | Name | Purpose |
| --- | --- | --- |
| id	| DB sequence ID | Internal database primary key
| file_id | Human-facing ID | Stable, readable identifier derived from filename
| file_uid | Content UID | Optional strong identifier (hash / UUID / CUID)

### `id`

- SQLite internal primary key
- Auto-incremented
- Never exposed to users

### `file_id`

- Derived from filename (e.g. yyyy-mm-dd-nnnn[suffix])
- Case-insensitive by convention
- Stable across renames of title / context

Used as the primary external reference in PKMS

### `file_uid`

- Optional
- Used for content-level identity
- May be:
    - UUID / CUID (for editable files)
    - Hash-derived UID (for snapshot files)

Not guaranteed to exist in v1

## Location
### `file_uri`

- URI pointing to the physical location of the resource
- Currently restricted to:
  - `file:///...`
- Uses URI instead of URL to avoid locking into HTTP semantics
- May support other schemes in the future

### `origin_uri`

- Optional
- Records the original source of the resource
- Common examples:
  - https://example.com/article
  - pkms://page/2025-12-14-0001
- Not necessarily dereferenceable

## File Properties

### `file_extension`

- File extension with leading dot (e.g. .md, .pdf)
- Empty string '' is allowed
- Important:
  - Empty string is reserved for future semantics and is NOT restricted to directory meaning.
  - It may represent extensionless resources or non-file-backed logical entities.
- This field is always non-null to simplify querying and indexing.

### `file_size`

- File size in bytes
- Reflects physical file size at indexing time

## Classification
### `file_kind`

Indicates how PKMS should treat the resource in indexing and update strategies.

Current v1 values:

| Value | Meaning |
| --- | --- |
| snapshot | Immutable capture of content at a point in time |
| editable | User-editable, expected to change over time |

- Why snapshot instead of readonly?
  - snapshot expresses temporal semantics (captured state)
  - readonly only expresses permission

- Some future resources may be:
  - technically writable
  - but semantically snapshots

Therefore, snapshot is preferred as it encodes intent, not OS-level mutability.

## Metadata
### `title`

- Best-effort, human-readable display title
- Guaranteed to be non-empty
- Derived from:
  - `<title>` tag (HTML)
  - Metadata (PDF, media)
  - Filename fallback
- Generated placeholder (e.g. Photo 2025-12-16)

### `importance`

- Integer importance level
- Default: `0`
- UI may render this as symbolic markers (e.g. !, !!, !!!)

## Integrity

### file_hash_sha256

Optional SHA-256 hash of file content

- Used for:
  - Integrity checks
  - Duplicate detection (best-effort)
  - Not used as a primary identity

- May change due to:
  - Snapshot metadata injection
  - Format-specific normalization

## Time Fields

All datetime fields are stored as ISO 8601 strings.

| Field | Meaning |
|---|---|
| record_indexed_datetime | When this record was first indexed |
| record_updated_datetime | When this record was last updated |
| file_created_datetime | File creation time |
| file_modified_datetime | Last file modification time |

SQLite does not automatically manage these fields.

## Content

### `text`

- Extracted plain text content (Nullable)
- May be absent for:
  - Binary files
  - Media assets
  - Non-text snapshots

### `extra`

- JSON blob for:
  - Format-specific metadata
  - Parser output
- Future extensions
- Schema intentionally left open

## Design Notes

This schema is v1, intentionally conservative

- Supports:
  - Multiple devices
  - Multiple copies of the same logical resource
  - Future versioning strategies

- No assumptions are made about:
  - Synchronization
  - Deduplication
  - Content equivalence

Those concerns are deferred to future layers.

## Summary

- snapshot is preferred over readonly
- file_extension = '' is reserved, not directory-specific
- Identity is layered, not overloaded
- Schema is designed to evolve without breaking contracts