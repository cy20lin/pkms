# ADR-0025: File Resolution Status Naming and Semantics

## Status

**status**: Accepted  
**date**: 2026-01-21  

## Context

In the PKMS system, the `resolve` operation is responsible for determining and reporting
the **current, confirmed existence state** of a file-like resource.

The purpose of resolution is intentionally narrow:

- It reports what the system **knows to be true now**
- It does **not** diagnose failures
- It does **not** attempt repair or reconciliation
- It does **not** infer intent or future actions

Resolution may consult:

- Database records
- The filesystem vault (or backing storage)
- System invariants that establish existence or non-existence

The result must be:

- Deterministic
- Emotionally neutral
- Stable over time
- Suitable for both human and machine consumers

## Decision

The following `ResolutionStatus` enum is adopted:

```python
class ResolutionStatus(str, Enum):
    OK      = "OK"
    TRASHED = "TRASHED"
    DELETED = "DELETED"
    ABSENT  = "ABSENT"
```

## Semantics

### OK

- The file exists
- The database record and filesystem vault are consistent
- The file is accessible and in a good state

This is the normal, healthy resolution outcome.

### TRASHED

- A database record exists
- The file has been soft-deleted (trashed)
- The file may still exist physically, but is no longer considered active

This state represents a **reversible lifecycle decision**, not non-existence.

### DELETED

- A database record exists
- The backing file has been permanently deleted
- The resource is gone, but its historical record remains

This state communicates **known prior existence** with confirmed removal.

### ABSENT

- No database record exists
- No file exists in the filesystem vault
- The system has completed synchronization and can **confirm non-existence**

`ABSENT` is explicitly used instead of `MISSING` to avoid alarmist or investigative  
connotations.  
It represents **confirmed non-existence**, not uncertainty or failure.

## Rationale

### 1\. Resolution Reports Facts, Not Anomalies

The `resolve` API is designed to report factual system state.  
Conditions such as data corruption, partial loss, or invariant violations  
are intentionally excluded from this enum.

States like `DESYNCED`, `CORRUPT`, or `MOVED` describe **system anomalies**  
and belong to diagnostics or reconciliation layers, not resolution.

### 2\. Avoiding Ambiguous or Emotional Vocabulary

Terms such as `MISSING` or `PENDING` were rejected because they imply:

- Uncertainty
- Ongoing investigation
- Operational failure

By contrast, `ABSENT` communicates a calm, confirmed conclusion that aligns  
with normal resolution outcomes.

### 3\. Clear Distinction Between Lifecycle and Existence

The enum cleanly separates:

- **Lifecycle states** (`TRASHED`, `DELETED`)
- **Existence states** (`OK`, `ABSENT`)

This avoids overloading resolution with workflow or policy semantics.

### 4\. Long-Term Stability

The chosen statuses are:

- Unlikely to require renaming
- Independent of future workflow changes
- Compatible with audit, history, and garbage-collection logic

Additional states may be added later if real-world operation justifies them,  
but the current set intentionally remains minimal.

## Consequences

### Positive

- Simple, predictable resolution results
- Clear semantics for clients and agents
- Reduced risk of enum churn
- Clean separation of concerns

### Trade-offs

- Certain rare or anomalous conditions are not represented directly
- Additional diagnostics may be required outside of resolution

## Summary

The `ResolutionStatus` enum defines a minimal, stable vocabulary for reporting  
file existence and lifecycle outcomes.

It prioritizes:

- Confirmed knowledge over speculation
- Neutral system language over emotional phrasing
- Long-term semantic stability over completeness

This design ensures that `resolve` remains a reliable foundation  
for higher-level PKMS behaviors.
