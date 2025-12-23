# Architecture Decision Records (ADR)

This document contains:

1. A **standard ADR template** for this PKMS project
2. **Guidelines on when and how to write a new ADR**

It is intended for both current and future developers and contributors.


## Table of Contents

- [Architecture Decision Records (ADR)](#architecture-decision-records-adr)
  - [Table of Contents](#table-of-contents)
  - [1. ADR Template](#1-adr-template)
    - [Context](#context)
    - [Decision](#decision)
    - [Rationale](#rationale)
    - [Alternatives Considered](#alternatives-considered)
    - [Consequences](#consequences)
    - [Notes (Optional)](#notes-optional)
    - [Revision History (Optional)](#revision-history-optional)
  - [2. When to Write an ADR](#2-when-to-write-an-adr)
    - [You SHOULD write an ADR when:](#you-should-write-an-adr-when)
    - [You SHOULD NOT write an ADR when:](#you-should-not-write-an-adr-when)
    - [Practical Heuristics](#practical-heuristics)
  - [3. ADR Lifecycle](#3-adr-lifecycle)
  - [4. Recommended Placement](#4-recommended-placement)
  - [5. Final Principle](#5-final-principle)


## 1. ADR Template

Use this template whenever you make an architectural or conceptual decision that has long-term impact.

```
# ADR-XXXX: <Short, Descriptive Title>

* **Status**: Proposed | Accepted | Deprecated | Superseded
* **Date**: YYYY-MM-DD
* **Decision Makers**: <optional>
* **Related**: ADR-YYYY, ADR-ZZZZ (if any)
```


### Context

Describe the problem or situation that led to this decision.

Include:

* What was unclear, difficult, or risky
* Constraints (technical, personal, time, tooling, OS, scale)
* What triggered the need to decide *now*

Avoid describing the solution here.


### Decision

State **clearly and concisely** what was decided.

This should be a single, unambiguous statement.

Example:

> PKMS will use SQLite as the system of record for indexed metadata.


### Rationale

Explain **why** this decision was made.

Cover:

* Key reasons
* Trade-offs considered
* Why this option was preferred over alternatives

This section is the most important for future readers.


### Alternatives Considered

List other options that were seriously considered.

For each alternative:

* Brief description
* Why it was not chosen

Example:

* Meilisearch as primary store — rejected due to persistence and schema control concerns
* PostgreSQL — rejected due to operational overhead for v1


### Consequences

Describe the outcomes of this decision.

Include both:

* **Positive consequences** (what becomes simpler or possible)
* **Negative consequences / costs** (what becomes harder, what is postponed)

Be honest; future-you will thank you.


### Notes (Optional)

Additional thoughts, open questions, or follow-ups that are intentionally deferred.


### Revision History (Optional)

* YYYY-MM-DD: Initial version
* YYYY-MM-DD: Clarified rationale


## 2. When to Write an ADR

Write an ADR **only when a decision is structural and long-lived**.

Use the following rules of thumb.


### You SHOULD write an ADR when:

* You choose **one model over another** (e.g. snapshot vs readonly, file vs resource)
* You introduce or freeze an **identity scheme** (IDs, UIDs, hashes)
* You decide **where truth lives** (filesystem vs DB vs index)
* You define **boundaries between modules** (globber / indexer / upserter)
* You commit to a **data contract** or schema that migrations will depend on
* You intentionally **defer** a capability (e.g. versioning, sync, dedup)
* You say *"we will not do X in v1"*

If reversing the decision later would be painful → write an ADR.

### You SHOULD NOT write an ADR when:

* Choosing variable names or small refactors
* Writing one-off scripts or experiments
* Fixing bugs
* Making decisions that are easy to undo

If the decision only affects a single file or function → no ADR.


### Practical Heuristics

Ask yourself:

> “If I come back to this project in 6 or 12 months, will I ask *why* this is like this?”

If the answer is **yes**, write an ADR.

Another heuristic:

> “Does this decision constrain future features?”

If yes → ADR-worthy.


## 3. ADR Lifecycle

1. **Proposed**: Written but not yet fully accepted (during exploration)
2. **Accepted**: Actively followed by the codebase
3. **Deprecated**: Still true for history, but no longer recommended
4. **Superseded**: Replaced by a newer ADR (must reference the new one)

Never delete ADRs — they are part of project memory.


## 4. Recommended Placement

```
/doc/adr/
  ADR-0001-sqlite-as-system-of-record.md
  ADR-0002-identity-model.md
  ADR-0003-snapshot-vs-editable.md
```

Number ADRs sequentially; numbers are identifiers, not importance.


## 5. Final Principle

**ADR is not bureaucracy.**

ADR is a tool to:

* Reduce cognitive load
* Preserve intent
* Make future changes safer

If writing an ADR feels annoying, it probably means the decision matters.
