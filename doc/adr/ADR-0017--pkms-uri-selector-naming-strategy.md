# ADR-0017: PKMS URI Selector Naming Strategy

## Status

**Status**: Accepted  
**Date**: 2026-01-15

## Context

PKMS introduces a custom URI scheme (`pkms:///`) to provide stable, human-usable references to managed files and resources.

These URIs are intended to be:

- Persisted long-term (notes, links, bookmarks)
- Generated and consumed by both humans and machines
- Used consistently across subsystems (ingestion, search, preview, linking)

A PKMS-managed file may be addressable via multiple identifier forms, including:

- **PKMS-native identifiers** (human-assigned, name-based)
- **Content-based identifiers** (e.g. SHA-256)
- **External identifiers** (e.g. ISBN, UUID, DOI)

This raises design questions regarding:

- How identifiers should be expressed in the URI path
- Whether a “default” identifier should exist
- How to balance human ergonomics with long-term semantic stability
- Whether URI versioning should be explicit

Example candidates:

```text
pkms:///file/id:2000-01-01-0001.txt
pkms:///file/sha256:abcd1234....pdf
pkms:///file/isbn:9780132350884.epub
```

## Decision

### 1\. Explicit selector-based addressing

PKMS URIs SHALL use **explicit selectors** to indicate the identifier namespace being used.

There is **no implicit or default selector**.

Examples:

```text
pkms:///file/id:1970-01-01-0000.txt
pkms:///file/uid:00000000-0000-0000-0000-000000000000.md
pkms:///file/sha256:0000000000000000000000000000000000000000000000000000000000000000.pdf
pkms:///file/isbn:000-0-00-000000-0.epub
```

### 2\. `id` is the PKMS-native primary identifier

The selector `id` denotes the **PKMS-native primary identifier**.

- It is defined and governed by PKMS
- It is human-assigned and human-readable
- Its structure is intentionally flexible and evolution-friendly
- It is **not** an alias for UUID, hash-based IDs, or external identifier schemes

The selector name `id` is deliberately generic and unqualified, serving as the canonical identifier within the PKMS domain.

### 3\. Short symbolic selectors are preferred

Selectors SHALL use **short, stable, symbolic names** rather than verbose, fully spelled-out descriptors.

Examples of accepted selector styles:

- `id`
- `uid`
- `sha256`
- `isbn`
- `doi`

Verbose alternatives such as:

```text
international-standard-book-number
persistent-identifier
content-hash-sha256
```

are explicitly rejected.

### 4\. File extension SHALL be present in the URI

The file extension **SHALL be included** as part of the URI path whenever applicable.

```text
pkms:///file/id:1970-01-01-0000.txt
pkms:///file/sha256:0000000000000000000000000000000000000000000000000000000000000000.pdf
```

Rationale:

- Improves human readability
- Provides immediate media-type hints
- Aids UI routing and preview handling
- Avoids ambiguity when the same identifier maps to multiple representations

URIs without extensions are permitted only when the resource is inherently extensionless.

### 5\. Compound selectors are not supported

Selectors such as:

```text
id+ext
id+extension
id+hash
```

are explicitly **not supported**.

Rationale:

- The selector identifies the namespace of the identifier
- The extension is part of the resource representation, not the identifier namespace
- Combining concerns increases parsing complexity and semantic ambiguity

### 6\. Selector-based extensibility replaces URI versioning

PKMS URIs intentionally avoid explicit version prefixes such as:

```text
pkms:///v1/file/...
pkms:///v2/file/...
```

Instead, new semantics or identifier schemes are introduced via **new selectors**:

```text
pkms:///file/blake3:...
pkms:///file/id2:...
```

This approach preserves backward compatibility and avoids link rot.

## Rationale

### URIs are identifiers, not documentation

PKMS URIs prioritize **stability and referential clarity** over self-descriptive verbosity.

This aligns with established identifier ecosystems such as ISBN, DOI, and cryptographic hashes, where meaning is defined by specification rather than literal expansion.

### `id` minimizes cognitive and ergonomic cost

All identifier names impose some learning cost.

The selector `id`:

- Is universally familiar
- Requires no explanation for basic usage
- Avoids over-specifying semantics prematurely
- Leaves room for internal evolution without renaming

In PKMS context, `id` naturally reads as “the primary identifier in this system”.

### Explicit selectors prevent hidden assumptions

By requiring explicit selectors, PKMS avoids implicit defaults that would:

- Create ambiguity
- Increase long-term maintenance risk
- Make future extensions harder

Explicitness today prevents semantic debt tomorrow.

## Consequences

### Positive

- Stable, ergonomic, and human-usable URIs
- Clear separation between PKMS-native and external identifiers
- Clean extensibility without version churn
- Reduced long-term regret around naming

### Trade-offs

- Short selectors (e.g. `id`, `uid`) require minimal user onboarding
- Some identifiers may not be self-explanatory to first-time users

This trade-off is accepted. Discoverability can be addressed in UI and documentation; URI stability cannot.

## Notes

PKMS URIs are treated as a **technical language**, not a UI affordance.

As with ISBNs or DOIs, initial unfamiliarity is expected—but once learned, the system becomes frictionless, expressive, and resilient over time.
