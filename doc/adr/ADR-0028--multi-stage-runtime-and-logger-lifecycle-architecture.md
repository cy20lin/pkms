# ADR-0028: Multi-Stage Runtime and Logger Lifecycle Architecture

**Status**: Draft  
**Date**: 2026-01-29  

## Context

As PKMS grows into a multi-layered system supporting application-wide behavior, per-workspace execution, and multiple domain components, the system must address several intertwined concerns:

- Configuration vs. runtime responsibility
- Explicit lifecycle boundaries (bootstrap → app → workspace)
- Logging behavior during early startup and runtime transitions
- Clear ownership of mutable state and external resources
- Avoiding implicit global singletons while preserving usability

Earlier designs suffered from ambiguity around:

- When configuration is loaded relative to logging availability
- Where logger instances should be constructed
- Whether `App` should be treated as a Component or a Runtime
- How workspace-specific behavior (including logging) should override or extend application defaults

This ADR formalizes a **multi-stage runtime model** and defines how **Config**, **State**, **Runtime**, and **Logger** interact across those stages.

## Decision

### 1\. Explicit Runtime Stages

The application lifecycle is divided into **explicit, ordered stages**, each with clearly defined responsibilities and logging behavior:

```csharp
[BOOTSTRAP]
[APP_STARTING]
[APP_STARTED]
[WORKSPACE_STARTING]
[WORKSPACE_STARTED]
```

Each stage progressively unlocks more capabilities while preserving observability and failure transparency.

### 2\. Bootstrap Stage

**Purpose**:  
Enable diagnostics before configuration, environment, or filesystem state is available.

**Characteristics**:

- Logger: **bootstrap logger**
- Output: **stderr only**
- Configuration: none
- State: none

Rules:

- No file I/O beyond argument parsing
- No config or state loading
- No persistent resources

This logger is intentionally minimal and short-lived.

### 3\. App Stage

#### 3.1 App Starting

**Purpose**:  
Resolve inputs required to construct the application runtime.

Actions:

- Parse CLI arguments
- Read environment variables
- Load `AppConfig`
- Load optional `AppState`

Logger:

- Still uses **bootstrap logger**

#### 3.2 App Started

**Purpose**:  
Establish application-level runtime and infrastructure.

Actions:

- Construct **App logger** using `AppConfig.logger`
- Create `AppRuntime`
- Discard bootstrap logger

Logger behavior:

- stderr (always)
- optional file sinks as defined by config

The App logger becomes the **default logger** for subsequent stages.

### 4\. Workspace Stage

#### 4.1 Workspace Starting

**Purpose**:  
Resolve and prepare the active workspace.

Actions:

- Resolve workspace root
- Load `WorkspaceConfig`
- Load `WorkspaceState`
- Merge logger configuration:

  - base = `AppConfig.logger`

  - override = `WorkspaceConfig.logger` (if any)

Logger:

- App logger (still active)

#### 4.2 Workspace Started

**Purpose**:  
Activate workspace-scoped execution.

Actions:

- Construct **Workspace logger**
- Create `WorkspaceRuntime`

Logger behavior:

- Inherits structure from App logger
- May add or override sinks (e.g. workspace-local log files)
- App logger may continue to exist but is no longer default

### 5\. Config vs State vs Runtime

#### 5.1 Config

- Declarative
- Immutable
- User-authored
- Pydantic models
- Describes *intent*, not execution

Examples:

- `AppConfig`
- `WorkspaceConfig`
- `LoggerConfig`

Config MUST NOT:

- Construct loggers
- Open files or connections
- Depend on runtime state

#### 5.2 State

- Serializable
- Mutable across executions
- Written by the system
- Restorable

Examples:

- `AppState`
- `WorkspaceState`

#### 5.3 Runtime

A **Runtime** represents execution-scoped capabilities.

Properties:

- Owns external resources (loggers, DB connections, caches)
- Not serializable
- Created by the application
- May produce or update State

Examples:

- `AppRuntime`
- `WorkspaceRuntime`

### 6\. Logger Ownership Model

#### Decision: **Loggers are Runtime Capabilities**

- Loggers are **constructed by Runtime**, not by Components
- Logger configuration lives in Config
- Logger instances live in Runtime

This ensures:

- Clear lifecycle ownership
- Correct handling of early startup logs
- No hidden global logger state

### 7\. App Is an Orchestrator, Not a Component

The `App` object:

- Is **not** a domain Component
- Is **not** a ComponentRuntime
- Owns lifecycle orchestration only

Responsibilities:

- Stage transitions
- Runtime construction
- Config and State loading
- Logger handoff

This avoids overloading Component semantics and keeps domain logic isolated.

### 8\. Logger Flow Invariant

The system enforces a **top-down logger flow**:

```markdown
bootstrap logger
    ↓
app logger
    ↓
workspace logger
    ↓
component-bound loggers
```

Rules:

- No upward dependency
- No implicit global access
- All components receive loggers via Runtime

## Rationale

This design:

- Makes lifecycle boundaries explicit
- Solves the “parse-time logging” problem cleanly
- Prevents config from performing side effects
- Avoids global singletons without sacrificing ergonomics
- Supports future extensions:
  - multiple workspaces
  - remote runtimes
  - agent-based execution
  - structured logging and tracing

## Consequences

### Positive

- Clear mental model for contributors
- Deterministic logging behavior
- Testable config/state/runtime separation
- Workspace-specific observability without hacks

### Trade-offs

- Slightly more abstraction
- Requires discipline in respecting stage boundaries

These trade-offs are accepted in exchange for long-term architectural clarity and correctness.

## Notes

This ADR intentionally treats **logging as infrastructure**, not domain logic.  
By placing loggers in Runtime rather than Components or Config, PKMS gains explicit lifecycle control without leaking implementation details into the domain layer.
