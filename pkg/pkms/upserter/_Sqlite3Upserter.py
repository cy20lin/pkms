from pkms.core.model import IndexedDocument, FilesDbRecord
from pkms.core.component.upserter import (
    Upserter,
    UpserterConfig,
    UpserterRuntime
)
from pkms.core.utility import *

from typing import Optional, Literal
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone


# ---------- utils ----------

def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()

# ---------- DB ----------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY,

    -- Identity
    file_id TEXT NOT NULL UNIQUE,
    file_uid TEXT,

    -- Location
    file_uri TEXT NOT NULL,

    -- Integrity
    file_size INTEGER NOT NULL,
    file_hash_sha256 TEXT NOT NULL,

    -- Classification
    file_extension TEXT NOT NULL,
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

CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
    title,
    text,
    content='files',
    content_rowid='id'
);

-- files_ai : after insert trigger to sync files -> files_fts
CREATE TRIGGER IF NOT EXISTS files_ai AFTER INSERT ON files BEGIN
  INSERT INTO files_fts(rowid, title, text)
  VALUES (new.id, new.title, new.text);
END;

-- files_ad : after delete trigger to sync files -> files_fts
CREATE TRIGGER IF NOT EXISTS files_ad AFTER DELETE ON files BEGIN
  INSERT INTO files_fts(files_fts, rowid, title, text)
  VALUES('delete', old.id, old.title, old.text);
END;

-- files_au : after update trigger to sync files -> files_fts
CREATE TRIGGER IF NOT EXISTS files_au AFTER UPDATE ON files BEGIN
  INSERT INTO files_fts(files_fts, rowid, title, text)
  VALUES('delete', old.id, old.title, old.text);
  INSERT INTO files_fts(rowid, title, text)
  VALUES (new.id, new.title, new.text);
END;
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
    -- record_created_datetime is insert-only
    record_updated_datetime = excluded.record_updated_datetime,
    file_created_datetime = excluded.file_created_datetime,
    file_modified_datetime = excluded.file_modified_datetime,
    text = excluded.text,
    extra = excluded.extra;
"""

import json
from datetime import datetime

def to_files_db_record(
    doc: IndexedDocument,
) -> FilesDbRecord:
    """
    Convert IndexedDocument to FilesDbRecord
    Pure function:
    same input -> same output
    """

    now_iso_ = now_iso()

    return FilesDbRecord(
        file_id=doc.file_id,
        file_uid=doc.file_uid,
        file_uri=doc.file_uri,
        file_size=doc.file_size,
        file_extension=doc.file_extension,
        file_hash_sha256=doc.file_hash_sha256,
        file_kind=doc.file_kind,
        importance=doc.importance,
        title=doc.title,
        origin_uri=doc.origin_uri,
        record_created_datetime=now_iso_,
        record_updated_datetime=now_iso_,
        file_created_datetime=doc.file_created_datetime,
        file_modified_datetime=doc.file_modified_datetime,
        text=doc.text,
        extra=json.dumps(doc.extra, ensure_ascii=False),
    )

from contextlib import contextmanager

class Sqlite3UpserterConfig(UpserterConfig):
    type: Literal['Sqlite3UpserterConfig'] = 'Sqlite3UpserterConfig'

class Sqlite3UpserterRuntime(UpserterRuntime):
    pass

class Sqlite3Upserter(Upserter):
    Config = Sqlite3UpserterConfig

    def __init__(self, config:Sqlite3UpserterConfig, runtime: Optional[Sqlite3UpserterRuntime] = None):
        super().__init__(config=config, runtime=None)
        assert self.config
        self._in_transaction = False
        self._connection = sqlite3.connect(config.db_path)
        self._connection.row_factory = sqlite3.Row
        self._init_db()
    
    def _init_db(self):
        """
        Initialize Database
        """
        self._connection.execute("PRAGMA journal_mode=WAL;")
        self._connection.executescript(SCHEMA_SQL)
        self._connection.commit()
    
    # DONE: Decide Should use [IndexedDocument] vs IndexedDocument as input => Use single IndexedDocument
    # DONE: Think wether using explicit curor or not, 
    def upsert(self, indexed_document: IndexedDocument):
        """
        Insert or update the indexed document to database

        - Auto-commit to database by default.
        - upsert() will not commit with transaction() context, this enable batch commit.

        To use with transaction context, you could upsert like following:

        ```python
        with upserter.transaction():
            for doc in docs:
                upserter.upsert(doc)
        ```
        
        :param self: Description
        :param indexed_document: Description
        :type indexed_document: IndexedDocument
        """
        if self._connection is None:
            raise RuntimeError("Upserter is closed")

        file_db_record: FilesDbRecord = to_files_db_record(indexed_document)
        file_db_record_dict: dict = file_db_record.model_dump()
        self._connection.execute(UPSERT_SQL, file_db_record_dict)
        if not self._in_transaction:
            self._connection.commit()

    @contextmanager
    def transaction(self):
        """
        Transaction context.

        - Inside the context, upsert() will NOT auto-commit.
        - On exit:
            - commit if no exception
            - rollback if exception raised
        """
        if self._connection is None:
            raise RuntimeError("Upserter is closed")

        if self._in_transaction:
            # Prevent nested transaction
            raise RuntimeError("Nested transaction is not supported")

        try:
            self._in_transaction = True
            self._connection.execute("BEGIN")
            yield self
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            self._in_transaction = False
    
    def close(self) -> bool:
        """
        Try close the internal connection to db if possible
        
        :return: Previous connection status, (Ture: Closed successfully, False: Closed already)
        :rtype: bool
        """
        has_connection = self._connection is not None
        if has_connection:
            self._connection.close()
            del self._connection
            self._connection = None
        return has_connection

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

