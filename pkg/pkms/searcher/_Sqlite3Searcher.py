import sqlite3
from typing import Optional, Literal
from pkms.core.component.searcher import (
    Searcher,
    SearcherConfig,
    SearcherRuntime,
)
from pkms.core.model import (
    SearchArguments,
    SearchResult,
    SearchHit,
)

SEARCH_SQL = """
SELECT
    files.file_id,
    files.title,
    files.file_uri,
    files.origin_uri,
    bm25(files_fts) AS score,
    snippet(
        files_fts,
        1,
        '<mark>',
        '</mark>',
        '…',
        20
    ) AS snippet
FROM files_fts
JOIN files ON files.id = files_fts.rowid
WHERE files_fts MATCH ?
ORDER BY score
LIMIT ? OFFSET ?;
"""

class Sqlite3SearcherConfig(SearcherConfig):
    type: Literal['Sqlite3SearcherConfig'] = 'Sqlite3SearcherConfig'

class Sqlite3SearcherRuntime(SearcherRuntime):
    pass

class Sqlite3Searcher(Searcher):
    Config = Sqlite3SearcherConfig
    Runtime = Sqlite3SearcherRuntime

    def __init__(self, *, config: Sqlite3SearcherConfig, runtime: Optional[Sqlite3SearcherRuntime] = None):
        super().__init__(config=config, runtime=runtime)

    def _connect(self):
        conn = sqlite3.connect(self.config.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def search(self, args: SearchArguments) -> SearchResult:
        limit = min(args.limit, self.config.max_limit)

        with self._connect() as conn:
            cur = conn.execute(
                SEARCH_SQL,
                (args.query, limit, args.offset),
            )

        hits = []
        for row in cur.fetchall():
            hits.append(
                SearchHit(
                    file_id=row["file_id"],
                    title=row["title"],
                    file_uri=row["file_uri"],
                    origin_uri=row["origin_uri"],
                    snippet=row["snippet"],
                    score=row["score"],
                )
            )

        return SearchResult(
            query=args.query,
            limit=limit,
            offset=args.offset,
            hits=hits,
        )

    def close(self):
        pass
