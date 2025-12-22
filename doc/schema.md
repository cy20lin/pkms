# v1 SQLite Schema（與 Identity Contract 對齊）

這份可以放在 /docs/design/schema.sql
或直接作為實作起點

```sql
CREATE TABLE pages (
    id INTEGER PRIMARY KEY,

    -- Identity
    file_id TEXT NOT NULL UNIQUE,
    file_uid TEXT,

    -- File info
    file_path TEXT,
    file_extension TEXT,
    file_size INTEGER,

    -- Content integrity (non-identity)
    file_hash_sha256 TEXT,

    -- Metadata
    title TEXT,
    origin_url TEXT,

    -- Temporal signals
    snapshot_datetime TEXT,
    file_created_datetime TEXT,
    file_modified_datetime TEXT,

    -- Content
    text TEXT,
    extra JSON
);

CREATE INDEX idx_pages_file_id ON pages(file_id);
CREATE INDEX idx_pages_file_uid ON pages(file_uid);
CREATE INDEX idx_pages_origin_url ON pages(origin_url);
```


## 設計說明（重點）

- file_id：唯一、人類錨點
- file_uid：允許 NULL（v1 不強制）
- origin_url：未來版本分組用
- extra：避免 schema 過早膨脹

## 

importance | added | 
context    | not added | free text, high entropy
title | add |
full text | add |

### title

A best-effort, human-readable label for display and search.

May be derived from content metadata, filename, or timestamps.

Not guaranteed to convey semantic meaning.