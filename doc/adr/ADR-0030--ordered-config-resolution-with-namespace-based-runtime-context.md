# ADR-0030: Ordered Config Resolution with Namespace-Based Runtime Context

**Status**: Draft
**Date**: 2026-02-02  
**Related ADRs**:

- ADR-0016: Explicit Separation of Component, Config, and Runtime
- ADR-0028: App / Workspace Runtime & Logger Lifecycle
- ADR-0029: Config & State Update Semantics

## Context

PKMS configuration spans multiple conceptual layers and lifetimes:

- **Builtin defaults**
- **Application config**
- **Workspace config** (`.pkms`)
- **Collection config** (`.pkms.collection`)
- (Future) **Runtime-provided objects** (components, services)

These configurations are:

- User-authored
- Layered and overridable
- Frequently reused across scopes
- Required to remain understandable and debuggable

Early experiments revealed several tensions:

1. **DAG-based resolution** is powerful but introduces:
    - Hidden complexity
    - Non-local reasoning
    - Error-prone partial ordering
    - Poor debuggability in user-facing config

2. JSON is commonly used for config, but:
    - JSON formally does not define map ordering
    - Python implementations *do* preserve insertion order (≥3.7)

3. PKMS requires **multiple kinds of replacement**:
    - Simple string substitution
    - Config object reuse
    - (Future) runtime object references

4. Configuration must remain **pure data**, while still being expressive enough  
    to describe runtime wiring declaratively.

This ADR defines a **deterministic, ordered, namespace-driven config resolution model**  
that deliberately avoids DAG resolution while remaining extensible

## Decision

### 1\. Ordered Resolution Model (No DAG)

PKMS adopts a **single-pass, ordered resolution model**:

- Configuration objects are resolved **in the order their keys appear**
- No dependency graph (DAG) is constructed
- Earlier keys may be referenced by later keys
- Forward references are **not supported**

This model intentionally resembles an **imperative `let*` / sequential binding** rather than a declarative graph.

#### Rationale

- Aligns with how users naturally read config files
- Eliminates graph construction and cycle detection
- Keeps error locality clear
- Matches Python’s deterministic dict behavior

> While JSON does not formally guarantee ordering, PKMS explicitly **treats object key order as semantically meaningful**.

### 2\. Resolution Layers

Configuration is resolved **layer by layer**, from lowest to highest precedence:

1. Builtin
2. Application
3. Workspace
4. Collection

Each layer is resolved independently, then overlaid according to precedence rules defined elsewhere (see ADR-0029)

### 3\. Namespace-Based Resolution Context

All resolution occurs against an explicit **namespace context**.

At resolution time, the following namespaces are available:

```python
context = {
    "root": current_resolved_view,
    "raw": original_unresolved_config,
    "app": app_config,
    "workspace": workspace_config,
    "env": os.environ,
    "builtin": builtin_registry,
}
```

#### Namespace Semantics

- **`root`**
  - The *progressively resolved* view of the current config
  - Grows as keys are resolved in order
  - Primary mechanism for intra-config reuse
- **`raw`**
  - The namespace for all original, unresolved config data
  - Allows access to literal values without resolution effects
  - Enables future quote-like semantics without complicating the base model
  - for example use `raw.root` to access the unresolved config in `root`
- **`app`, `workspace`**
  - Fully resolved parent-layer configs
  - Read-only during resolution
- **`env`**
  - Environment variables
  - String-only access
- **`builtin`**
  - Builtin registries (e.g. components, defaults)
  - May include runtime-capable references (see §6)

### 4\. Replacement Semantics

PKMS defines **three distinct replacement forms**

#### 4.1 String Substitution — `{var}`

- Uses formatter-style syntax
- Operates only on strings
- Always produces a string

Example:

```json
{
  "root": "/data",
  "path": "{this.root}/files"
}
```

Rules:

- Formatter paths are resolved against the namespace context
- Missing keys raise a resolution error
- Escaping follows formatter rules

#### 4.2 Config Object Replacement — `${obj}`

- `${...}` indicates **object-level replacement**
- The entire value is replaced with the referenced object
- The string **must start with `${` and end with `}`**

Example:

```json
{
  "base_globber": { "type": "PathspecGlobberConfig" },
  "globber": "${this.base_globber}"
}
```

Rules:

- Replacement preserves object identity semantics (deep copy rules are implementation-defined)
- `${...}` is not interpolated into strings
- This is intentionally **not string formatting**

Escaping:

- `"$${foo}"` → literal `"${foo}"`

#### 4.3 Runtime Reference — `$builtin.components.globber`

- Same syntax as config object replacement
- Target may be a **runtime-capable reference**
- Resolution may be deferred until runtime construction

Rules:

- Resolver does **not** construct runtime objects
- Resolver records a reference token
- Runtime is responsible for realizing the reference

This preserves the **Config vs Runtime boundary** defined in ADR-0016

### 5\. Constants and Variables (Unified Model)

Rather than enforcing separate structures, PKMS treats config objects as **ordered bindings**.

Practically:

- Earlier keys behave like “constants”
- Later keys may reference earlier ones
- No self-referential cycles are supported

This avoids introducing:

- Separate `constants` / `variables` DAGs
- Topological sorting requirements
- Confusing partial evaluation rules

Future extensions may introduce explicit binding groups, but the base model remains sequential

### 6\. Resolution Algorithm

Resolution is implemented using:

- A **non-recursive walker**
- An **explicit stack**
- A pluggable **policy layer** for:
  - Node cloning
  - Assignment strategy
  - Type handling (dict, list, model, etc.)

This enables:

- Controlled maximum depth
- Predictable memory usage
- Extension to runtime-aware resolution
- Reuse of the same walker for:
  - Constants
  - Variables
  - Layer overlays
  - Future runtime resolution

### 7\. Config → Runtime Boundary

Resolution produces **resolved config values**, not runtime objects.

Explicitly:

- Resolver:
  - Substitutes strings
  - Replaces config objects
  - Records runtime references
- Runtime:
  - Interprets runtime references
  - Constructs components
  - Injects capabilities

This ensures:

- Config remains serializable
- Runtime remains mutable and contextual
- Capabilities depend on Runtime, not Config

## Consequences

### Positive

- Simple, deterministic mental model
- No DAG complexity
- Excellent debuggability
- Natural extension to runtime references
- Aligns with Python behavior and user intuition

### Trade-offs

- Forward references are not supported
- Ordering becomes semantically significant
- JSON portability depends on implementation behavior

These trade-offs are accepted for clarity and maintainability

## Notes

This ADR intentionally treats configuration as a **small, deterministic language** rather than a static data blob.

Complexity is managed by:

- Explicit namespaces
- Explicit ordering
- Explicit boundaries between config and runtime

Future ADRs may extend this model with:

- Optional quoting semantics
- Explicit binding blocks
- Partial re-resolution in runtime contexts
