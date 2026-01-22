from dataclasses import dataclass
from typing import Optional, Literal
import sqlite3
import urllib.parse

from pkms.core.component.resolver import (
    Resolver,
    ResolverConfig,
    ResolverRuntime,
)
from pkms.core.model import (
    ResolvedTarget,
    ResolutionStatus,
    FileLocation,
    FileType,
)


class UriResolverRuntime(ResolverRuntime):
    pass

class UriResolverConfig(ResolverConfig):
    type: Literal['UriResolverConfig'] = 'UriResolverConfig'
    db_path: str

class UriResolver(Resolver):
    Config = UriResolverConfig
    Runtime = UriResolverRuntime

    def __init__(self, config: UriResolverConfig, runtime: Optional[UriResolverRuntime] = None):
        super().__init__(config=config, runtime=runtime)

    def resolve(self, uri: str) -> ResolvedTarget:
        parsed = urllib.parse.urlparse(uri)

        # print(f'parsed: {parsed}',flush=True)
        # 1. scheme
        if parsed.scheme != "pkms":
            raise ValueError(f"Unsupported URI scheme: {parsed.scheme}")

        # 2. authority (reserved, currently unused)
        # parsed.netloc MAY be empty, but position must exist
        authority = parsed.netloc  # reserved for future use

        # 3. path
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) != 2:
            raise ValueError(f"Invalid PKMS path: {parsed.path}")

        resource, selector_part = path_parts

        if resource != "file":
            raise ValueError(f"Unsupported PKMS resource: {resource}")

        # 4. selector:value.ext
        try:
            selector, rest = selector_part.split(":", 1)
        except ValueError:
            raise ValueError("Missing selector in PKMS URI")

        if "." not in rest:
            raise ValueError("File extension is required")

        value_ext = rest.split(".", 1)
        value = value_ext[0].lower()
        ext = '.'+value_ext[1].lower() if len(value_ext) == 2 else ''

        return self._resolve_by_selector(
            selector=selector,
            value=value,
            ext=ext,
        )

    def _resolve_by_selector(
        self,
        *,
        selector: str,
        value: str,
        ext: str,
    ) -> ResolvedTarget:
        conn = sqlite3.connect(self.config.db_path)
        conn.row_factory = sqlite3.Row

        try:
            if selector == "id":
                row = conn.execute(
                    """
                    SELECT file_id, file_uri, file_kind, title, file_extension
                    FROM files
                    WHERE file_id = ? AND file_extension = ?
                    """,
                    (value, ext),
                ).fetchone()
                # print(row,flush=True)

            elif selector == "uid":
                row = conn.execute(
                    """
                    SELECT file_id, file_uri, file_kind, title, file_extension
                    FROM files
                    WHERE file_uid = ?
                    """,
                    (value,),
                ).fetchone()
            elif selector == "sha256":
                row = conn.execute(
                    """
                    SELECT file_id, file_uri, file_kind, title, file_extension
                    FROM files
                    WHERE file_hash_sha256 = ?
                    """,
                    (value,),
                ).fetchone()
            else:
                raise ValueError(f"Unsupported selector: {selector}")

            if not row:
                raise LookupError(f"Resource not found for {selector}:{value}")
            return ResolvedTarget(
                status=ResolutionStatus.OK,
                file_id=row["file_id"],
                file_extension=row['file_extension'],
                file_kind=row["file_kind"],
                title=row["title"],
                file_location=FileLocation.from_uri(row['file_uri']),
                file_type=FileType.REGULAR,
            )

        finally:
            conn.close()