# ADR-0014: Define ADR Lifecycle and Status Semantics

**Status**: Accepted  
**Date**: 2025-12-27

## Context

As PKMS evolves, Architectural Decision Records (ADRs) are used not only to capture accepted architectural decisions, but also to record explored, rejected, or postponed ideas.

Without a clearly defined lifecycle and shared understanding of ADR statuses, the meaning of each ADR may become ambiguous over time, increasing cognitive load for future maintenance, design iteration, and automation.

Therefore, a clear, minimal, and intention-revealing ADR lifecycle is required.

This lifecycle should:

- Be simple enough for a single-maintainer project
- Capture decision intent and finality
- Preserve historical reasoning
- Avoid premature over-structuring

## Decision

PKMS adopts the following **ADR lifecycle statuses**:

### 1. Proposed

A decision has been formally documented and is awaiting evaluation or commitment.

Characteristics:

- The idea is concrete and worth recording
- No implementation commitment is implied
- May transition to Accepted, Rejected, or Postponed

### 2. Accepted

The decision has been agreed upon and is considered part of the system’s architectural truth.

Characteristics:

- Affects implementation, documentation, and future decisions
- New designs SHOULD conform to this ADR
- May later transition to Superseded

### 3. Rejected

The decision has been explicitly considered and decided against.

Characteristics:

- The idea is not to be pursued
- Preserves reasoning to avoid repeated discussions
- Does not imply the idea was invalid, only unsuitable

### 4. Deferred

The decision is valuable but intentionally delayed. It is neither accepted nor rejected and may be revisited whe condition change.

Characteristics:

- Not rejected, but not actionable at present
- Commonly used for future-scope or speculative directions
- May transition back to Proposed when revisited
- Status name `deferred` is preferred over `postponed`.
  - As `deferred` sounds intentional and formal in technical context.
  - It implies the decision was **reviewed** and a **conscious** choice was made to push it to a later date.

### 5. Superseded

An Accepted ADR has been replaced by a newer ADR.

Characteristics:

- Maintained for historical traceability
- MUST reference the ADR that supersedes it
- No longer authoritative

Example:

```markdown
**Status**: Superseded by ADR-0000
```

## Explicitly Excluded Statuses

The following statuses are intentionally not adopted at this time:

- Draft: Considered redundant with version control and pre-ADR discussion, a ADR document commit into `doc/adr` is considered as non-draft ADR document.
- Withdrawn: Semantically overlaps with Rejected in a single-maintainer context.
- Deprecated: Reserved for future use when backward compatibility or migration policies are required.
- Archived: Superseded and Rejected ADRs already fulfill archival needs.

These may be revisited if project scale or governance requirements change.


## Rationale

- This lifecycle balances expressiveness and simplicity:
- Avoids overloading ADRs with process-heavy states
- Aligns with PKMS’s current scope and maturity
- Supports future evolution without locking in premature constraints
- Makes decision intent explicit and reviewable

## Consequences

- All ADRs MUST declare one of the defined statuses
- Contributors SHOULD update ADR status when decision intent changes
- Historical decisions remain visible and explainable
- Tooling and automation may rely on these statuses as stable semantics