# PKMS Config Specification v0.1

> Status: Draft (v0.1)
>
> This document defines the configuration file format for PKMS indexing pipeline.
> The config acts as a **contract** between user intent and PKMS runtime behavior.

---

## 1. Design Principles

* **Declarative**: Describe *what* to index, not *how* to execute it.
* **Composable**: Global defaults with collection-level overrides.
* **Deterministic**: Same config + same input → same indexed result.
* **Extensible**: New indexers, globbers, upserters can be added without breaking schema.
* **Local-first**: v0.1 assumes local filesystem resources.

---

## 2. Top-Level Structure

```jsonc
{
  "version": "0.1.0",
  "name": "",
  "description": "",
  "indexer_mapping": { /* global */ },
  "collections": [ /* collection list */ ]
}
```

### 2.1 version (required)

* Type: `string`
* Format: Semantic Versioning
* Meaning: Config schema version

Example:

```json
"version": "0.1.0"
```

---

### 2.2 name / description (optional)

* Type: `string | null`
* User-facing metadata only
* No semantic meaning to PKMS runtime

---

## 3. Global Indexer Mapping

Defines default indexer configuration per file extension.

```jsonc
"indexer_mapping": {
  ".html": {
    "module": "pkms.indexer.HtmlIndexer",
    "config": { /* optional */ }
  }
}
```

### 3.1 Key: file extension

* Type: `string`
* Must include leading dot (`.html`, `.md`)
* Case-insensitive

---

### 3.2 IndexerBuildingConfig

```jsonc
{
  "module": "pkms.indexer.HtmlIndexer",
  "config_base": "global",
  "config": { }
}
```

#### Fields

| Field       | Required | Description                         |
| ----------- | -------- | ----------------------------------- |
| module      | yes      | Python import path to Indexer class |
| config_base | no       | Base config to inherit from         |
| config      | no       | Indexer-specific configuration      |

---

### 3.3 config_base semantics

Possible values:

| Value   | Meaning                                       |
| ------- | --------------------------------------------- |
| null    | No base config                                |
| builtin | Indexer-defined builtin defaults              |
| global  | Global indexer_mapping config                 |
| default | Implementation-defined (defaults to `global`) |

**Merge rule**:

```
final_config = deep_merge(base_config, config)
```

* Objects: deep merge
* Lists: replace

---

## 4. Collections

A collection defines a **processing unit**:

* Resource scope
* Globbing rules
* Indexing policy

```jsonc
"collections": [
  {
    "name": "HTML Webpages",
    "description": null,
    "base_path": "/path/to/webpages/dir",
    "globber": { },
    "indexer_mapping": { },
    "upserter": { }
  }
]
```

---

### 4.1 base_path (required)

* Type: `string`
* Meaning: OS filesystem path
* Semantics:

  * Not a URI
  * Used directly by globber

> Note: `base_uri` is intentionally deferred to future versions.

---

### 4.2 `globber`

Defines how files are discovered.

```jsonc
"globber": {
  "patterns": ["**/*.html"],
  // "exclude": ["**/.git/**"]
}
```

#### Fields

| Field    | Required | Description                         |
| -------- | -------- | ----------------------------------- |
| patterns | yes      | Glob patterns relative to base_path |
<!-- | exclude  | no       | Exclusion glob patterns             | -->

* Globbing uses filesystem paths
* Order is implementation-defined

---

### 4.3 Collection-level indexer_mapping

Overrides or extends global indexer mapping.

```jsonc
"indexer_mapping": {
  ".html": {
    "module": "pkms.indexer.HtmlIndexer",
    "config_base": "global",
    "config": { }
  }
}
```

Resolution order:

1. Collection indexer_mapping
2. Global indexer_mapping
3. Indexer builtin defaults

---

### 4.4 `upserter`

Defines database write behavior.

```jsonc
"upserter": {
  "db_path": "pkms.db"
}
```

* Schema and SQL logic are **out of scope** of config
* Upserter is responsible for:

  * INSERT / UPSERT
  * Timestamp management
  * Conflict resolution

---

## 5. Indexer Contract (Conceptual)

Each Indexer MUST:

* Be instantiable via Python import
* Accept:
  * file_path
  * resolved config
* Return an IndexedDocument object

```yaml
IndexedDocument:
  file_id
  file_uid
  file_hash_sha256
  title
  text
  metadata
```

Properties:

* Deterministic
* Side-effect free (except cache usage)

---

## 6. Versioning & Compatibility

* v0.x: schema may change without backward compatibility
* v1.0:

  * Stable field meanings
  * Strict validation

---

## 7. Non-Goals (v0.1)

* Remote URI crawling
* Distributed indexing
* Search configuration
* Permission / ACL modeling
* AI inference policies

---

## 8. Future Extensions (Non-Normative)

* base_uri support
* Named indexer profiles
* Conditional indexer routing
* Searcher / retriever config
* GUI integration metadata

---

End of Spec
