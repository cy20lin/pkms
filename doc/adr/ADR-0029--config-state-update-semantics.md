
# ADR-0029: Config & State Update Semantics

**Status**: Draft  
**Date**: 2026-01-29  

## Context

PKMS distinguishes **Config**, **State**, and **Runtime** as separate concerns:

- **Config** describes user intent and desired behavior
- **State** captures system-produced, serializable execution results
- **Runtime** represents live, mutable execution with external resources

While this separation is established (see ADR-0016 and ADR-0028), ambiguity remained around:

- How Runtime should be constructed when Config and/or State are missing
- Whether Runtime can exist with Config only
- How State should be updated when Config changes
- How backward compatibility and partial upgrades should be handled
- How to avoid implicit mutation or hidden coupling between Config and State

This ADR defines **explicit semantics** for how Config and State interact during Runtime construction and update

## Decision

### 1\. Conceptual Roles

#### 1.1 Config

- Declarative
- Immutable
- User-authored
- Describes *intent* and *policy*
- May change between executions

#### 1.2 State

- System-authored
- Serializable
- Represents *materialized results* of prior execution
- May be incompatible with new Config

#### 1.3 Runtime

- Live execution object
- Owns mutable resources
- May be constructed from:

  - Config only

  - State only

  - Config + State

Runtime is the **only entity** allowed to mutate State

### 2\. Runtime Construction Invariants

A Runtime MUST satisfy the following invariants:

1. Runtime MUST be constructible with **Config only**

2. Runtime MUST be constructible with **State only**

3. Runtime MUST be able to **produce a State**

4. State MUST be serializable without Runtime

5. Runtime MUST NOT require State to exist

6. Runtime MUST NOT mutate Config

This ensures:

- First-run initialization is possible
- Recovery from persisted state is possible
- Config and State lifecycles are decoupled

### 3\. State Update Semantics

State evolution is governed by an explicit update operation:

```python
state_ = Runtime.update_state(
    config: Optional[Config],
    state: Optional[State],
)
```

This function is **pure** (no external side effects) and defines the canonical transition rules.

#### 3.1 Update Rules

| config | state | Semantics |
| --- | --- | --- |
| `None` | `None` | Produce initial state using built-in defaults |
| `Config` | `None` | Produce initial state from Config |
| `None` | `State` | Identity mapping (no-op) |
| `Config` | `State` | Attempt compatible state migration |

Rules:

- Absence of Config MUST NOT invalidate existing State
- Presence of Config MAY invalidate or reshape State
- Incompatible updates MUST fail explicitly

Silent corruption or implicit fallback is forbidden

### 4\. Runtime Loading Model

Runtime construction is split into **two explicit phases**:

#### 4.1 State Resolution

```python
state_ = Runtime.update_state(config, state)
```

- No external resources
- Deterministic
- Testable in isolation

#### 4.2 Runtime Instantiation

```python
runtime = Runtime.from_state(
    state_,
    *,
    logger: Logger,
)
```

- Acquires external resources
- Binds logger
- Initializes live execution

This separation allows:

- Offline state migration
- Dry-run validation
- Clear error boundaries

### 5\. State as the Source of Truth for Runtime

Once constructed:

- Runtime internal state MUST originate from `State`
- Runtime MUST NOT retain hidden configuration-only mutations
- `runtime.get_state()` MUST reflect the full serializable state

Config MAY be retained for introspection, but MUST NOT be mutated or relied upon as live state

### 6\. Analogy: Hyperparameters vs Parameters

This model intentionally mirrors patterns from systems like PyTorch:

| PKMS | ML Analogy |
| --- | --- |
| Config | Hyperparameters |
| State | Model Parameters |
| Runtime | Live Model Instance |

Just as changing hyperparameters does not automatically make old parameters valid:

- Some Config changes MAY invalidate State
- Migration MAY be partial or impossible
- Failure is preferable to silent reuse

### 7\. Logger Interaction

- Logger is injected at Runtime construction time
- Logger MAY influence Runtime behavior
- Logger MUST NOT be part of State
- Logger configuration belongs to Config

This preserves State portability and replayability

## Rationale

This design:

- Makes Config–State interaction explicit and auditable
- Prevents hidden coupling and accidental mutation
- Enables robust recovery, migration, and validation workflows
- Supports advanced features:

  - state versioning

  - dry-run upgrades

  - multi-runtime orchestration

  - agent-controlled execution

## Consequences

### Positive

- Deterministic runtime initialization
- Clear upgrade semantics
- Testable state transitions
- Strong guarantees against silent corruption

### Trade-offs

- Requires explicit migration logic
- Some Config changes may force State reset

These trade-offs are accepted in favor of correctness and long-term maintainability

## Notes

This ADR intentionally avoids prescribing **how** migration is implemented.  
It only defines **when**, **with what inputs**, and **under what guarantees** state transitions occur.
