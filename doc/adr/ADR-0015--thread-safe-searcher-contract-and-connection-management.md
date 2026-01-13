# ADR-0015 — Thread-Safe Searcher Contract and Connection Management

**Status**: Accepted  
**Date**: 2025-12-29 
**Related ADRs**:

- ADR-0003 Treat IndexedDocument as a Stable Contract Boundary
- ADR-0006 Modular Pipeline (Globber / Indexer / Upserter)
- ADR-0014 ADR Lifecycle and Status Model

## Context

PKMS introduces a `Searcher` abstraction to provide text-based and structured retrieval over indexed resources.  
In the current implementation, `Sqlite3Searcher` uses SQLite as the underlying storage engine.

During integration with a Flask backend, a runtime error occurred:

> `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread`

This surfaced a fundamental architectural question:

- Should a `Searcher` instance be **thread-affine**, requiring one instance per thread?
- Or should `Searcher` be **thread-safe**, encapsulating all concurrency and connection management internally?

Given PKMS’s design philosophy—**stable contracts, explicit boundaries, and hiding infrastructure complexity**—this decision must be made explicit and enforced.


## Decision

### 1\. Searcher Thread-Safety Contract

**All `Searcher` implementations MUST be safe to call concurrently from multiple threads.**

- A `Searcher` instance **MAY be shared across threads**
- Callers **MUST NOT** manage database connections, thread affinity, or synchronization
- Threading, connection pooling, or caching strategies are **implementation details**


### 2\. Connection Management Responsibility

- Database connections (e.g. SQLite connections) are **not part of the public contract**
- A `Searcher` implementation MAY:
  - Open a new connection per call
  - Use thread-local connection caching
  - Use an internal connection pool
- These choices MUST NOT affect:
  - The `Searcher` interface
  - The semantics of `.search(...)`


### 3\. Interface Stability

The `Searcher` interface SHALL remain stable regardless of backend changes:

- SQLite → other embedded engines
- Local DB → remote search service
- Single-process → multi-process deployments


## Rationale

### Why NOT per-thread Searcher instances?

While feasible, a thread-affine Searcher would:

- Leak execution model concerns (threads) into domain contracts
- Increase cognitive load for users and integrators
- Introduce fragile, convention-based correctness
- Complicate Flask, GUI, scheduler, and background task integration

This contradicts PKMS’s core principle of **pushing complexity inward and stabilizing boundaries outward**.

### Why thread-safe Searcher?

A thread-safe Searcher:

- Preserves a clean, minimal abstraction:
  > “Given a query, return matching indexed knowledge”
- Enables safe reuse across:
  - Flask request handlers
  - CLI tools
  - GUI backends
  - Background jobs
- Allows internal optimization without breaking callers

## Consequences

### Positive

- Clear and enforceable contract
- Safer integration with multi-threaded frameworks (Flask, GUI servers)
- Future-proof for alternative storage/search backends
- Cleaner mental model for developers

### Trade-offs

- Slightly more complexity inside Searcher implementations
- Requires explicit testing for concurrency behavior

These trade-offs are acceptable and localized.

## Implementation Notes

- Searcher implementations SHOULD document their internal strategy
- Tests MUST cover concurrent access patterns
