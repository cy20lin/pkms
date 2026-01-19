# PKMS Architecture Overview

This document describes the high-level architecture of the PKMS (Personal Knowledge Management System), its layering, dependency rules, and the rationale behind major structural decisions.

The goal of this architecture is to support a **human-centric knowledge system** that is:

* Explicit about user intent
* Observable and debuggable
* Incrementally evolvable
* Friendly to future automation and agents

## Design Principles

1. **Clear Responsibility Boundaries**
   Each layer has a single, well-defined responsibility.

2. **Intent Over Convenience**
   User actions (e.g. ingestion) must be explicit and inspectable, not implicit side effects.

3. **Progressive Capability**
   The system should function meaningfully even when only partial metadata or indexing is complete.

4. **Multiple Interfaces, One Core Logic**
   CLI, Web UI, API, and future agents should share the same application logic.

5. **Future-Agent-Compatible by Design**
   Even without implementing agents now, the architecture should already be compatible with non-human actors.

## Layered Architecture

The PKMS architecture is organized as a dependency stack. Each layer may only depend on layers below it.

```
core
  ↑
components
  ↑
app.{ingest, resolve, search, represent}
  ↑
(rest)api.{ingest, resolve, search, represent}
web(ui).{ingest, resolve, search, represent}
cli.{ingest, resolve, search, represent}
```

## Layer Descriptions

### 1. `core`

**Responsibility:**

* Fundamental domain concepts
* Pure logic and utilities
* No IO, no framework, no environment assumptions

**Characteristics:**

* Stateless or explicitly state-driven
* Fully testable in isolation
* Long-term stable

Examples:

* Addressing semantics
* Identity models
* Utility functions

### 2. `components`

**Responsibility:**

* Pluggable, reusable building blocks
* Declarative configuration + runtime behavior

**Characteristics:**

* Each component has:

  * Config (pure data)
  * Runtime (behavior)
* No orchestration responsibility

Examples:

* Globber
* Screener
* Stamper (identity / integrity)
* Indexer
* Resolver
* Searcher
* Upserter

### 3. `app.*` (Application Layer)

**Responsibility:**

* Orchestrate components into meaningful workflows
* Represent *user intent* as executable processes

**Key Insight:**

> The `app` layer is where the system understands *why* something happens, not just *how*.

Submodules:

* `app.ingest`

  * Ingestion task model
  * Progressive stamping and indexing
  * Observable ingestion states

* `app.resolve`

  * Addressing and resolution semantics

* `app.search`

  * Search workflows and result shaping

* `app.represent`

  * Representation logic (HTML, snapshots, etc.)

This layer is **interface-agnostic** and shared by CLI, Web, API, and future agents.

### 4. Interface Layers

These layers adapt application logic to specific interaction modes.

#### `cli.*`

* Explicit, scriptable user intent
* Debugging and power-user workflows

#### `web(ui).*`

* Human-facing interaction
* Visual inspection of ingestion state
* Browsing, searching, and representation

#### `(rest)api.*`

* Programmatic access
* Enables automation and future agent usage

**Important:**

These layers:

* Must not contain business logic
* Must not duplicate orchestration
* Are replaceable without affecting the core system

## Ingestion as a First-Class Concept

A key architectural decision is treating **ingestion** as a first-class, observable process.

Reasons:

* Ingestion represents explicit user intent
* It may be partial, progressive, or long-running
* Its state must be inspectable (pending, in-progress, failed, completed)

This is why ingestion lives in `app.ingest`, not inside components or web-only code.

## Why Web Is Not the App

Previously, web functionality bundled:

* resolve
* search
* represent

As ingestion gained importance, this model no longer scaled.

By separating:

* `app.*` → *what the system does*
* `web(ui).*` → *how humans interact with it*

The architecture becomes:

* Cleaner
* More testable
* Agent-ready

## Future Considerations

This architecture intentionally leaves room for:

* Agent interfaces using the same `app.*` layer
* Finer-grained access control and sensitivity levels
* Encrypted collections and conditional processing modes
* UI hints when crossing trust boundaries (e.g. external links)

These are **not implemented yet**, but the architecture already has a place for them.

## Summary

PKMS is structured around a simple but strict idea:

> **One core logic, many interfaces, explicit user intent, and observable state.**

This architecture favors clarity and longevity over short-term convenience, making it suitable for a long-lived personal system that can grow alongside its user.
