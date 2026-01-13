#!/usr/bin/env python3

import argparse
from typing import Optional

from flask import Flask, request, jsonify, send_file

from pkms.core.component.searcher import (
    Searcher,
    SearcherConfig,
)

from pkms.core.model import (
    SearchArguments,
    SearchResult,
)
from pkms.searcher import Sqlite3Searcher
import os

from dataclasses import dataclass
import sqlite3
import urllib

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

class UriResolver:
    def __init__(self, db_path: str):
        self.db_path = db_path

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

        raise ValueError(f"Unsupported PKMS resource path: {parsed.path}")

    def _resolve_by_file_id(self, file_id: str) -> ResolvedTarget:
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        result = None
        try:
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

            result = ResolvedTarget(
                file_id=row["file_id"],
                file_uri=row["file_uri"],
                file_kind=row["file_kind"],
                title=row["title"],
            )
        finally:
            self._conn.close()
            self._conn = None

        return result

# File uri to path
import urllib.parse
import urllib.request
import os

def file_uri_to_path(uri: str) -> str:
    """Convert a file URI to a local filesystem path."""
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme != 'file':
        raise ValueError(f"Not a file URI: {uri}")
    
    # Decode percent-encoded characters
    path = urllib.request.url2pathname(parsed.path)
    
    # Fix leading slash issue on Windows
    if len(path) > 2 and path.startswith('/') and path[1].isalpha() and path[2] == ':':
        path = path[1:]
    
    return path

# Example usage:
# posix_uri = 'file:///home/user/documents/test%20file.txt'
# windows_uri = 'file:///C:/Users/User/Documents/test%20file.txt'

# print(file_uri_to_path(posix_uri))   # /home/user/documents/test file.txt
# print(file_uri_to_path(windows_uri)) # C:\Users\User\Documents\test file.txt

# ---------- App Factory ----------

def create_app(searcher: Searcher, resolver: UriResolver) -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return send_file(os.path.join(os.path.dirname(__file__), 'index.html'))

    @app.route("/api/search", methods=["GET"])
    def search():
        query = request.args.get("q")
        if not query:
            return jsonify({"error": "missing query parameter 'q'"}), 400

        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))

        args = SearchArguments(
            query=query,
            limit=limit,
            offset=offset,
        )

        result: SearchResult = searcher.search(args)
        return jsonify(result.model_dump())

    @app.route("/api/view/<file_id>", methods=["GET"])
    def view(file_id):
        try:
            resolved = resolver.resolve(f"pkms://file/id/{file_id}")
            file_uri = resolved.file_uri
            file_path = file_uri_to_path(file_uri)
            result = send_file(file_path)
        except:
        # except Exception as e:
            result = f"{file_id} NOT FOUND"
        return result
            
    return app


# ---------- Composition Root ----------

def build_searcher(db_path: str) -> Searcher:
    config = Sqlite3Searcher.Config(db_path=db_path, max_limit=100)
    return Sqlite3Searcher(config=config)


# ---------- CLI / Entrypoint ----------

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PKMS Search WebApp",
    )

    parser.add_argument(
        "--db-path",
        required=True,
        help="Path to SQLite database",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Flask bind host (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=43472,
        help="Flask bind port (default: 43472)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode",
    )

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)

    searcher = build_searcher(db_path=args.db_path)
    resolver = UriResolver(args.db_path)
    app = create_app(searcher, resolver)

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
    )


if __name__ == "__main__":
    main()
