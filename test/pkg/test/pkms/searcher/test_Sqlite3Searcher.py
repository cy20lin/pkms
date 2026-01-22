import sqlite3
import pytest

from pkms.component.searcher import (
    Sqlite3Searcher,
    Sqlite3SearcherConfig,
    Sqlite3SearcherRuntime,
)
from pkms.core.model import (
    SearchArguments,
    SearchResult,
    SearchHit,
)

# ---------- Test DB Setup ----------

from pkms.component.upserter._Sqlite3Upserter import SCHEMA_SQL
# SCHEMA_SQL = """
# CREATE TABLE files (
#     id INTEGER PRIMARY KEY,
#     file_id TEXT NOT NULL UNIQUE,
#     title TEXT NOT NULL,
#     file_uri TEXT,
#     origin_uri TEXT,
#     text TEXT
# );

# CREATE VIRTUAL TABLE files_fts USING fts5(
#     title,
#     text,
#     content='files',
#     content_rowid='id'
# );
# """

INSERT_FILE_SQL = """
INSERT INTO files (
    file_id, 
    title, 
    file_uri, 
    origin_uri, 
    text, 
    file_size, 
    file_hash_sha256, 
    file_extension, 
    file_kind,
    record_created_datetime,
    record_updated_datetime,
    file_created_datetime,
    file_modified_datetime
) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

INSERT_FTS_SQL = """
INSERT INTO files_fts(rowid, title, text)
VALUES (?, ?, ?);
"""


@pytest.fixture
def sqlite_db(tmp_path):
    """
    Create a temporary SQLite DB with FTS5 enabled.
    """
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    conn.executescript(SCHEMA_SQL)

    # Insert test data
    rows = [
        (
            "2025-01-01-0001",
            "Example Domain",
            "file:///example.html",
            "https://example.com",
            "Example.com is a cool website",
            1000,
            '0000000000000000000000000000000000000000000000000000000000000000',
            '.html',
            'snapshot',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
        ),
        (
            "2025-01-01-0002",
            "SQLite FTS",
            "file:///sqlite.html",
            None,
            "SQLite provides full text search using FTS5",
            1001,
            '1111111111111111111111111111111111111111111111111111111111111111',
            '.html',
            'snapshot',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
        ),
        (
            "2025-01-01-0003",
            "Python Programming",
            "file:///python.html",
            None,
            "Python is a programming language",
            1002,
            '2222222222222222222222222222222222222222222222222222222222222222',
            '.html',
            'snapshot',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
            '2000-01-01T01:01:01.000000+00:00',
        ),
    ]

    for row in rows:
        cur = conn.execute(INSERT_FILE_SQL, row)
        rowid = cur.lastrowid
        conn.execute(
            INSERT_FTS_SQL,
            (rowid, row[1], row[4]),
        )

    conn.commit()
    conn.close()

    return str(db_path)


@pytest.fixture
def searcher(sqlite_db):
    config = Sqlite3SearcherConfig(
        db_path=sqlite_db,
        default_limit=20,
        max_limit=50,
    )
    return Sqlite3Searcher(config=config)


# ---------- Tests ----------

def test_basic_search(searcher):
    """
    Basic smoke test for full-text search.

    Verifies that:
    - search() returns a SearchResults object
    - at least one SearchHit is returned for a matching query
    - returned hit contains expected semantic content
    """
    args = SearchArguments(query="SQLite")

    results = searcher.search(args)

    assert isinstance(results, SearchResult)
    assert results.query == "SQLite"
    assert len(results.hits) >= 1

    hit = results.hits[0]
    assert isinstance(hit, SearchHit)
    assert "SQLite" in hit.title or "SQLite" in (hit.snippet or "")


def test_search_returns_expected_fields(searcher):
    """
    Ensure that SearchHit contains all required and optional fields
    defined by the search contract.

    This test validates the structural integrity of SearchHit.
    """
    args = SearchArguments(query="Example")
    results = searcher.search(args)

    hit = results.hits[0]

    assert hit.file_id == "2025-01-01-0001"
    assert hit.file_extension == ".html"
    assert hit.title == "Example Domain"
    assert hit.file_uri is not None
    assert hit.score is not None


def test_limit_and_offset(searcher):
    """
    Verify pagination behavior using limit and offset.

    Ensures:
    - limit restricts number of results
    - offset correctly shifts the result window
    """
    args_page_1 = SearchArguments(query="is", limit=1, offset=0)
    args_page_2 = SearchArguments(query="is", limit=1, offset=1)

    res1 = searcher.search(args_page_1)
    res2 = searcher.search(args_page_2)

    assert len(res1.hits) == 1
    assert len(res2.hits) == 1
    assert res1.hits[0].file_id != res2.hits[0].file_id


def test_no_result(searcher):
    """
    Search with a query that matches no document.

    The expected behavior is to return an empty hits list,
    not None and not an exception.
    """
    args = SearchArguments(query="nonexistentterm")
    results = searcher.search(args)

    assert results.hits == []


def test_limit_is_capped_by_config(searcher):
    """
    Ensure that SearchArguments.limit is capped by SearcherConfig.max_limit.

    This prevents excessive result sets and enforces defensive defaults.
    """
    args = SearchArguments(query="is", limit=999)
    results = searcher.search(args)

    assert results.limit <= searcher.config.max_limit

import threading
from pkms.core.model import SearchArguments

def test_searcher_is_thread_safe(searcher):
    """
    Searcher should support concurrent search calls across threads
    using a shared Searcher instance.
    """

    errors = []

    def worker():
        try:
            args = SearchArguments(query="hello", limit=5, offset=0)
            result = searcher.search(args)
            assert result.hits is not None
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []

# Test query wrap
from pkms.component.searcher._Sqlite3Searcher import (
    wrap_text_search_query
)

@pytest.mark.parametrize(
    "input_query, expected",
    [
        (
            "hello world",
            '"hello" AND "world"',
        ),
        (
            '"hello   world"',
            '"hello   world"',
        ),
        (
            "hello-world",
            '"hello-world"',
        ),
        (
            "-world",
            'NOT "world"',
        ),
        (
            "foo -bar baz",
            '"foo" AND NOT "bar" AND "baz"',
        ),
        (
            "",
            '""',
        ),
        (
            "   ",
            '""',
        ),
        (
            '"quoted" word',
            '"quoted" AND "word"',
        ),
        (
            '-"exact phrase"',
            'NOT "exact phrase"',
        ),
        (
            'a:b c+d',
            '"a:b" AND "c+d"',
        ),
    ],
)
def test_wrap_text_search_query(input_query, expected):
    assert wrap_text_search_query(input_query) == expected