# ADR-0009 ADR Filename Convention -- with Explicit Delimiter

* **Status**: Accepted
* **Date**: 2025-12-23

> This ADR applies to project governance and documentation, not runtime PKMS behavior.

## Context

PKMS uses Architecture Decision Records (ADR) to document long-lived architectural and conceptual decisions.

As the number of ADR documents grows, a **stable, unambiguous, and tool-friendly filename convention** is required.
The filename must satisfy the following constraints:

* Clearly separate **ADR identity** (sequence number) from **human-readable title**
* Avoid ambiguity when parsed by tools or scripts
* Be safe across filesystems (Windows / Linux)
* Be robust when used in CLI, globbing, URLs, and Markdown links
* Avoid whitespace-related escaping issues
* Remain readable by humans

Naive formats such as:

```
ADR-0009 The title.md
ADR-0009-the-title.md
```

introduce ambiguity and/or operational friction, especially when filenames are processed programmatically.

Therefore, a clear delimiter and normalization strategy is required.


## Decision

ADR filenames SHALL use the following convention:

```
ADR-{4-digit-sequence}--{normalized-title}.md
```

Where:

* `ADR-{4-digit-sequence}` is the unique ADR identifier
* `--` (double dash) is a **reserved structural delimiter** separating identity and title
* `{normalized-title}` is a human-readable, **natural-language kebab-case** title
* `.md` is the Markdown extension

Example:

```
ADR-0009--adr-filename-convention-with-explicit-delimiter.md
```

## Title Normalization Rules

ADR filename titles are **not code identifiers**. They are human-oriented summaries rendered in a machine-safe form.

### Word Separation

* CamelCase or PascalCase identifiers MUST be **word-separated** before rendering
* Semantic boundaries MUST be preserved

Example:

```
IndexedDocument     -> indexed-document
HTTPRequest         -> http-request
IndexedHTMLDocument -> indexed-html-document
file_id             -> file-id
```

### Acronym Normalization

* Consecutive uppercase letters (length ≥ 2) SHALL be treated as a **single token**
* Acronyms SHALL NOT be split into individual letters
* Acronyms SHALL be rendered as lowercase

Examples:

| Original | Normalized |
| -------- | ---------- |
| HTML     | html       |
| HTTP     | http       |
| URL      | url        |
| UUID     | uuid       |
| PKMS     | pkms       |

❌ Invalid forms:

```
h-t-m-l
u-r-l
p-k-m-s
```

### Case Rules

* All filename tokens SHALL be lowercase
* Filename casing MUST NOT preserve code-level capitalization

### Separator Rules

* Words MUST be joined using a single hyphen (`-`)
* Structural separation between ADR ID and title MUST use `--`

### Underscore and other symbols Rules

* underscore or character from other symbol are treated like space

## Rationale

### Explicit Structural Separation

Using a **double dash (`--`)** provides a visually and mechanically clear boundary between:

* **Identity** (ADR number)
* **Description** (title)

This enables zero-ambiguity parsing using simple rules or regular expressions, for example:

```regex
^ADR-(\d{4})--(.+)\.md$
```

### Avoidance of Whitespace Issues

Spaces in filenames introduce friction in:

* Shell commands and scripts (quoting / escaping)
* Glob patterns
* URL encoding (`%20`)
* Markdown link portability
* Cross-tool interoperability

ADR files are **system-level artifacts**, not user content; therefore, they prioritize stability and machine-friendliness over natural language formatting.

### Tooling and Automation Readiness

The chosen format supports future automation, such as:

* ADR index generation
* CLI commands
* Programmatic ADR parsing
* Obsidian / Markdown cross-linking
* Chronological sorting by filename alone

### Consistency with PKMS Design Philosophy

PKMS explicitly separates:

* **Human-facing content** (resource filenames, notes)
* **System-facing identifiers and contracts** (IDs, schemas, ADRs)

ADR filenames belong to the latter category and therefore follow stricter rules.


## Alternatives Considered

### `ADR-0009 The title.md`

Rejected due to:

* Shell and scripting friction
  - Potential breakage for tools to process
* URL encoding issues (%20)
  - URL escape space character and it is hard to interpret for human
* Ambiguous parsing
* Inconsistent cross-platform behavior

Considered because:

* Comprehension friendly for human
* Though space in file is tricky to handle, but with modern tools they should handle file name with space correctly.
* Modern filesystem accept spaces in filename in general.

### `ADR-0009,the-title.md`

Use a symbol like comma as a seperator for the ADR ID and the title.

Rejected due to:

* URL encoding issues (%2C)
  - comma is a reserved character in URL
  - URL escape comma character and it is hard to interpret for human

### `ADR-0009-the-title.md`

Rejected due to:

* Ambiguity between ADR ID and title
* Difficulty in reliable programmatic parsing


### `ADR-0009__the-title.md` (double underscore)

<!-- Considered acceptable but not chosen because: -->
Rejected due to:

* Slightly lower readability compared to `--`
* Less visually expressive as a structural separator
* Use underscores to **seperate** words confuses users / developers
  - While `snake_case` **connect** words with underscores

May be reconsidered if `--` proves problematic in future tooling.


## Consequences

### Positive

* Unambiguous ADR identity and title separation
* Preserved semantic boundaries in filenames
* Simplified parsing and automation
* Improved long-term maintainability

### Negative

* Slightly more verbose filenames
* Requires contributors to follow a defined normalization rule

These costs are considered minimal and acceptable.


## Revision History

* 2025-12-22: Initial version, decision accepted
* 2025-12-23: Added explicit title normalization and acronym handling rules
