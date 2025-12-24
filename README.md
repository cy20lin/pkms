# PKMS – Personal Knowledge Management System

PKMS is a **local‑first, file‑centric personal knowledge indexing system**.

Its goal is not to replace your editor, note‑taking app, or file system, but to **index, normalize, and search heterogeneous personal resources** (HTML snapshots, Markdown notes, PDFs, media files, etc.) in a stable, extensible, and automation‑friendly way.

PKMS is designed around **explicit identity contracts**, **declarative configuration**, and **boring, reliable storage (SQLite)**.

## 🔖 Table Of Contents

- [PKMS – Personal Knowledge Management System](#pkms--personal-knowledge-management-system)
  - [🔖 Table Of Contents](#-table-of-contents)
  - [✨ Core Ideas](#-core-ideas)
    - [1. Local‑first, offline‑friendly](#1-localfirst-offlinefriendly)
    - [2. Files are first‑class citizens](#2-files-are-firstclass-citizens)
    - [3. Explicit identity model](#3-explicit-identity-model)
    - [4. Declarative configuration](#4-declarative-configuration)
  - [🧱 Architecture Overview](#-architecture-overview)
    - [Modules](#modules)
  - [📁 Project Structure](#-project-structure)
  - [🗂️ SQLite Schema](#️-sqlite-schema)
    - [Time semantics](#time-semantics)
  - [🧩 Indexer Model](#-indexer-model)
  - [⚙️ Configuration](#️-configuration)
  - [🚧 Project Status](#-project-status)
  - [🧠 Non‑Goals](#-nongoals)
  - [🛣️ Future Directions](#️-future-directions)
  - [✍️ Philosophy](#️-philosophy)

## ✨ Core Ideas

### 1. Local‑first, offline‑friendly

- Files live on your disk
- Index lives in SQLite
- No mandatory cloud, no SaaS dependency

### 2. Files are first‑class citizens

PKMS treats files as **resources**, not just text blobs:

- Human‑readable file IDs
- Stable URIs
- Clear distinction between snapshots and editable content

### 3. Explicit identity model

Each indexed file has **three layers of identity**:

| Layer      | Purpose                          | Example                |
| ---------- | -------------------------------- | ---------------------- |
| `id`       | Database primary key             | `INTEGER`              |
| `file_id`  | Human‑visible, stable identifier | `2025-12-22-0001.html` |
| `file_uid` | Strong unique content identifier | `sha256 / uuid / cuid` |

This avoids overloading a single ID with incompatible responsibilities.

### 4. Declarative configuration

Indexing behavior is defined via **JSON config**, not code:

- Global and per‑collection indexer mappings
- Explicit globbing rules
- Future‑proof extension points

## 🧱 Architecture Overview

```text
Filesystem
   │
   ▼
Globber  ──►  Indexer  ──►  Upserter  ──►  SQLite
            (per file)           (idempotent)

                         ▲
                         │
                       Searcher (future)
```

### Modules

| Module     | Responsibility                             |
| ---------- | ------------------------------------------ |
| `globber`  | Discover files using glob patterns         |
| `indexer`  | Convert files into structured indexed data |
| `upserter` | Insert / update records in SQLite          |
| `cli`      | Orchestrate pipelines from command line    |
| `gui`      | Web UI (NiceGUI, future)                   |

## 📁 Project Structure

```text
pkms/
└─ pkg/
   ├─ pkms/
   │  ├─ __init__.py
   │  ├─ globber.py
   │  ├─ indexer/
   │  │  ├─ __init__.py
   │  │  └─ html_indexer.py
   │  ├─ upserter.py
   │  ├─ cli/
   │  │  └─ main.py
   │  └─ gui/   # future
   ├─ doc/
   │  ├ design/
   │  └ ...
   ├─ script/
   │  └ ...
   └─ test/
      └ pkg/
         ├ test/
         │  └ pkms/
         └ testing/
```

## 🗂️ SQLite Schema

The primary table is `files` (name may evolve to `resources` in future versions).

Key characteristics:

- SQLite is the **source of truth** for indexing state
- No hidden metadata magic
- Timestamps are explicitly managed by PKMS

### Time semantics

| Column                    | Meaning                   |
| ------------------------- | ------------------------- |
| `record_created_datetime` | Set only on first insert  |
| `record_updated_datetime` | Updated on every upsert   |
| `file_created_datetime`   | File system creation time |
| `file_modified_datetime`  | File system modified time |

## 🧩 Indexer Model

Indexers are responsible for **interpreting a file**, not deciding *where* it goes.

Different indexers exist for different formats:

- HTML snapshots
- Markdown notes
- PDFs
- Open Document Format (ODF) files
- Audio / Video (future)

Indexers:

- Are pure (input → structured output)
- Accept configuration
- Do **not** talk to the database

## ⚙️ Configuration

PKMS uses a JSON‑based configuration file.

Highlights:

- Versioned (`version: "0.1.0"`)
- Global indexer mappings
- Per‑collection overrides
- Clear inheritance rules (`config_base`)

See **Config Spec v0.1** for the full contract.

## 🚧 Project Status

**Early development (v0.1)**

Current focus:

- globber
- indexer
- upserter
- CLI

Deferred:

- search UI
- URI handlers
- cross‑device sync
- version graph / deduplication

## 🧠 Non‑Goals

PKMS intentionally does **not** aim to:

- Replace Obsidian / editors
- Enforce a single note format
- Auto‑generate content via LLMs
- Act as a cloud sync service

It is a **substrate**, not a product.

## 🛣️ Future Directions

- SQLite FTS integration
- URI rewrite / pkms:// scheme
- Versioned resources
- Multi‑device indexing
- Optional external search engines (Meilisearch)

## ✍️ Philosophy

> Boring infrastructure scales better than clever magic.
>
> Explicit contracts age better than implicit assumptions.
>
> Files outlive applications.

PKMS is built with these principles in mind.
