# PKMS Component Author Guide

## 0\. Purpose and Audience

This document is intended for developers who:

- Implement new PKMS components (Indexer, Screener, Searcher, Upserter, etc.)
- Extend or customize existing components
- Need a clear mental model of PKMS’s internal architecture and contracts

This document is **not** intended for end users or basic configuration-only usage.

## 1\. What Is a Component?

In PKMS, a **Component** is a pluggable, composable unit of behavior that participates in the ingestion or query pipeline.

Examples include:

- **Globber** — discovers candidate resources
- **Screener** — validates and admits candidates
- **Indexer** — converts resources into indexed representations
- **Upserter** — writes indexed data into shared storage
- **Searcher** — queries indexed storage

### Core Properties of a Component

A Component:

- Encapsulates a **single responsibility**
- Is **configured declaratively**
- May optionally rely on **runtime-provided shared state**
- Must **not assume global singletons**

## 2\. The Three Core Building Blocks

Every component type is defined by three related concepts:

```text
Component
├── ComponentConfig   (static, declarative)
└── ComponentRuntime  (dynamic, imperative, optional)
```

## 2.1 Component (Behavior)

The Component class defines *what the component does*.

Characteristics:

- Usually an abstract base class (ABC)
- Implements domain logic only
- Does **not** own resource lifecycles
- Does **not** assume a runtime is present

Example shape:

```python
class Component(ABC):
    name: str
    Config: type[ComponentConfig]
    Runtime: type[ComponentRuntime]
```

## 2.2 ComponentConfig (Static Configuration)

`ComponentConfig` describes **how a component should be constructed and behave**.

### Properties

- Inherits from `pydantic.BaseModel`
- Serializable (JSON / YAML)
- Immutable during runtime
- Used for validation, selection, and reproducibility

### Design Rules

✅ May contain:

- Component identity (`name`, `type`)
- Policy parameters (thresholds, modes, flags)
- Resource *descriptors* (DB URI, endpoint, paths)

❌ Must not contain:

- Open connections
- File handles
- Thread-local or mutable state
- Caches or live objects

> **Config describes intent, not execution.**

## 2.3 ComponentRuntime (Execution-Time State)

`ComponentRuntime` exists to carry **shared, mutable, or long-lived execution state**.

Typical examples:

- Database connection pools
- Thread-local connection caches
- Cross-component registries (e.g. deduplication state)
- Shared caches or indexes

### Key Characteristics

- Created and owned **outside** the component
- Injected into the component at construction time
- May be `None`
- May provide lifecycle hooks (optional)

```python
def __init__(
    self,
    *,
    config: ComponentConfig,
    runtime: Optional[ComponentRuntime] = None,
):
    ...
```

## 3\. Runtime Dependency Rules (Critical)

### MUST

- A component must **not** create or own global runtime state
- A component must **not** assume runtime lifetime
- A component must **not** close shared resources in `__del__`

### SHOULD

- If runtime is missing, the component should:
  - Fall back to per-call resources, or
  - Provide clearly defined degraded behavior

### MAY

- Runtime may expose lifecycle methods such as:
  - `shutdown()`
  - `cleanup_thread()`

## 4\. Components and Global State

### Principle

> A component must not *own* global state, but may *operate on* global state via runtime.

Examples:

- ❌ Storing a DB connection directly on a component instance
- ✅ Accessing a DB connection via injected runtime
- ✅ Upserter mutating shared storage via runtime

### Why Upserter Is Special

Upserter’s responsibility is **explicitly to mutate shared state**.

Therefore:

- Runtime is a **required dependency** for correct behavior
- If runtime is missing, behavior must be:
  - Explicitly failing, or
  - Explicitly no-op (documented)

Silent failure is not acceptable.

## 5\. Module Structure and Naming

### Recommended Layout

```text
pkms.core.component/
├── base/                 # Public abstractions
│   ├── Component
│   ├── ComponentConfig
│   └── ComponentRuntime
├── indexer/
│   ├── base.py
│   ├── html_indexer.py
│   └── ...
├── screener/
│   ├── base.py
│   └── ...
```

### Naming Guidelines

- `base` is a **public abstraction boundary**
- Avoid `_base` (suggests private/internal)
- Avoid re-exporting symbols into higher-level namespaces
- Prefer explicit imports:  
    `from pkms.core.component.base import Component`

## 6\. Behavioral Constraints Across Components

### Components MUST NOT

- Perform database writes (except Upserter)
- Mutate input objects
- Implicitly depend on other components

### Components SHOULD

- Accept explicit inputs → produce explicit outputs
- Make decisions explainable (`reason`, `diagnostics`)
- Be testable in isolation

## 7\. Degraded Behavior

If a component cannot fully function without runtime support:

- Degraded behavior **must be explicitly defined**
- Behavior **must be documented**
- Silent skipping or partial execution is forbidden

## 8\. One-Sentence Summary

> **Config defines intent,  
> Component implements behavior,  
> Runtime acknowledges that the world is shared.**
