# libinfo.jsonc Specification

## Purpose

`libinfo.jsonc` describes the provenance, versioning, and integrity of an embedded library used inside PKMS.

This file is designed to:

- Be **Human-readable** (for review and auditing)
- Be **Machine-readable** (for tooling, verification, automation)
- ~~Be **Stable over time** (independent of build systems or package managers)~~
  - Doesn't intend to be stable in mind though, just to help reduce some work
- Enable library files integrity verification
  - To ensure there is no accident modification on the library files
- Enable library upgrade without manual work
  - Human make mistakes, let the tools do it for you.

It acts as a **self-contained manifest** for vendored or embedded code.

## Design Goals

- Reduce Cognitive Cost for mantaining embedded libraries
- Fetch library files from the origin via proper tooling
- Track **where code came from**
- Record **exact source version**
- Enable **integrity verification**
- Support **local embedding**, not dynamic dependency resolution
- Avoid tight coupling to PyPI / npm / system package managers

## File Format

- Encoding: UTF-8
- Format: JSON with comments (`.jsonc`)
- Location: Root directory of the embedded library

Example path:

```text
pkms/lib/markdown_to_html/libinfo.jsonc
```

## Top-Level Fields

### `name` (string, required)

Logical name of the embedded library.

```jsonc
"name": "markdown_to_html"
```

### `description` (string, optional)

Human-readable description of the library’s purpose.

```jsonc
"description": "Markdown to HTML converter for PKMS preview"
```

### `repo` (string, optional)

Version control repository URL of the source code, if applicable.

This field answers: *“Where can the original source be found?”*

```jsonc
"repo": "git@github.com:user/markdown_to_html.git"
```

### `commit` (string, optional)

Exact commit hash used as the source.

```jsonc
"commit": "abcd1234ef567890..."
```

### `tag` (string, optional)

Optional tag or release name associated with the commit.

```jsonc
"tag": "v0.2.0"
```

### `license` (string, optional)

Declares intended usage of the embedded code.

This is **not a legal contract**, but an internal usage declaration.

Recommended values:

- `private-use`
- `proprietary`
- `unknown`

Example:

```jsonc
"license": "private-use"
```

## `files` Section

### Purpose of files property

The `files` array lists **all files embedded from the source**, together with integrity information.

This allows tools to:

- Verify file integrity
- Detect accidental or unauthorized changes
- Reconstruct provenance during audits

### `files[].from` (string, required)

Path of the file **in the original source repository**.

This is informational and used for traceability.

```jsonc
"from": "markdown_to_html.py"
```

### `files[].to` (string, required)

Target path of the file **relative to the directory containing `libinfo.jsonc`**.

This is the actual embedded location.

```jsonc
"to": "markdown_to_html.py"
```

### `files[].size` (integer, required)

File size in bytes at the time of embedding.

Used for quick sanity checks.

```jsonc
"size": 12345
```

### `files[].sha256` (string, required)

SHA-256 hash of the file contents.

Used for integrity verification.

```jsonc
"sha256": "0000000000000000000000000000000000000000000000000000000000000000"
```

## Intended Usage

`libinfo.jsonc` is intended to be used by:

- Developers reviewing embedded code
- Tooling that verifies integrity
- Auditing or debugging workflows
- Future automation (updates, provenance checks)

It is **not** intended to:

- Replace a package manager
- Perform dynamic dependency resolution
- Encode build instructions

## Notes

- Comments are allowed and encouraged (`.jsonc`)
- Fields may be extended in the future without breaking compatibility
- Absence of `repo` or `commit` does not invalidate the file

## Summary

`libinfo.jsonc` provides a lightweight, explicit, and auditable way to embed external or internal libraries into PKMS while preserving provenance and integrity — without introducing unnecessary tooling complexity.
