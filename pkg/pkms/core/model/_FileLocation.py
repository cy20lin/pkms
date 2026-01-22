from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field
import pathlib
from urllib.parse import urlparse, unquote, quote
import os.path


class FileLocation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scheme: str = Field(
        default='file',
        description='Reserved field for file accessing scheme (protocol)'
    )
    authority: str = Field(
        default='',
        description='Reserved field for user, host and port'
    )
    base_path: str = Field(
        description='Base path of the target file, where file_path = join(base_path, sub_path)'
    )
    sub_path: str = Field(
        description='Sub-path of the target file, where file_path = join(base_path, sub_path)'
    )

    @staticmethod
    def from_fs_path(
        self, 
        path:Optional[str],
        base_path:Optional[str]='', 
        authority='', 
        scheme='file'
    ):
        p = pathlib.Path(path)
        try:
            sub_path = p.relative_to(base_path)
        except ValueError as e:
            # if p is relative or path is not in base_path
            sub_path = p
        self.scheme = scheme
        self.authority = authority
        self.base_path = quote(base_path)
        self.sub_path = quote(sub_path)
        return FileLocation(
            scheme=scheme,
            authority=authority,
            base_path=base_path,
            sub_path=sub_path,
        )

    @staticmethod
    def from_uri(uri:str, base_path=''):
        parsed = urlparse(uri)
        if uri and parsed.scheme == '':
            raise ValueError(f'Empty scheme for non empty uri={uri}')
        try:
            path = pathlib.PurePosixPath(parsed.path)
            sub_path = path.relative_to(base_path).as_posix()
        except ValueError as e:
            # Catch error like:
            # > ValueError: path is on mount 'c:', start on mount 'd:'
            # fallback with given base_path, and sub_path=parsed.path 
            # e.g. base_path='/' and sub_path='d:/original/parsed/path'
            # in such case os.path.join(base_path, sub_path) is still subpath
            # ValueError: '\\example\\path\\to\\file' is not in the subpath of '\\a\\b' OR one path is relative and the other is absolute.
            sub_path = parsed.path
        return FileLocation(
            scheme=parsed.scheme,
            authority=parsed.netloc,
            base_path=base_path,
            sub_path=sub_path,
        )

    @property
    def path(self) -> str:
        if self.base_path or self.sub_path:
            p = (pathlib.PurePosixPath(self.base_path) / self.sub_path).as_posix()
        else:
            p = '/'
        return p

    @property
    def fs_path(self) -> str:
        path = self.path
        path = unquote(path)
        if self.scheme == 'file':
            path = path.lstrip('/') if ':' in path else path
        return path

    @property
    def uri(self) -> str:
        path = self.path
        return f'{self.scheme}://{self.authority}{path}'