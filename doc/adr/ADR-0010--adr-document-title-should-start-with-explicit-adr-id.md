# ADR-0010: ADR Document Title should start with Explicit ADR id

**Status**: Accepted
**Date**: 2025-12-23

> This ADR applies to project governance and documentation, not runtime PKMS behavior.

## Context

When writing ADR documents in markdown file, it is tedious to manually rename file according [ADR-0009 ADR Filename Convention](./ADR-0009--adr-filename-convention-with-explicit-delimiter.md). It is preferable to have a script and automate such job for developers. 

The ADR id should somehow be retrievable from the document, for the script to automate the normalization and rename ADR document process.


## Decision

- ADR id SHOULD be placed at the beginning of the title
- ADR id `ADR-<adr_id>` follows a colon `:` and then follows the document title composing into a ADR document markdown title
    ```markdown
    # ADR-0010: ADR Document Title
    ```
- If filename *ADR id* conflicts with document title *ADR id*, tooling MUST trust the document title *ADR id*.

## Rationale

- Enforce *ADR id* in the content of document so that the reader could clearly see what ADR they are reading and/or referring to.
- Scripting tool may rename the title thus retrieve the *ADR id* from file name may be unstable. 

## Consequences

- Clear Title with *ADR id* for reader reference
- Stable location for automation tool to retrieve *ADR id*
