# ADR-0027: URI Path Segmentation Semantics in `FileLocation`

## Status

**Status**: Accepted  
**Date**: 2026-01-25  

## Context

`FileLocation` supports parsing and representing URIs that may or may not include an authority component, and whose paths may be empty, absolute, or rootless, according to RFC 3986.

During the implementation of `FileLocation.from_uri`, several ambiguities arise from RFC 3986’s permissive grammar, especially around edge cases such as:

- `scheme:`
- `scheme:/`
- `scheme://`
- `scheme:///`
- trailing slashes
- empty path vs absolute path

RFC 3986 intentionally allows multiple syntactically distinct URI forms that appear similar but have different meanings depending on:

- whether an authority component is present
- whether the path is empty or absolute
- how leading slashes are interpreted
- whether empty path segments are preserved

The design challenge is to define a **stable and unsurprising internal representation** that:

1. Respects RFC 3986 grammar
2. Preserves meaningful distinctions (e.g. empty vs absolute path)
3. Avoids embedding filesystem or OS-specific semantics
4. Is suitable as a long-term internal model, even when some states are not serializable back into a URI

## Decision

### 1\. Path Segmentation Model

`FileLocation` represents URI paths using an immutable tuple called `segments`.

```python
segments: tuple[str | None, ...]
```

Each element represents a **logical URI path segment**, after percent-decoding.

The following conventions apply:

- `None` is used **internally** as a *root marker*, indicating an absolute path
- `""` (empty string) represents an explicitly empty segment (e.g. a trailing `/`)
- `segments = ()` represents an **empty path**

This model directly mirrors RFC 3986’s definition of `segment = *pchar`, including the allowance for empty segments.

### 2\. Absolute vs Empty Path

The distinction between **empty path** and **absolute path** is preserved explicitly:

| URI form | Meaning | `segments` |
| --- | --- | --- |
| `scheme:` | empty path | `()` |
| `scheme:/` | absolute path with empty segment | `(None, "")` |
| `scheme:///` | absolute path with empty segment | `(None, "")` |

The presence of the root marker (`None`) is the sole indicator of an absolute path.

### 3\. Empty Segments and Trailing Slashes

Trailing slashes are preserved as empty segments:

| URI | `segments` |
| --- | --- |
| `a/` | `("a", "")` |
| `/a/` | `(None, "a", "")` |
| `/a//` | `(None, "a", "", "")` |

No normalization or collapsing of slashes is performed.

### 4\. Internal-Only States

Some internal `segments` states **cannot be uniquely serialized back into a URI**, but are still allowed:

- `(None,)` represents an absolute path with no segments
- This state is **never produced by `from_uri`**
- It may exist as the result of internal transformations or joins

This is intentional:  
`FileLocation` is a semantic model, not a lossless URI pretty-printer.

### 5\. Authority Handling (Clarification)

`FileLocation` distinguishes between:

- **null authority** (`authority is None`)
- **empty authority** (`authority == ""`)

This distinction exists in RFC 3986 but is not preserved by Python’s `urlparse`.  
`from_uri` applies a corrective check to recover this information where possible.

## Design Guarantees

This ADR guarantees that:

- `segments` preserve RFC-valid path distinctions
- Empty segments are never dropped or normalized
- Absolute vs relative paths are always explicit
- Percent-decoding happens at the segment level
- No filesystem or OS semantics are embedded in `segments`

## Rationale

This design deliberately separates **URI syntax**, **semantic path structure**, and **environment-specific interpretation** in order to handle the inherent ambiguity of RFC 3986 without losing information or inventing false semantics.

### 1\. RFC 3986 Is Permissive by Design

RFC 3986 allows multiple syntactic forms that are distinct at the grammar level but easy to conflate in practice, including:

- empty path vs absolute path
- presence vs absence of authority
- trailing slashes vs no trailing slashes
- multiple adjacent slashes

Rather than normalizing these differences away, `FileLocation` preserves them where they are meaningful and representable.

### 2\. `segments` Is a Semantic Layer, Not a Syntax Mirror

The internal `segments` model is **not a direct encoding of RFC grammar**, but a semantic abstraction:

- `None` represents a root marker (i.e. “this path is absolute”)
- `""` represents an explicitly empty segment (i.e. trailing slash)
- `segments=()` represents an empty path

This allows the model to:

- preserve trailing slashes
- distinguish empty vs absolute paths
- reason about paths independently of their textual URI form

Some internal states (e.g. `(None,)`) are intentionally allowed even though they cannot be serialized into a valid URI. This is a conscious trade-off to keep internal operations simple and expressive.

### 3\. No Implicit Normalization

The model intentionally avoids implicit normalization such as:

- collapsing multiple slashes
- removing empty segments
- resolving dot-segments
- guessing filesystem semantics

