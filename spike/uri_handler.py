import sys
import os
import sqlite3
import urllib.parse
from dataclasses import dataclass
from typing import Optional


# =========================
# Models
# =========================

@dataclass
class ResolvedTarget:
    file_id: str
    file_uri: str
    file_kind: Optional[str]
    title: Optional[str]


# =========================
# Resolver
# =========================

class PkmsUriResolver:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row

    def resolve(self, uri: str) -> ResolvedTarget:
        parsed = urllib.parse.urlparse(uri)

        if parsed.scheme != "pkms":
            raise ValueError(f"Unsupported URI scheme: {parsed.scheme}")

        if parsed.netloc != "file":
            raise ValueError(f"Unsupported PKMS authority: {parsed.netloc}")

        path_parts = parsed.path.strip("/").split("/")

        if not path_parts:
            raise ValueError("Empty PKMS resource path")

        # pkms://file/<file_id>
        if len(path_parts) == 1:
            return self._resolve_by_file_id(path_parts[0])

        # pkms://file//<file_id>
        if len(path_parts) == 2 and path_parts[0] == "":
            return self._resolve_by_file_id(path_parts[1])

        # pkms://file/id/<file_id>
        if len(path_parts) == 2 and path_parts[0] == "id":
            return self._resolve_by_file_id(path_parts[1])

        # pkms://file/uid/<file_uid>
        if len(path_parts) == 2 and path_parts[0] == "uid":
            return self._resolve_by_file_uid(path_parts[1])

        raise ValueError(f"Unsupported PKMS resource path: {parsed.path}")

    def _resolve_by_file_id(self, file_id: str) -> ResolvedTarget:
        row = self._conn.execute(
            """
            SELECT file_id, file_uri, file_kind, title
            FROM files
            WHERE file_id = ?
            """,
            (file_id,),
        ).fetchone()

        if not row:
            raise LookupError(f"file_id not found: {file_id}")

        return ResolvedTarget(
            file_id=row["file_id"],
            file_uri=row["file_uri"],
            file_kind=row["file_kind"],
            title=row["title"],
        )

    def _resolve_by_file_uid(self, file_uid: str) -> ResolvedTarget:
        row = self._conn.execute(
            """
            SELECT file_id, file_uri, file_kind, title
            FROM files
            WHERE file_uid = ?
            """,
            (file_uid,),
        ).fetchone()

        if not row:
            raise LookupError(f"file_uid not found: {file_uid}")

        return ResolvedTarget(
            file_id=row["file_id"],
            file_uri=row["file_uri"],
            file_kind=row["file_kind"],
            title=row["title"],
        )


# =========================
# Handler
# =========================

class PkmsUriHandler:
    def handle(self, target: ResolvedTarget) -> None:
        # file:///C:/path/to/file.html -> C:/path/to/file.html
        path = self._file_uri_to_path(target.file_uri)

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        # v1: delegate everything to OS default app
        os.startfile(path)

    @staticmethod
    def _file_uri_to_path(file_uri: str) -> str:
        if not file_uri.startswith("file://"):
            raise ValueError(f"Unsupported file URI: {file_uri}")

        parsed = urllib.parse.urlparse(file_uri)
        return urllib.parse.unquote(parsed.path.lstrip("/"))


# =========================
# Entry Point
# =========================

def main():
    if len(sys.argv) < 3:
        print("Usage: pkms_uri_handler.py <db_path> <pkms_uri>")
        sys.exit(1)

    db_path = sys.argv[1]
    pkms_uri = sys.argv[2]

    resolver = PkmsUriResolver(db_path)
    handler = PkmsUriHandler()

    try:
        target = resolver.resolve(pkms_uri)
        handler.handle(target)
    except Exception as e:
        print(f"[PKMS URI ERROR] {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
