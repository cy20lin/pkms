# ADR-0011: Terminology – Owned Resource vs External Resource

**Status**: Accepted
**Date**: 2025-12-24

## Context

The PKMS system operates across multiple storage locations and systems,
including local filesystems, user-managed servers, cloud storage services,
and third-party platforms.

Previously, terms such as *local*, *remote*, or *personal* were considered
to describe resource locations. However, these terms introduce ambiguity:

- *Local* incorrectly limits the scope to a single machine
- *Personal* implies a single user and does not scale to group or organizational use
- *Remote* describes network topology rather than trust or control

The system requires terminology that accurately reflects **ownership,
control, and trust boundaries**, rather than physical location or number of users.

## Decision

The PKMS system SHALL adopt the following terminology:

- **Owned Resource**
- **External Resource**

### Owned Resource

An *Owned Resource* is a resource that is **fully controlled and trusted**
by the PKMS operator, regardless of its physical location or hosting model.

Ownership implies:

- Full read and write access
- Authority over lifecycle management (creation, update, deletion, backup)
- Trust in data integrity and availability
- Responsibility for failure handling and recovery

Owned Resources MAY reside on:

- Local filesystems
- User-managed or team-managed servers
- Rented or managed cloud storage services
- Any infrastructure where the operator retains effective control

### External Resource

An *External Resource* is a resource that is **not fully controlled**
by the PKMS operator and whose lifecycle, availability, or integrity
depends on a third-party system.

External Resources are considered **untrusted by default** and typically
require explicit acquisition (fetching, exporting, snapshotting) before
being ingested into the PKMS system.

Examples include:

- Web services
- Messaging platforms
- Third-party SaaS applications

## Rationale

- Clearly separates **trust and control boundaries** from physical location
- Avoids assumptions about single-user or single-machine usage
- Supports future expansion to team or organization-level PKMS deployments
- Aligns terminology across ingestion, indexing, and storage pipelines

## Consequences

- Documentation and diagrams should use *Owned* and *External* instead of
  *local*, *remote*, or *personal*
- Fetcher components conceptually transform External Resources into
  Owned Resources
- Storage abstractions may evolve without changing core terminology