Any such behavior would silently discard information and make round-tripping or reasoning across layers unreliable.

Normalization, if needed, must be **explicit and layered**, not accidental.

### 4\. Authority and Path Are Treated Orthogonally

Authority presence (`None` vs empty vs non-empty) and path structure are treated as independent dimensions, even though many libraries conflate them.

This allows `FileLocation` to correctly model cases such as:

- `scheme:` (no authority, empty path)
- `scheme://` (empty authority, empty path)
- `scheme:///` (empty authority, absolute empty path)

These distinctions are required for correctness when interoperating with URI-based systems.

### 5\. Filesystem Semantics Are Explicitly Out of Scope

The `segments` model deliberately avoids encoding:

- OS path rules
- filesystem constraints
- drive-letter semantics
- platform-specific separators

All filesystem interpretation is deferred to **explicit projection methods** (`to_filesystem_path`, etc.).

This prevents accidental coupling between URI meaning and a particular operating system.

### 6\. Design Goal: Predictability Over Convenience

The primary design goal is **predictability**, not minimalism.

This model prefers:

- explicit states over inferred ones
- internal consistency over shortest code paths
- clear invariants over “what most libraries do”

As a result, `FileLocation` may appear more verbose than typical path utilities, but it avoids surprising behavior in edge cases and remains safe to evolve.

## Non-goals

The following are explicitly **out of scope** for this ADR:

- Full URI normalization (e.g. dot-segment removal)
- Canonical URI rendering
- Query (`?`) handling
- Fragment (`#`) handling
- Path parameter (`;`) handling
- Guaranteeing that all internal states are serializable back into a URI
- Enforcing stricter invariants than RFC 3986 requires

Future ADRs may extend `FileLocation` to cover these concerns.


## Non-goals

The following concerns are **explicitly out of scope** for this design.

### 1\. Filesystem Correctness or Validity

- The model does not guarantee that a projected filesystem path:
  - exists
  - is accessible
  - is legal on the target OS
- Characters such as `:` or `/` inside segments are permitted.

Filesystem correctness is the responsibility of the execution environment.

### 2\. Path Normalization or Canonicalization

- The system does **not**:
  - collapse consecutive slashes
  - remove empty segments
  - resolve `"."` or `".."` segments
- No attempt is made to define a “canonical” path form.

All segments are preserved exactly as derived.

### 3\. Full URI Component Coverage

- This ADR intentionally limits its scope to the following URI components
  - scheme
  - authority
  - path
- Query parameters (`?query`) and fragments (`#fragment`) are not modeled.
- URI parameters (`;params`) within path segments are not interpreted.
- These components may be added in future ADRs.

### 4\. Full Bidirectional Textual Round-Trip

`FileLocation` does **not** guarantee full bidirectional round-trip fidelity
between `FileLocation` and URI strings.

In particular:

- Not all internal `PathSegments` states have a unique or valid textual URI representation
  (e.g. `(None,)`)
- Therefore, `FileLocation → URI → FileLocation` is **not guaranteed** to preserve
  the original internal structure

This is an intentional design choice.

`FileLocation` is allowed to represent semantic path states that are
not directly expressible in RFC 3986 syntax.

### 5\. Scheme-Specific Semantics

- No scheme-specific interpretation is applied.
- `file:`, `http:`, `pkms:` and others are treated uniformly at the path level.
- Dereferencing behavior is explicitly out of scope.

### 6\. Automatic Interpretation of Authority Semantics

- The model does not infer meaning from authority values.
- Empty authority (`""`) and null authority (`None`) are treated distinctly but not interpreted.

## Consequences

- Some `segments` states are representable internally but not textually.
  - Such states intentionally have no precise or unique URI string representation.
  - This allows `FileLocation` to express semantic path states beyond RFC 3986 syntax.

- Consumers must treat `segments` as **semantic path units**, not filesystem tokens
  or operating-system-dependent constructs.

- The model favors semantic precision and explicitness over convenience.
  - Additional complexity is accepted at the parsing and rendering boundaries
    in order to guarantee stability, correctness, and unambiguous meaning
    within the core model.

- URI parsing and segmentation behavior is fully deterministic and testable.
  - All edge cases (empty paths, absolute paths, trailing slashes, authority presence)
    have explicitly defined outcomes.

- **Asymmetric Round-Trip Guarantees**
  - Round-trip guarantees are intentionally **asymmetric**.

  - **Ingest direction (`URI → FileLocation`)**
    - Strongly defined and information-preserving.
    - For URIs composed only of `(scheme, authority, path)`,
      the transformation  
      `URI → FileLocation → URI`
      preserves URI *semantics* as defined by RFC 3986.
    - Exact textual identity of the URI string is not guaranteed.

  - **Emission direction (`FileLocation → URI`)**
    - Best-effort and constrained by RFC 3986 expressiveness.
    - Some internal `segments` states may not have a unique or exact
      textual URI representation.

  - This asymmetry allows `FileLocation` to function as a
    **semantic superset** of URI syntax rather than a lossless string wrapper.

