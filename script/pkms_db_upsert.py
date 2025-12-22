#!/usr/bin/env python3
import argparse
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


# ---------- utils ----------

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON: {path} ({e})")


def ensure_non_empty_title(data: dict) -> str:
    """
    Title fallback chain.
    Guaranteed to return non-empty string.
    """
    if data.get("title"):
        return data["title"].strip()

    extra = data.get("extra") or {}
    html = extra.get("html") or {}
    if html.get("title"):
        return html["title"].strip()

    file_id = data.get("file_id", "UNKNOWN")
    return f"Untitled {file_id}"


def classify_file_kind(file_extension: str) -> str:
    """
    v1 classification rules.
    """
    ext = file_extension.lower()

    if ext in {".html", ".pdf", ".mp3", ".mp4", ".mkv", ".wav"}:
        return "snapshot"
    if ext in {".md", ".txt", ".odt"}:
        return "editable"

    # default conservative choice
    return "snapshot"


# ---------- DB ----------

SCHEMA_SQL = """
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
"""

UPSERT_SQL = """
INSERT INTO files (
    file_id,
    file_uid,
    file_uri,
    file_size,
    file_extension,
    file_hash_sha256,
    file_kind,
    importance,
    title,
    origin_uri,
    record_created_datetime,
    record_updated_datetime,
    file_created_datetime,
    file_modified_datetime,
    text,
    extra
) VALUES (
    :file_id,
    :file_uid,
    :file_uri,
    :file_size,
    :file_extension,
    :file_hash_sha256,
    :file_kind,
    :importance,
    :title,
    :origin_uri,
    :record_created_datetime,
    :record_updated_datetime,
    :file_created_datetime,
    :file_modified_datetime,
    :text,
    :extra
)
ON CONFLICT(file_id) DO UPDATE SET
    file_uid = excluded.file_uid,
    file_uri = excluded.file_uri,
    file_size = excluded.file_size,
    file_extension = excluded.file_extension,
    file_hash_sha256 = excluded.file_hash_sha256,
    file_kind = excluded.file_kind,
    importance = excluded.importance,
    title = excluded.title,
    origin_uri = excluded.origin_uri,
    record_updated_datetime = excluded.record_updated_datetime,
    file_created_datetime = excluded.file_created_datetime,
    file_modified_datetime = excluded.file_modified_datetime,
    text = excluded.text,
    extra = excluded.extra;
"""


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(SCHEMA_SQL)
    conn.commit()


# ---------- mapping ----------

def map_json_to_record(data: dict) -> dict:
    """
    Map parsed JSON into SQLite-ready record.
    """
    required = [
        "file_id",
        "file_uri",
        "file_size",
        "file_extension",
        "file_hash_sha256",
        "file_created_datetime",
        "file_modified_datetime",
    ]
    for k in required:
        if k not in data:
            raise ValueError(f"Missing required field: {k}")

    title = ensure_non_empty_title(data)
    file_kind = classify_file_kind(data["file_extension"])

    now = now_iso()

    record = {
        "file_id": data["file_id"],
        "file_uid": data.get("file_uid"),
        "file_uri": data["file_uri"],
        "file_size": int(data["file_size"]),
        "file_extension": data.get("file_extension", ""),
        "file_hash_sha256": data["file_hash_sha256"],
        "file_kind": file_kind,
        "importance": int(data.get("importance", 0)),
        # "title": title,
        "title": data.get('title', ''),
        "origin_uri": data.get("origin_uri"),
        "record_created_datetime": now,
        "record_updated_datetime": now,
        "file_created_datetime": data["file_created_datetime"],
        "file_modified_datetime": data["file_modified_datetime"],
        "text": data.get("text"),
        "extra": json.dumps(data.get("extra")) if data.get("extra") is not None else None,
    }

    return record


# ---------- CLI ----------

def index_files(db_path: Path, inputs: list[Path], dry_run: bool = False) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    init_db(conn)

    indexed = 0

    try:
        for path in inputs:
            data = load_json(path)
            record = map_json_to_record(data)

            if dry_run:
                print(f"[DRY-RUN] would index: {record['file_id']}")
            else:
                conn.execute(UPSERT_SQL, record)
                indexed += 1

        if not dry_run:
            conn.commit()

    finally:
        conn.close()

    print(f"Indexed {indexed} file(s)")


def parse_args():
    p = argparse.ArgumentParser("pkms-index")
    p.add_argument("--db", required=True, help="SQLite database path")
    p.add_argument("--input", required=True, nargs="+", help="JSON file(s)")
    p.add_argument("--dry-run", action="store_true", help="Validate only")
    return p.parse_args()


def main():
    args = parse_args()

    inputs: list[Path] = []
    for pattern in args.input:
        matches = list(Path().glob(pattern))
        if not matches:
            print(f"Warning: no match for {pattern}", file=sys.stderr)
        inputs.extend(matches)

    if not inputs:
        print("No input files", file=sys.stderr)
        sys.exit(1)

    index_files(
        db_path=Path(args.db),
        inputs=inputs,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
