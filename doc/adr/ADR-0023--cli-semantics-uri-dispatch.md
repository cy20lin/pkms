
# ADR-0023: CLI Semantics & URI Dispatch

**Status**: Draft (OS part needs dissucusion)  
**Date**: 2026-01-21  
**Context**: PKMS Core Architecture  
**Decision Scope**: Command Line Interface (CLI), URI handling, dispatch semantics

## Context

PKMS exposes multiple interaction surfaces:

- Command Line Interface (CLI)
- Web UI
- (Future) OS-level URI handlers (`pkms://`)
- (Future) AI agents

A core requirement is that **PKMS URIs (`pkms://...`) remain stable, semantic, and environment-agnostic**, while different frontends (CLI, Web, OS handler) may present or act on resolved resources differently.

During implementation of `pkms.cli.resolve` and related commands, a design question emerged:

- What should CLI commands output?
- How should `pkms://` URIs be handled when invoked from the operating system?
- Where should “open / view / dispatch” behavior live?
- How strict should CLI semantics be?

This ADR formalizes the separation of concerns between **resolution**, **presentation**, and **dispatch**, and defines the semantic contract of the PKMS CLI.

## Decision

### 1\. CLI Semantics

The PKMS CLI **follows Unix-style semantics by default**:

- **Input**: command-line arguments, stdin
- **Output**:
  - `stdout`: machine-readable output (JSON)
  - `stderr`: human-readable diagnostics
- **Exit code**:
  - `0`: success
  - non-zero: failure with semantic meaning

#### Example

```bash
pkms resolve pkms:///file/id:2024-01-01-xxxx
```

```json
{
  "status": "ok",
  "uri": "pkms:///file/id:2024-01-01-xxxx.txt",
  "resolved": {
    "file_id": "2024-01-01-xxxx",
    "file_extension": ".txt",
    "file_kind": "editable",
    "title": "Example Note",
    "revision": "HEAD",
    "file_location": {
      "scheme":"file",
      "authority": "",
      "base_path": "/path/to/collection-dir",
      "sub_path": "sub/path/to/file.txt",
    },
    "file_type": "REGULAR"
  }
}
```

The CLI **does not automatically open files, launch browsers, or perform UI actions**. Its responsibility is to **describe reality**, not act on it.

### 2\. Resolver Is Pure and Side-Effect Free

The resolver:

- Accepts a `pkms://` URI
- Returns structured semantic data (`ResolvedTarget`)
- Has **no knowledge** of:
  - CLI vs Web vs OS
  - human vs agent
  - presentation or interaction

This ensures:

- Testability
- Determinism
- Reusability across all frontends

### 3\. Dispatch Is Explicit and Separate

Actions such as:

- opening a file
- rendering HTML
- redirecting to a browser
- revealing a path in a file manager

are **not resolver responsibilities**.

Instead, PKMS introduces the concept of **dispatch**.

#### Dispatch semantics

> “Given a resolved target and an execution environment, decide *how* to act.”

Dispatch is environment-specific and may vary by frontend.

### 4\. Module Responsibilities

The following layering is established:

```pgsql
pkms.core
  └─ addressing / resolver (pure semantics)

pkms.app.dispatch
  └─ environment-agnostic dispatch logic (view / edit / reveal)

pkms.cli.resolve
  └─ CLI adapter → JSON output

pkms.cli.dispatch
  └─ CLI wrapper around app.dispatch (optional UX behavior)

pkms.web.dispatch
  └─ Web-specific dispatch (HTML, redirect, iframe, etc.)

(future)
pkms.os.handler
  └─ OS-level URI handler for pkms://
```

The CLI may expose `dispatch` commands, but these are considered **semi-CLI UX adapters**, not pure data commands.

### 5\. Handling `pkms://` at the OS Level

OS-level URI handling (`pkms://...`) is treated as a **separate concern** from CLI parsing.

Key principles:

- The OS handler should:
  - invoke PKMS with a URI
  - delegate to `pkms.app.dispatch`
- It must not duplicate resolver logic
- It must not embed business rules

This keeps the URI semantics stable while allowing different user experiences.

### 6\. Strict vs Relaxed CLI Semantics

Commands are categorized as:

| Category | Examples | Semantics |
| --- | --- | --- |
| **Pure CLI** | `resolve`, `search`, `inspect` | Strict stdin/stdout/JSON |
| **Semi-CLI (UX)** | `dispatch`, `open`, `view` | May trigger side effects |

This distinction is intentional and explicit.

## Consequences

### Positive

- Clear separation of concerns
- Stable URI semantics across environments
- CLI remains composable with other tools
- Future OS and agent integrations are unblocked
- Avoids “CLI that secretly launches UI” anti-pattern

### Trade-offs

- Requires explicit dispatch commands
- Slightly more concepts (resolve vs dispatch)
- UX actions require intentional invocation

These trade-offs are considered acceptable and aligned with PKMS’s long-term goals.

## Related Decisions / Future Work

- ADR: Addressing & Resolver Semantics
- ADR: Ingestion Task Model & Observability
- ADR: PKMS Onboarding & Configuration Layout
- ADR: Security Baseline (external link handling, referrer policy)
- Future ADR: OS URI Handler Integration

## Summary

> **CLI describes. Resolver understands. Dispatch acts.**

By keeping these roles distinct, PKMS maintains semantic clarity, composability, and long-term extensibility across human, system, and agent-driven interactions.
