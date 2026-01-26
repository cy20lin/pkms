#!/usr/bin/env python3
from typing import Optional
from dataclasses import dataclass
import os
import urllib
import argparse
import sqlite3
import pathlib
import traceback 

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, HTMLResponse
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
from pkms.core.model._ReadyStatus import ReadyStatus

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
import pkms

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

from pkms.lib.markdown_to_html import MarkdownToHtmlConverter
from pkms.lib.odt_to_html import OdtToHtmlConverter

class HtmlRepresenter():

    def __init__(self):
        md_config = MarkdownToHtmlConverter.Config(
            title=None,
            title_from_metadata=True,
            title_from_h1=True,
            title_fallback=None,
            title_from_filename=True,
            redirect_base="/redirect?target="
        )
        self.md_converter = MarkdownToHtmlConverter(config=md_config)
        odt_config = OdtToHtmlConverter.Config(
            title=None,
            title_from_metadata=True,
            title_from_h1=True,
            title_fallback=None,
            title_from_styled_title=True,
            title_from_filename=True,
            show_page_breaks=False,
        )
        self.odt_converter = OdtToHtmlConverter(config=odt_config)

    def represent(self, file_path):
        path = pathlib.Path(file_path)
        if path.suffix == '.odt':
            result = self.odt_converter.convert(file_path,title=None)
        elif path.suffix == '.md':
            result = self.md_converter.convert(file_path,title=None)
        return result

# --------- Middleware ------------

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Referrer-Policy"] = "no-referrer"
        # response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


# ---------- App Factory ----------

def create_app(searcher: "Searcher", resolver: "UriResolver", representer: HtmlRepresenter) -> FastAPI:
    app = FastAPI(title="PKMS Search WebApp")
    app.add_middleware(HeaderMiddleware)

    @app.get("/")
    def index():
        index_path = os.path.join(os.path.dirname(__file__), "index.html")
        return FileResponse(index_path)

    @app.get("/api/ready", response_model=ReadyStatus)
    def ready():
        """
        Dispatcher-facing readiness probe.
        Must be fast, side-effect free, and reliable.
        """
        return ReadyStatus(
            status="ready",
            app="pkms-web",
            version=pkms.__version__,  
            capabilities={
                "search": True,
                "resolve": resolver is not None,
                "render": ["html"],
            },
        )

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

    @app.get("/api/view/{id}")
    def view(id: str):
        try:
            resolved = resolver.resolve(f"pkms:///file/id:{id}")
            path_convention = 'windows' if os.name == 'nt' else 'posix'
            file_path = resolved.file_location.to_filesystem_path(path_convention=path_convention)

            if not os.path.exists(file_path):
                raise FileNotFoundError(file_path)
            
            if resolved.file_extension == '.html':
                return FileResponse(file_path)
            else:
                representation: str = representer.represent(file_path)
                return HTMLResponse(representation)

        except Exception as e:
            reason=''.join(traceback.format_exception(None, e, e.__traceback__))
            raise HTTPException(
                status_code=404,
                detail=f"id:{id} NOT FOUND, reason={reason!r}",
            )

    @app.get("/redirect")
    def redirect(target: str = Query(..., description="Target URL to redirect to")):
        if not target.startswith(("http://", "https://")):
            raise HTTPException(
                status_code=400,
                detail="Target URL must start with http:// or https://",
            )
        return RedirectResponse(url=target, status_code=302)
    # Handle favicon.ico requests gracefully
    @app.get("/favicon.png", include_in_schema=False)
    def favicon():
        # Direct serving from the mounted static directory
        return FileResponse(f"{os.path.dirname(__file__)}/favicon-20260118_115236-64x64-wcbg.ico")

    return app

# ---------- CLI / Entrypoint ----------

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pkms.web",
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


def main(argv: list[str] = []) -> int:
    args = parse_args(argv[1:])

    searcher_config = Sqlite3Searcher.Config(
        db_path=args.db_path,
        max_limit=100,
    )
    searcher = Sqlite3Searcher(config=searcher_config)
    resolver_config = UriResolver.Config(db_path = args.db_path)
    resolver = UriResolver(config=resolver_config)
    representer = HtmlRepresenter()
    app = create_app(searcher, resolver, representer)

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


if __name__ == "__main__":
    import sys
    argv = sys.argv
    code = main(argv)
    sys.exit(code)
