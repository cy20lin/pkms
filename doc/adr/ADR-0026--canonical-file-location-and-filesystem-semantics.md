# ADR-0026: Canonical FileLocation and Filesystem Semantics

## Status

Status: Accepted  
Date: 2026-01-25  

## Context

The system needs to store and reason about file-like resources coming from different environments (local filesystem, file URIs, future schemes such as WebDAV). These resources must be persisted in a database and later re-interpreted on potentially different platforms (POSIX, Windows).

Filesystem paths and `file:` URIs have platform-dependent semantics:

* Windows paths encode drive letters (e.g. `C:/a/b`).
* POSIX filesystems allow `:` as a valid filename character.
* A `file:` URI such as `file:///c:/a/b` maps differently depending on the target platform:

  * On POSIX: `/c:/a/b`
  * On Windows: `c:/a/b`

Because of this, filesystem paths are not round-trip safe across platforms, and `file:` URIs themselves explicitly rely on local system interpretation (RFC 8089).

The design must avoid leaking platform-specific filesystem semantics into the persistent data model, while still allowing correct interpretation at runtime.

## Decision

We introduce a canonical `FileLocation` model that stores paths as URI-aligned **path segments**, independent of any specific filesystem semantics.

### **PathSegments Invariant**

`FileLocation` represents paths as ordered segment tuples (`PathSegments`) rather than opaque strings.  
This design enables lossless round-tripping between URI and filesystem representations while keeping resolution logic explicit.

#### Definition

```text
PathSegments := tuple[str | None, ...]
```

#### Invariants

* `PathSegments` **may be empty**, representing an empty or unspecified path
* If non-empty:
  * **Only the first segment may be `None`**
  * All subsequent segments **must be non-null strings**
* `None` represents a leading semantic marker (e.g. root / authority boundary),  
    not a literal path component

#### Non-goals (Current Scope)

* Multiple `None` segments
* `None` appearing in middle or trailing positions
* Normalization of repeated separators (e.g. `////`)
* Preservation of original filesystem-specific semantics (e.g. Windows drive vs POSIX root)

Such cases are considered **unsupported** and will be rejected at model construction time.

This constraint is enforced via validation and documented as a precondition.  
Future extensions may relax or generalize this invariant if required.

### Canonical Representation

* Paths are stored as ordered `segments`.
* Absolute paths are indicated by a leading `None` segment.
  * Example: `/a/b/c` → `(None, "a", "b", "c")`
* No platform-specific meaning is encoded in segments.
  * Example: `c:` is treated as a literal segment, not a drive designator.
* Segments are conceptually aligned with URI path segments, not filesystem path components.

### Information Loss Is Explicitly Allowed

Converting from a filesystem path or a `file:` URI into canonical segments **may lose platform-specific semantics**, including but not limited to:

* Windows drive letter interpretation
* UNC path semantics
* Original path separator conventions

This information loss is intentional and accepted.

### Interpretation Responsibility

* Canonical `FileLocation` data is platform-neutral.
* Converting canonical segments into a filesystem path is a **projection**, not an inverse operation.
* The target runtime environment (POSIX, Windows, etc.) is responsible for interpreting the segments according to its own rules.

In other words:

> The model preserves *location identity*, not *filesystem meaning*.

## Consequences

### Positive

* Clean separation of concerns between storage and interpretation
* Database schema remains platform-agnostic
* Easy extension to new URI schemes (e.g. `dav://`, `s3://`)
* Avoids false guarantees of round-trip correctness

### Negative

* Original filesystem semantics cannot always be reconstructed
* Developers must understand that filesystem projection is platform-dependent

## Alternatives Considered

### Preserve Platform-Specific Semantics

Embedding OS-specific metadata (e.g. explicit drive markers) was rejected because:

* It leaks platform concerns into the data model
* It complicates persistence and querying
* It still cannot guarantee correct cross-platform behavior

### Store Raw Filesystem Paths

Rejected because:

* Paths are ambiguous across platforms
* They are not future-proof for non-filesystem URI schemes

## Notes

This design aligns with the reality that `file:` URIs and filesystem paths are inherently contextual. The system intentionally stops at a canonical, URI-aligned boundary and delegates interpretation to the runtime environment.
