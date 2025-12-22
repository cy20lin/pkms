CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY,

    -- Identity
    file_id TEXT NOT NULL UNIQUE,
    file_uid TEXT,

    -- Location
    file_uri TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_extension TEXT NOT NULL,

    -- Integrity
    file_hash_sha256 TEXT NOT NULL,

    -- Classification
    file_kind TEXT NOT NULL,

    -- Metadata
    importance INTEGER NOT NULL DEFAULT 0,
    title TEXT NOT NULL,
    origin_uri TEXT,

    -- Time
    record_created_datetime TEXT NOT NULL,
    record_updated_datetime TEXT NOT NULL,
    file_created_datetime TEXT NOT NULL,
    file_modified_datetime TEXT NOT NULL,

    -- Content
    text TEXT,
    extra JSON
);
-- 

CREATE INDEX idx_pages_file_id ON files(file_id);
CREATE INDEX idx_pages_file_uid ON files(file_uid);
CREATE INDEX idx_pages_origin_uri ON files(origin_uri);
