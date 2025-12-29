import sqlite3
import pytest

from pkms.upserter._Sqlite3Upserter import Sqlite3Upserter
from pkms.core.model import IndexedDocument
from pkms.core.interface import Upserter
import datetime

# --------------------------
# helpers
# --------------------------

def now_iso() -> str:
    return datetime.datetime.now().isoformat()

def make_doc(file_id: str, title: str = "title", text: str="hello") -> IndexedDocument:
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
        text=text,
        extra={},
    )


def fts_search(conn: sqlite3.Connection, query: str) -> list[str]:
    cur = conn.execute(
        """
        SELECT files.file_id
        FROM files_fts
        JOIN files ON files_fts.rowid = files.id
        WHERE files_fts MATCH ?
        ORDER BY rank
        """,
        (query,),
    )
    return [row["file_id"] for row in cur.fetchall()]


# --------------------------
# fixtures
# --------------------------

@pytest.fixture
def upserter(tmp_path):
    db_path = tmp_path / "fts.db"
    config = Upserter.Config(db_path=db_path.as_posix())
    u = Sqlite3Upserter(config)
    yield u
    u.close()


@pytest.fixture
def conn(upserter):
    conn = sqlite3.connect(upserter.config.db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


# --------------------------
# tests
# --------------------------

def test_fts_basic_search(upserter, conn):
    upserter.upsert(make_doc("file-1", text="hello sqlite fts"))
    upserter.upsert(make_doc("file-2", text="nothing relevant"))

    result = fts_search(conn, "sqlite")
    assert result == ["file-1"]


def test_fts_updates_on_upsert(upserter, conn):
    upserter.upsert(make_doc("file-1", text="old content"))
    upserter.upsert(make_doc("file-1", text="new searchable content"))

    result_old = fts_search(conn, "old")
    result_new = fts_search(conn, "searchable")

    assert result_old == []
    assert result_new == ["file-1"]


def test_fts_transaction_rollback(upserter, conn):
    good = make_doc("good", text="visible")
    bad = make_doc("bad", text="should rollback")

    # force failure
    bad.file_uri = None  # violate NOT NULL

    with pytest.raises(Exception):
        with upserter.transaction():
            upserter.upsert(good)
            upserter.upsert(bad)

    assert fts_search(conn, "visible") == []
    assert fts_search(conn, "rollback") == []


def test_fts_batch_upsert(upserter, conn):
    docs = [
        make_doc("a", text="alpha beta"),
        make_doc("b", text="beta gamma"),
        make_doc("c", text="gamma delta"),
    ]

    with upserter.transaction():
        for d in docs:
            upserter.upsert(d)

    assert set(fts_search(conn, "beta")) == {"a", "b"}
    assert set(fts_search(conn, "gamma")) == {"b", "c"}
