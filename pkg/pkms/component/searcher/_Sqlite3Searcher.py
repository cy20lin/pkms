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

import re
from dataclasses import dataclass
from typing import List

# NOTE: don't use pydantic for not introducing validation overhead
@dataclass(frozen=True)
class Token:
    """
    Represents a single logical search term.

    Attributes:
        text:
            The literal text of the term, without surrounding quotes
            and without any leading operator characters.
        negate:
            Whether this term is negated (logical NOT).
    """
    text: str
    negate: bool = False

_TOKEN_PATTERN = re.compile(
    r'-"([^"]+)"|"([^"]+)"|(-?\S+)'
)



def wrap_text_search_query(query: str) -> str:
    """
    Compile a user-provided free-form search string into a safe and
    predictable FTS-compatible query expression.

    This function interprets the input as *textual intent*, not as a
    raw query language. It applies a minimal, well-defined set of rules
    to transform the input into a structured boolean expression while
    preventing accidental exposure to backend query syntax.

    Parsing rules
    -------------
    1. Quoted segments:
       - Text enclosed in double quotes is treated as a literal phrase.
       - Whitespace inside quotes is preserved.
       - No further tokenization is performed on quoted content.

    2. Tokenization:
       - Unquoted text is split on whitespace only.
       - Symbols such as '-', '+', '/', '.', ':' are preserved as part
         of the token text.
       - No implicit splitting is performed on punctuation.

    3. Negation:
       - A leading '-' on an unquoted token marks it as negated.
       - The '-' character is not part of the resulting term text.
       - Negation applies to exactly one token.

    4. Boolean composition:
       - All non-negated tokens are combined using implicit logical AND.
       - Negated tokens are combined using logical NOT.
       - No implicit OR behavior is introduced.

    5. Safety guarantees:
       - All terms are emitted as quoted phrases to prevent accidental
         interpretation as backend query operators or column specifiers.
       - The resulting expression is suitable for parameterized execution
         against an FTS engine.

    Parameters
    ----------
    query:
        Raw user input representing a textual search intent.

    Returns
    -------
    str
        A boolean expression composed of quoted phrases and explicit
        logical operators, suitable for use as an FTS MATCH argument.

    Examples
    --------
    >>> compile_text_search_query("hello world")
    '"hello" AND "world"'

    >>> compile_text_search_query('"hello   world"')
    '"hello   world"'

    >>> compile_text_search_query("hello-world")
    '"hello-world"'

    >>> compile_text_search_query("-world")
    'NOT "world"'
    """
    tokens: List[Token] = []

    for neg_quoted, quoted, bare in _TOKEN_PATTERN.findall(query):
        if neg_quoted:
            tokens.append(Token(text=neg_quoted, negate=True))
        elif quoted:
            tokens.append(Token(text=quoted))
        elif bare:
            if bare.startswith("-") and len(bare) > 1:
                tokens.append(Token(text=bare[1:], negate=True))
            else:
                tokens.append(Token(text=bare))

    if not tokens:
        return '""'

    parts: List[str] = []
    for token in tokens:
        escaped = token.text.replace('"', '""')
        phrase = f'"{escaped}"'
        if token.negate:
            parts.append(f'NOT {phrase}')
        else:
            parts.append(phrase)

    return " AND ".join(parts)

SEARCH_SQL = """
SELECT
    files.file_id,
    files.file_extension,
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

        query = wrap_text_search_query(args.query)
        with self._connect() as conn:
            cur = conn.execute(
                SEARCH_SQL,
                (query, limit, args.offset),
            )

        hits = []
        for row in cur.fetchall():
            hits.append(
                SearchHit(
                    file_id=row["file_id"]+row["file_extension"],
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
