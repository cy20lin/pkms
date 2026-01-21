# ADR-0024: ScreeningStatus Naming and Semantics

**Status**: Accepted
**Date**: 2026-01-21  

## Context

The PKMS ingestion pipeline includes a **Screener** stage responsible for evaluating whether a resource (e.g. file) can be ingested automatically into the system.

The Screener inspects properties such as:

- File location
- FileStamp (file id, uid, sha256, size, ctime, mtime, inode)
- File name conventions
- File content (e.g. policy violations, privacy risks)

The Screener **does not perform content curation or editing**, and it does not assume the presence of a submitter who can immediately revise inputs.  
Its responsibility is strictly to determine whether the system can **safely and confidently make an automated decision**.

As a result, the Screener must return a small, stable set of result states that clearly express **decision authority**, not workflow intent.

---

## Decision

The following `ScreeningStatus` enum is adopted:

```python
class ScreeningStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
```

### Semantics

- **APPROVED**  
    The Screener determines that all automated checks pass and the resource is safe to ingest without human involvement.

- **REJECTED**  
    The Screener determines that the resource violates explicit rules or policies and must not be ingested.  
    This is a terminal decision.

- **ESCALATED**  
    The Screener intentionally abstains from making an automated decision and escalates the decision to a human operator.  
    This state indicates uncertainty or policy edge cases, not failure.

## Rationale

### 1\. Decision Ownership over Workflow Prescription

The Screener's responsibility is to answer:

> *Can the machine decide safely?*

It is **not** responsible for prescribing subsequent human actions (e.g. review, revision, confirmation).  
`ESCALATED` expresses a change in decision ownership without implying what the human must do next.

### 2\. Avoiding Overloaded or Misleading Terms

Several alternative names were considered and intentionally rejected:

- **REQUIRES\_REVIEW**  
    Implies that the resource has already been reviewed once or that a specific review workflow is mandated.

- **REQUIRES\_REVISE / REQUIRES\_REVISION**  
    Assumes modification is necessary and introduces semantic collision with file versioning concepts (`rev`, `revision`) common in VCS and content lineage systems.

- **PENDING**  
    Ambiguous between "not yet processed" and "awaiting human decision", and therefore unsuitable as a screening result.

By contrast, **ESCALATED** has a precise and established meaning in systems design:  
*decision authority has been elevated to a higher (human) level*.

### 3\. Long-Term Vocabulary Stability

`ESCALATED` is intentionally abstract and infrastructure-oriented:

- It does not encode assumptions about UI, workflow, or policy evolution.

- It remains valid even as human review processes change.

- It allows future expansion via structured metadata (e.g. reasons, evidence, recommendations) without modifying the enum.

Example:

```json
{
  "status": "ESCALATED",
  "reason": "NAMING_NONCONFORMING",
  "evidence": {...}
}
```

## Consequences

### Positive

- Clear separation between **automated decisions** and **human-mediated decisions**

- Reduced risk of semantic drift or future renaming

- Clean integration with ingestion pipelines, agents, and batch workflows

### Trade-offs

- Downstream systems must consult additional metadata (e.g. reason codes) to determine specific human actions

- Slightly less descriptive than workflow-specific terms, by design

## Notes

- `ESCALATED` is a **screening result**, not a pipeline state.

- Pipeline states such as `PENDING`, `BLOCKED`, or `INGESTING` are defined separately and remain orthogonal.

## Summary

`ESCALATED` was chosen to represent **intentional machine abstention** and **decision escalation to humans**, while avoiding semantic collisions with review workflows, revision/versioning concepts, and pipeline state ambiguity.

This choice prioritizes long-term clarity, extensibility, and correctness in PKMS infrastructure design.
