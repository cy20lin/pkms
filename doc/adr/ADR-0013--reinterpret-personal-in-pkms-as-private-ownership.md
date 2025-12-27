# ADR-0013: Reinterpret "Personal" in PKMS as Private Ownership

**Status**: Deferred  
**Date**: 2025-12-25

> This ADR records a possible future reinterpretation of “Personal” in PKMS.
> The current implementation and design focus remain single-user and personal workflows.

## Context

The project name **PKMS** historically stands for *Personal Knowledge Management System*, a term that is widely recognized and familiar in the knowledge management domain.

As the system design evolved, PKMS has incorporated concepts such as:

- Owned vs External Resources
- Explicit ownership and trust boundaries
- Multi-device and potentially multi-actor usage
- URI-based addressing and resolution
- Local-first and user-controlled storage

These characteristics extend beyond the traditional interpretation of *Personal* as *single-user*.

At the same time, renaming the project would introduce unnecessary disruption, as **PKMS** is already an established and meaningful identifier.

## Decision

- The project name **PKMS** is retained.
- The term **Personal** in PKMS is reinterpreted to emphasize **ownership** and control rather than the number of users.
- *Personal* SHALL NOT be interpreted as strictly *single-user*.
- Documentation SHOULD clarify that *Personal* refers to **private ownership and trust boundary**.

## Rationale

- **Private ownership** aligns precisely with core system concepts such as:
  - Owned Resource
  - Ownership Boundary
  - Local-first storage
- The reinterpretation avoids premature or costly renaming while preserving conceptual clarity.
- The term *Private* generalizes naturally to:
  - Individual users
  - Families
  - Teams
  - Organizations
- This interpretation better reflects PKMS as a **knowledge infrastructure** rather than a UI-centric personal tool.

## Consequences

- Documentation (README, glossary, design docs) SHOULD explain this interpretation explicitly.
- The abbreviation **PKMS** remains stable across code, repository structure, and tooling.
- No changes are required to runtime behavior, data models, or APIs.
- Future contributors and users are expected to understand PKMS as ownership-centric rather than user-count-centric.

## Notes

This ADR formalizes a semantic clarification rather than a functional change.
It serves as a stable reference point for terminology consistency across the project.

## Related ADRs

- ADR-0003: Treat IndexedDocument as a Stable Contract Boundary
- ADR-0005: Use URI Instead of Path in Persistent Models
- ADR-0011: Terminology - Owned Resource vs External Resource