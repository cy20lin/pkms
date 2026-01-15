#!/usr/bin/env python3
from typing import Optional
from dataclasses import dataclass
import os
import urllib
import argparse
import sqlite3

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

from pkms.core.component.searcher import (
    Searcher,
    SearcherConfig,
)

from pkms.core.model import (
    SearchArguments,
    SearchResult,
)
from pkms.component.searcher import Sqlite3Searcher

# =========================
# Models
# =========================

@dataclass
class ResolvedTarget2:
    file_id: str
    file_uri: str
    file_kind: Optional[str]
    title: Optional[str]


# =========================
# Resolver
# =========================

from pkms.component.resolver import UriResolver
from pkms.core.model import ResolvedTarget

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

def create_app(searcher: "Searcher", resolver: "UriResolver") -> FastAPI:
    app = FastAPI(title="PKMS Search WebApp")

    @app.get("/")
    def index():
        index_path = os.path.join(os.path.dirname(__file__), "index.html")
        return FileResponse(index_path)

    @app.get("/api/search", response_model=None)
    def search(
        q: str = Query(..., description="Search query"),
        limit: int = Query(20, ge=1),
        offset: int = Query(0, ge=0),
    ):
        args = SearchArguments(
            query=q,
            limit=limit,
            offset=offset,
        )

        result: SearchResult = searcher.search(args)
        return result.model_dump()

    @app.get("/api/view/{file_id}")
    def view(file_id: str):
        try:
            resolved = resolver.resolve(f"pkms:///file/id:{file_id}")
            file_uri = resolved.file_uri
            file_path = file_uri_to_path(file_uri)

            if not os.path.exists(file_path):
                raise FileNotFoundError(file_path)

            return FileResponse(file_path)

        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"{file_id} NOT FOUND",
            )

    return app


# ---------- Composition Root ----------

def build_searcher(db_path: str) -> "Searcher":
    config = Sqlite3Searcher.Config(
        db_path=db_path,
        max_limit=100,
    )
    return Sqlite3Searcher(config=config)


# ---------- CLI / Entrypoint ----------

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PKMS Search WebApp (FastAPI)",
    )

    parser.add_argument(
        "--db-path",
        required=True,
        help="Path to SQLite database",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=43472,
        help="Bind port (default: 43472)",
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto reload (dev only)",
    )

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv)

    searcher = build_searcher(db_path=args.db_path)
    resolver = UriResolver(args.db_path)
    app = create_app(searcher, resolver)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()