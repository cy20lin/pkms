# ADR-0003: Treat IndexedDocument as a Stable Contract Boundary

**Status**: Accepted
**Date**: 2025-12-22

## Context

Indexing pipelines vary widely by file type:

* HTML parsing
* Markdown processing
* Audio transcription

However, persistence and search must remain stable.

## Decision

Define a **normalized IndexedDocument model** as the output of all indexers.

## Rationale

* Decouples indexers from database schema
* Enables testing indexers independently
* Allows schema evolution without reindexing logic changes

## Consequences

* Indexers must perform normalization
* Some metadata loss is accepted intentionally