## Appendix A: RFC 3986 Mapping Table

This appendix documents how `FileLocation` and `PathSegments` map to RFC 3986 URI grammar, and where explicit design choices were made.

Its purpose is to clarify **what is RFC-derived** and **what is intentionally defined by this system**.

### A.1 Path Grammar Mapping

| RFC 3986 Concept | RFC Definition | FileLocation Representation | Source |
| --- | --- | --- | --- |
| path-empty | `path-empty = 0<pchar>` | `segments = ()` | RFC-derived |
| absolute path | `path-absolute` / `path-abempty` | `segments[0] is None` | Design choice |
| relative path | `path-rootless` / `path-noscheme` | `segments[0] is not None` | Design choice |
| path segments | `segment = *pchar` | `tuple[str]` entries | RFC-derived |
| empty segment | allowed (`*pchar`) | `""` preserved as segment | RFC-derived |
| trailing slash | results in empty segment | trailing `""` | RFC-derived |

### A.2 Slash Semantics (`/`)

| URI Example | RFC Interpretation | PathSegments | Source |
| --- | --- | --- | --- |
| `/` | absolute path with one empty segment | `(None, "")` | RFC-derived |
| `/a` | absolute, one segment | `(None, "a")` | RFC-derived |
| `/a/` | absolute, trailing empty segment | `(None, "a", "")` | RFC-derived |
| `///a` | path-abempty with empty segments | `(None, "", "", "a")` | Design choice (explicit preservation) |
| `a/b` | relative path | `("a", "b")` | RFC-derived |

> RFC 3986 allows empty segments; it does not mandate normalization.  
> Preservation of repeated slashes is an explicit design choice.

### A.3 Percent-Encoding and Decoding

| Aspect | Behavior | Source |
| --- | --- | --- |
| Segment splitting | split **before** percent-decoding | RFC-derived |
| `%2F` handling | decoded to literal `/` inside segment | RFC-derived |
| Uppercase hex | `%2F` preferred over `%2f` | RFC recommendation |
| Encoded slash | does **not** introduce hierarchy | RFC-derived |

Example:

```css
/a/b%2Fc → (None, "a", "b/c")
```

### A.4 Authority Handling

| URI Form | RFC Meaning | scheme | authority | PathSegments | Source |
| --- | --- | --- | --- | --- | --- |
| `scheme:` | no authority, empty path | `"scheme"` | `None` | `()` | RFC-derived |
| `scheme:/a` | no authority, absolute path | `"scheme"` | `None` | `(None,"a")` | RFC-derived |
| `scheme://` | empty authority | `"scheme"` | `""` | `()` | RFC-derived |
| `scheme://a` | authority `a`, empty path | `"scheme"` | `"a"` | `()` | RFC-derived |
| `scheme:///a` | empty authority, absolute path | `"scheme"` | `""` | `(None,"a")` | RFC-derived |

⚠️ **Python compatibility note**  
Python’s `urlparse` collapses empty and null authority.  
`FileLocation.from_uri` applies a post-parse patch to restore this distinction.

This behavior is a **pragmatic workaround**, not an RFC requirement.

### A.5 Absolute Marker (`None`) Semantics

| Representation | Meaning | Source |
| --- | --- | --- |
| `segments[0] is None` | absolute path | Design choice |
| `(None,)` | absolute path with no segments | Design-only (no unique URI rendering) |
| `(None,"")` | absolute path `/` | RFC-derived |

The use of `None` as an absolute-path marker is **not defined by RFC 3986**, but chosen to:

- keep path semantics explicit
- avoid overloading empty strings
- allow internal states not representable textually

### A.6 Normalization Decisions

| Aspect | RFC Position | FileLocation Behavior |
| --- | --- | --- |
| Slash collapsing | allowed but not required | ❌ not performed |
| Dot-segment removal | defined for resolution | ❌ not performed |
| Path normalization | optional | ❌ explicitly avoided |
| Canonical rendering | unspecified | ❌ not guaranteed |

These are **intentional non-goals**, documented in ADR-0027.

### A.7 Scope Clarifications

| Feature | Status |
| --- | --- |
| Query (`?`) | Out of scope |
| Fragment (`#`) | Out of scope |
| Path parameters (`;`) | Out of scope |
| Scheme-specific semantics | Out of scope |

Future ADRs may extend the model without invalidating these guarantees.

### Appendix Summary

- RFC 3986 defines **what is syntactically legal**
- `FileLocation` defines **what is semantically preserved**
- Where RFC is permissive or silent, explicit design choices are made
- No behavior is accidental or emergent
