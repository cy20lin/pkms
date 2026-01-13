# ADR-0016: Explicit Separation of Component, Config, and Runtime

**Status**: Accepted  
**Date**: 2026-01-13

## Context

As PKMS evolves into a modular system composed of Globbers, Screeners, Indexers, Upserters, Searchers, and Resolvers, it becomes increasingly important to clarify:

- What a *Component* is
- How configuration is represented and validated
- How external state and execution-scoped resources are managed

Early designs implicitly mixed concerns such as configuration, resource acquisition, runtime state, and domain logic within single classes. This led to ambiguity in:

- Thread-safety expectations
- Lifecycle ownership (e.g. database connections)
- Whether components are expected to function without access to external state

In particular, components such as **Upserter** and **Searcher** inherently interact with shared external stores (e.g. SQLite), while others may operate purely on data.

This ADR formalizes a clear separation between **Component**, **Config**, and **Runtime**, and classifies components based on their dependency on runtime-provided resources.

## Decision

### 1\. Component

A **Component** is a unit of domain behavior that performs a well-defined role in the PKMS pipeline.

Examples include:

- Globber
- Screener
- Indexer
- Upserter
- Searcher
- Resolver

A Component:

- Encapsulates *what* work is performed
- Defines abstract behavior via an interface (ABC)
- MUST NOT directly manage global or process-wide resources
- MAY depend on a Runtime for external state access

A Component instance is **not** responsible for:

- Owning long-lived external resources
- Managing thread affinity
- Deciding lifecycle of shared infrastructure

### 2\. Config

A **Config** is a declarative, serializable description of *intent*.

Config objects:

- Are represented as Pydantic models
- Describe *what* a component needs, not *how* it is provided
- MUST be immutable once constructed
- MUST be safe to load from user-provided configuration files

Examples:

- `db_uri`
- `indexing_policy`
- `id_collision_strategy`
- `file_kind_rules`

Config MUST NOT:

- Open files
- Open network connections
- Hold live handles, connections, or credentials in active form

Config is a **domain-level contract**, not a runtime object.

```python
from pydantic import BaseModel
class ComponentConfig(BaseModel):
    ...
```

### 3\. Runtime

A **Runtime** represents execution-scoped, mutable state and external resource access.

Runtime objects:

- Are created and owned by the application (not the Component)
- MAY manage:
  - Database connections or pools
  - Thread-local caches
  - Cross-component shared state (e.g. ID registries)
- Define lifecycle hooks such as initialization and shutdown

Runtime is **not** serialized and **not** part of domain configuration.

```python
from abc import ABC
class ComponentRuntime(ABC):
    def shutdown(self) -> None:
        """
        Optional lifecycle hook.
        Application MAY call this.
        """
        ...
```

### 4\. Runtime Dependency Classification

Components are classified into two categories:

#### 4.1 Runtime-Optional Components

These components MAY operate without a Runtime, though functionality may be limited.

Examples:

- Globber
- Screener
- Indexer

Behavior without runtime:

- MUST be well-defined
- MUST NOT silently depend on global state
- MAY produce partial or local-only results

#### 4.2 Runtime-Required Components

These components **cannot function correctly** without access to external shared state.

Examples:

- Upserter
- Searcher
- Database-backed Resolver

Rules:

- Runtime MUST be provided at construction time
- Absence of runtime MUST result in explicit failure
- Silent no-op or implicit global access is forbidden

This is not a violation of purity; it is an explicit declaration of dependency.

### 5\. Construction Pattern

All Components follow a unified construction pattern:

```python
class Component(ABC):
    Config: type[ComponentConfig]
    Runtime: type[ComponentRuntime]

    def __init__(
        self,
        *,
        config: ComponentConfig,
        runtime: Optional[ComponentRuntime] = None,
    ):
        ...
```

Rules:

- `config` is always required
- `runtime`:
  - MAY be `None` for runtime-optional components
  - MUST be provided for runtime-required components

## Rationale

- Makes external state dependencies explicit and auditable
- Prevents accidental global state usage
- Clarifies thread-safety and lifecycle ownership
- Allows advanced runtime strategies (thread-local, pooling, IPC) without polluting domain logic
- Supports both simple single-user usage and future multi-collection, multi-runtime scenarios

## Consequences

### Positive

- Clear mental model for contributors and future maintainers
- Easier testing (Config and Component logic can be tested independently)
- Cleaner separation between domain logic and infrastructure

### Trade-offs

- Slightly increased abstraction and number of concepts
- Runtime management responsibility shifts to application layer

This trade-off is accepted in favor of long-term architectural clarity.

## Notes

This ADR intentionally does **not** require all components to be “pure”.  
Instead, it enforces **explicit dependency boundaries**, which is a more practical and honest design principle for systems interacting with real-world storage.
