
from pkms.upserter._Sqlite3Upserter import UPSERT_SQL
from pkms.core.model import FilesDbRecord
from pkms.core.utility import assert_sql_model_aligned

def test_file_db_record_matches_upsert_sql():
    assert_sql_model_aligned(
        sql=UPSERT_SQL,
        model=FilesDbRecord,
    )

import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from pkms.core.model import IndexedDocument
from pkms.upserter import Sqlite3Upserter
Sqlite3UpserterConfig = Sqlite3Upserter.Config

# --------------------------
# helpers
# --------------------------

def now_iso() -> str:
    return datetime.now().isoformat()

def make_doc(file_id: str, title: str = "title") -> IndexedDocument:
    return IndexedDocument(
        file_id=file_id,
        file_uid=None,
        file_uri=f"file:///tmp/{file_id}.txt",
        file_size=256,
        file_hash_sha256="01234566789asdfef01234566789asdfef", # dummy hash
        file_extension=".txt",
        file_kind="snapshot",
        file_created_datetime=now_iso(),
        file_modified_datetime=now_iso(),
        index_created_datetime=now_iso(),
        index_updated_datetime=now_iso(),
        title=title,
        importance=0,
        origin_uri=None,
        text="hello",
        extra={},
    )

# --------------------------
# fixtures
# --------------------------

@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"

@pytest.fixture
def upserter(db_path: Path):
    config = Sqlite3UpserterConfig(db_path=db_path.as_posix())
    u = Sqlite3Upserter(config)
    yield u
    u.close()

# --------------------------
# tests
# --------------------------

def test_single_upsert(upserter: Sqlite3Upserter):
    doc = make_doc("file-1")
    upserter.upsert(doc)

    conn = sqlite3.connect(upserter.config.db_path)
    cur = conn.execute("SELECT file_id, title FROM files")
    row = cur.fetchone()

    assert row[0] == "file-1"
    assert row[1] == "title"


def test_upsert_is_idempotent(upserter: Sqlite3Upserter):
    doc1 = make_doc("file-1", title="v1")
    doc2 = make_doc("file-1", title="v2")

    upserter.upsert(doc1)
    upserter.upsert(doc2)

    conn = sqlite3.connect(upserter.config.db_path)
    cur = conn.execute("SELECT title FROM files WHERE file_id = ?", ("file-1",))
    row = cur.fetchone()

    assert row[0] == "v2"


def test_transaction_batch_commit(upserter: Sqlite3Upserter):
    docs = [make_doc(f"file-{i}") for i in range(3)]

    with upserter.transaction():
        for d in docs:
            upserter.upsert(d)

    conn = sqlite3.connect(upserter.config.db_path)
    cur = conn.execute("SELECT COUNT(*) FROM files")
    count = cur.fetchone()[0]

    assert count == 3


def test_transaction_rollback_on_error(upserter: Sqlite3Upserter):
    good = make_doc("good")
    bad = make_doc("bad")

    # violate NOT NULL constraint intentionally
    bad.file_uri = None  # type: ignore

    with pytest.raises(Exception):
        with upserter.transaction():
            upserter.upsert(good)
            upserter.upsert(bad)

    conn = sqlite3.connect(upserter.config.db_path)
    cur = conn.execute("SELECT COUNT(*) FROM files")
    count = cur.fetchone()[0]

    assert count == 0


def test_close_is_idempotent(upserter: Sqlite3Upserter):
    assert upserter.close() is True
    assert upserter.close() is False

    with pytest.raises(RuntimeError):
        upserter.upsert(make_doc("file-x"))

# --------------------------
# script entry point
# --------------------------

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__]))
