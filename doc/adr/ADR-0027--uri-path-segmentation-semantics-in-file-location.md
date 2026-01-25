# ADR-0027: URI Path Segmentation Semantics in `FileLocation`

## Status

Status: Draft
Date: 2026-01-25  

## Context

`FileLocation` supports parsing and representing URIs that may or may not include an authority component, and whose paths may be empty, absolute, or rootless, according to RFC 3986.

While implementing `FileLocation.from_uri`, ambiguities arise when interpreting how different URI spellings should map to internal `segments`, especially for edge cases such as:

- `scheme:`
- `scheme:/`
- `scheme://`
- `scheme:///`
- trailing slashes
- empty vs absolute paths

RFC 3986 allows multiple distinct syntactic forms that look similar but are semantically different, particularly around:

- empty path vs absolute path
- presence of authority
- how many leading slashes are meaningful
- whether empty segments should be preserved

The goal is to define **a consistent, unsurprising internal representation** that:

1. Respects RFC 3986 grammar

2. Preserves meaningful distinctions (e.g. absolute vs empty path)

3. REVIEW ~~Avoids inventing segments that are not representable in a URI~~
   - The design is mean to accept

4. REVIEW ~~Keeps `segments=()` as the canonical representation of “no path”~~
   - shuldn't no-path be `segments=None`, and empty-path be `segments=()`
   - just like null-authority and empty-authority

5. REVIEW This ADR current handle only RFC 3986 scheme, authority and path

## Decision

### 1\. Segment Model

- `segments: tuple`
- Each element represents a path segment
- `None` is used **internally** to represent the *root marker* (`/`)
- Empty string `""` represents an explicitly empty segment (i.e. trailing `/`)
- REVIEW `segments=()` represents an **empty path**

> Note: `(None,)` is a valid internal state but **cannot be serialized into a URI**. It is allowed in `FileLocation` but never produced by `from_uri`.


### 2\. Empty Path

If the URI has an empty path:

- No leading `/`
- No segments

```python
segments = ()
```

Examples:

| URI | RFC Path Type | segments |
| --- | --- | --- |
| `scheme:` | path-empty | `()` |
| `scheme://` | path-empty | `()` |



### 3\. Absolute Path (Single Leading Slash)

~~Per RFC 3986 `path-absolute = "/" [ segment-nz *( "/" segment ) ]`~~

Per RFC 3986 `path-abempty  = *( "/" segment )`

- A single leading `/` introduces hierarchy
- Absolute paths **always produce a root marker**

```python
segments = (None, ...)
```

Examples:

| URI | segments |
| --- | --- |
| `scheme:/` | `(None, "")` |
| `scheme:/a` | `(None, "a")` |
| `scheme:/a/` | `(None, "a", "")` |
| `scheme:/a/b` | `(None, "a", "b")` |



### 4\. Rootless Path (No Authority)

When no authority is present and the path does not begin with `/`, it is parsed as `path-rootless`:

Examples:

| URI | segments |
| --- | --- |
| `scheme:a` | `("a",)` |
| `scheme:a/` | `("a", "")` |
| `scheme:a/b` | `("a", "b")` |



### 5\. Authority and Path Interaction

When an authority is present (`scheme://authority`):

- An empty path remains empty
- The path component starts **after** the authority
- A path exists only if a `/` follows the authority

Examples:

| URI | Explanation | segments |
| --- | --- | --- |
| `scheme://` | authority, empty path | `()` |
| `scheme://a` | authority only, no path | `()` |
| `scheme://a/` | absolute empty path | `(None, "")` |
| `scheme://a/b` | absolute path `/b` | `(None, "b")` |
| `scheme://a/b/` | absolute path with trailing slash | `(None, "b", "")` |



### 6\. Triple Slash (`///`)

`scheme:///` represents:

- empty authority
- absolute path `/`

Thus:

| URI | segments |
| --- | --- |
| `scheme:///` | `(None, "")` |
| `scheme:///a` | `(None, "a")` |
| `scheme:///a/` | `(None, "a", "")` |

## Consequences

- URI parsing becomes predictable and testable.
- Serialization from `FileLocation` to URI is well-defined.
- Some internal states cannot round-trip to URI, by design.
- Test cases explicitly document edge cases instead of hiding them.

## Rationale

- RFC 3986 distinguishes **empty path** from **absolute path**; this distinction is preserved.
- `segments=()` is the only representation for an empty path.
- A leading `/` always introduces a root marker (`None`).
- Empty segments (`""`) are preserved to reflect trailing slashes.
- No URI produces `(None,)`; such a state is internal-only and non-serializable.
- This mapping minimizes surprise while remaining faithful to URI grammar.

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

- Query parameters (`?query`) and fragments (`#fragment`) are not modeled.
- URI parameters (`;params`) within path segments are not interpreted.
- These components may be added in future ADRs.

### 4\. Guaranteed Round-Trip Rendering

- Not all internal `PathSegments` representations are guaranteed to round-trip  
    to a syntactically identical URI string.
- Some segment states (e.g. `(None,)`) may not have a unique textual URI form.

Semantic preservation takes precedence over textual identity.

### 5\. Scheme-Specific Semantics

- No scheme-specific interpretation is applied.
- `file:`, `http:`, `pkms:` and others are treated uniformly at the path level.
- Dereferencing behavior is explicitly out of scope.

### 6\. Automatic Interpretation of Authority Semantics

- The model does not infer meaning from authority values.
- Empty authority (`""`) and null authority (`None`) are treated distinctly but not interpreted.


## Consequences

- URI parsing becomes predictable and testable.
- Serialization from `FileLocation` to URI is well-defined.
- Some internal states cannot round-trip to URI, by design.
- Test cases explicitly document edge cases instead of hiding them.

> This design intentionally favors **semantic precision and explicitness** over convenience.  
> Complexity is accepted at the boundary in order to guarantee stability and correctness at the core.

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