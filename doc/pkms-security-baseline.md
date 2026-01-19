# PKMS Security Baseline

## 1. Purpose

This document defines the **baseline security model** for PKMS.

It does **not** aim to provide military‑grade or enterprise‑grade security guarantees. Instead, it establishes a **clear, explicit, and inspectable security posture** aligned with PKMS’s core philosophy:

> PKMS is a personal system where the user is both the owner and the primary threat model designer.

The baseline focuses on:

- Preventing *unintentional information leakage*
- Making *security‑relevant behavior explicit and observable*
- Preserving *user intent* over implicit automation
- Providing a foundation that can evolve without breaking trust

## 2. Threat Model (Baseline Assumptions)

### 2.1 Trusted Environment Assumptions

At baseline, PKMS assumes:

- The PKMS server runs on **user‑controlled infrastructure**
- Access is limited to **trusted devices**, optionally connected via VPN
- The local operating system and storage are **trusted**
- Physical access attacks are **out of scope**

These assumptions may be relaxed in future designs, but are **explicitly assumed** at this stage.

### 2.2 Out‑of‑Scope Threats (Baseline)

The following are *not* addressed by the baseline:

- Host OS compromise
- Malicious browser extensions
- Hardware keyloggers
- Advanced side‑channel attacks
- Nation‑state adversaries

This is intentional. The baseline optimizes for *clarity and correctness*, not maximal paranoia.

## 3. Core Security Principles

### 3.1 Explicit Intent Over Implicit Inference

PKMS **never infers** user intent in security‑sensitive operations.

Instead:

- The user must **explicitly signal** intention or context
- The system reacts deterministically to that signal

This principle applies across:

- Ingestion
- Addressing
- Search
- Presentation
- External boundary crossing

### 3.2 Security Is a System Behavior, Not a Feature

Security in PKMS is not a toggle, plugin, or permission checkbox.

It is expressed through:

- Data flow constraints
- Presentation behavior
- Default isolation
- Controlled boundary crossings

### 3.3 Zero‑Trust Boundary, Trusted Interior

PKMS adopts a **hybrid trust model**:

- **Interior (PKMS system)**: trusted by default
- **Exterior (external websites, services, networks)**: zero‑trust

Crossing this boundary is always treated as a **security‑relevant event**.

## 4. Data Classification (Baseline)

At baseline, PKMS treats:

- All collections
- All files
- All databases

as operating under the **same access control level**.

However, the system explicitly acknowledges the existence of **higher‑sensitivity content**, including but not limited to:

- Personal health records
- Identification documents
- Financial information
- Legal records

The baseline does not yet enforce differentiated access, but **reserves architectural space** for it.

## 5. Ingestion Security Semantics

### 5.1 Ingestion Is Observable

All ingestion activities must be:

- Inspectable
- Attributable
- State‑driven

Ingestion state may be surfaced via:

- Filesystem artifacts
- Database records
- Task status APIs
- UI indicators

Hidden background ingestion is explicitly discouraged.

### 5.2 Partial Visibility Is Allowed

A file may exist in one of several states:

- Identity known, content unknown
- Content indexed, file missing
- Historical content available, current file absent

This is not treated as a security failure.

PKMS prioritizes **truthful representation of known state** over enforced consistency.

## 6. Addressing & Resolution Security

### 6.1 Addressing Is Referential, Not Authoritative

A PKMS URI:

- Identifies a logical resource
- Does not guarantee current file presence
- May resolve to historical or partial data

This prevents information loss and avoids unsafe assumptions.

### 6.2 Resolver Failure Is Non‑Destructive

Resolution failure:

- Does not erase historical knowledge
- Does not trigger forced re‑ingestion
- Does not silently redirect

The system must surface *what is known* and *what is missing* distinctly.

## 7. External Boundary Protection

### 7.1 No External Dependencies by Default

The PKMS web interface:

- MUST be self‑contained
- MUST NOT load external JS, CSS, fonts, or images
- MUST NOT depend on third‑party CDNs

This ensures predictable data flow and eliminates passive leakage.

### 7.2 Referrer Protection

PKMS enforces referrer protection using **multiple layers**:

- HTTP response headers:
  - `Referrer-Policy: no-referrer`
- HTML meta tags where applicable
- Controlled redirect endpoints

This prevents leakage of:

- Internal URIs
- File identifiers
- User navigation patterns

### 7.3 Controlled External Navigation

When the user chooses to access an external resource:

- The system SHOULD prevent referrer leakage
- The system MAY warn the user
- The system SHOULD make the boundary crossing explicit

Future versions may provide stronger affordances here.

## 8. Safety Signal Concept

### 8.1 Safety Signal Definition

PKMS supports the concept of a **Safety Signal**:

> An explicit signal from the user indicating their current intention or risk context.

This is:

- NOT authentication
- NOT authorization
- NOT identity verification

It is an **operational context signal**.

### 8.2 Possible Effects of a Safety Signal

Depending on system configuration, a safety signal MAY influence:

- Search scope
- Result visibility
- Caching behavior
- Rendering fidelity
- Export or sharing capabilities

### 8.3 Signaling Mechanisms

The baseline does not mandate a specific mechanism.

Possible forms include:

- Passphrases
- Time‑limited modes
- UI toggles
- Hardware presence
- Agent‑mediated signals

The key requirement is **explicit user action**.

## 9. Future Considerations (Non‑Binding)

The following are explicitly deferred:

- Fine‑grained collection access control
- Encrypted per‑collection indexes
- Agent‑specific permission models
- Multi‑user collaboration security

These may be addressed in future ADRs. e.g.

- ADR：Safety Signal Semantics
- ADR：Agent vs Human Interaction Boundary
- ADR：Search Visibility Policy（而不是 permission）
- ADR：Presentation Degradation for Sensitive Content

## 10. Design Philosophy Summary

PKMS security is built on the belief that:

- Silent security is dangerous
- Over‑automation erodes trust
- Users deserve truthful system behavior

The baseline favors:

- Explicitness over convenience
- Inspectability over opacity
- Evolution over premature hardening

This document defines the **minimum trustworthy posture** upon which PKMS may grow.
