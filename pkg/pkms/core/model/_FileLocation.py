from __future__ import annotations

from typing import Optional, Dict, List, Literal
from typing import TypeAlias, Iterable
from pydantic import BaseModel, ConfigDict, Field, field_validator
import pathlib
from urllib.parse import urlparse, unquote, quote
import os.path
import os

PathSegment: TypeAlias = str
PathSegments: TypeAlias = tuple[PathSegment | None, ...] 
'''
PathSegments invariant:

- PathSegments is an immutable sequence of URI semantic path segments
- If the first element is None, the path is absolute
- Segments are URI-decoded logical units and may be empty strings
- PathSegments does not encode OS or filesystem semantics
- PathSegments may be empty
- If non-empty, only segments[0] may be None
- None in any other position is unsupported and results in undefined behavior
- Empty string segments ('') are preserved and significant
- No normalization of trailing or repeated separators is performed
'''

class FileLocation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scheme: str = Field(
        default='file',
        description='Reserved field for file accessing scheme (protocol)'
    )
    authority: Optional[str] = Field(
        default='',
        description='Reserved field for user, host and port'
    )
    base_segments: PathSegments
    sub_segments: PathSegments

    @field_validator("base_segments", "sub_segments")
    @classmethod
    def validate_path_segments(cls, segments: PathSegments) -> PathSegments:
        # empty tuple is always valid
        if not segments:
            return segments

        # only the first element may be None
        if any(s is None for s in segments[1:]):
            raise ValueError(
                "Only the first path segment may be None; "
                "None in later positions is unsupported"
            )
        return segments

    @property
    def segments(self) -> PathSegments:
        return self.segments_join(self.base_segments, self.sub_segments)

    def uri_path_to_segments(path: str | None) -> tuple[str | None, ...]:
        """
        Examples:
        "/"           -> (None,)
        "/a/b"        -> (None, "a", "b")
        "/a%2Fb/c"    -> (None, "a/b", "c")
        "a/b"         -> ("a", "b")   # relative URI path (allowed internally)
        """
        if not path:
            return ()
        is_absolute: bool = path.startswith("/")
        relative_path: str = path[1:] if is_absolute else path
        segments: list[str|None] = [None] if is_absolute else []
        parts = relative_path.split("/")
        for part in parts:
            segments.append(unquote(part))
        return tuple(segments)

    @staticmethod
    def from_uri(
        uri: str,
        *,
        base_uri_path: str | None = None
    ) -> FileLocation:
        # due to CVE-2023-24329
        uri = uri.lstrip()
        parsed = urlparse(uri)
        
        path_segments = FileLocation.uri_path_to_segments(parsed.path)
        base_segments = FileLocation.uri_path_to_segments(base_uri_path)
        sub_segments = FileLocation.segments_try_relative_to(path_segments, base_segments)


        authority = parsed.netloc
        # While RFC 3986 technically distinguishes between an "undefined" and "empty" authority,
        # Python’s standard library typically collapses both into an empty string to maintain backward compatibility.
        # So extra step to detinguish is needed
        if authority == '':
            # NOTE: PATCH for python cannot distinguish null authority before python 3.15
            # under the condition that parsed.netloc is already empty string ''
            # check if string "://" follows from the ending position of scheme
            # if so the authority is treaded as EMPTY authority i.e. authority=''
            # otherwise authority is treated as NULL authority i.e. authority=None
            # https://github.com/python/cpython/issues/67041
            is_empty_authority = uri[len(parsed.scheme):].startswith('://') if parsed.scheme else uri.startswith('//')
            is_null_authority = not is_empty_authority
            if is_null_authority:
                authority = None

        return FileLocation(
            scheme=parsed.scheme,
            authority=authority,
            base_segments=base_segments,
            sub_segments=sub_segments
        )

    @property
    def uri(self) -> str:
        authority_str = '//' + self.authority if self is not None else ''
        return f'{self.scheme}:{authority_str}{self.uri_path}'

    @property
    def uri_path(self) -> str:
        return self._segments_to_uri_path(self.segments)

    @property
    def uri_base_path(self) -> str:
        return self._segments_to_uri_path(self.base_segments)

    @property
    def uri_sub_path(self) -> str:
        return self._segments_to_uri_path(self.sub_segments)

    # Filesystem projection（explicit, never implicit）
    @staticmethod
    def from_filesystem_path(
        path: str,
        base_path: str | None = None,
        *,
        scheme='file',
        authority='', 
        path_convention: Literal["posix", "windows"],
        absolute=False,
        normalize=True,
    ) -> FileLocation:
        if path_convention is None:
            Path = pathlib.PurePath
        elif path_convention == 'windows':
            Path = pathlib.PureWindowsPath
        elif path_convention == 'posix':
            Path = pathlib.PurePosixPath
        else:
            raise ValueError(f'Unkonw path_convention={path_convention!r}')
        
        # NOTE: absolute/normalize the path for canonical segments
        if absolute:
            # NOTE: absolute implies normalize when using os.path.abspath
            base_path = os.path.abspath(base_path) if base_path is not None else base_path
            path = os.path.join(base_path, path) if base_path is not None else path
            path = os.path.abspath(path)
        elif normalize:
            base_path = os.path.normpath(base_path) if base_path else base_path
            path = os.path.normpath(path) if path else path
        
        base_path, sub_path = FileLocation._split_path(path, base_path, Path)
        
        base_segments = FileLocation._filesystem_path_to_segments(base_path)
        sub_segments = FileLocation._filesystem_path_to_segments(sub_path)
        # check postcondition for filesystem path
        assert (
            len(base_segments) == 0 and len(sub_segments) > 0 or
            len(base_segments) > 0 and len(sub_segments) >= 0
        )
        return FileLocation(
            scheme=scheme,
            authority=authority,
            base_segments=base_segments,
            sub_segments=sub_segments
        )

    def to_filesystem_path(
        self,
        path_convention: Literal["posix", "windows"]
    ) -> str:
        return self._segments_to_filesystem_path(self.segments, path_convention)

    def to_filesystem_base_path(
        self,
        path_convention: Literal["posix", "windows"]
    ) -> str:
        return self._segments_to_filesystem_path(self.base_segments, path_convention)

    def to_filesystem_sub_path(
        self,
        path_convention: Literal["posix", "windows"]
    ) -> str:
        return self._segments_to_filesystem_path(self.sub_segments, path_convention)

    @staticmethod
    def _filesystem_path_to_segments(path:pathlib.PurePath) -> PathSegments:
        segments = None
        if len(path.parts) == 0: 
            segments = ()
        else: 
            front_segments = [None] if path.is_absolute() else []
            rest_segments = path.parts[1:]
            if isinstance(path, pathlib.PurePosixPath):
                # Follow PurePosixPath behavior with modification (remove slash)
                # '/' ==> (None,'',)
                # '//' ==> (None,'','')
                # '///' ==> (None,'',)
                # '////' ==> (None,'',)
                front_parts = path.parts[0].split('/')
                print(f'x={front_parts}')
                print(f'x={front_parts}')
            elif isinstance(path, pathlib.PureWindowsPath):
                # Follow PureWindowsPath behavior with modification (remove slash)
                # '/' ==> (None,'',)
                # '//' ==> (None,'',)
                # '///' ==> (None,'',)
                # '////' ==> (None,'',)
                # 'c:////' ==> (None,'c:',)
                # '//server/dir/file.txt' ==> (None,'','server','dir','file.txt')
                front_parts = path.parts[0].replace('\\','/').split('/')
            # strip empty starting part in front_parts
            if front_parts and front_parts[0] == '':
                front_parts = front_parts[1:]
            # strip empty ending part in front_parts, if the front_parts is followed by non-empty rest_segments
            if len(path.parts) > 1 and front_parts and front_parts[-1] == '':
                front_parts.pop()
            front_segments.extend(front_parts)
            segments = (*front_segments,*rest_segments)
        assert segments is not None
        return segments
        
    @staticmethod
    def _segments_to_filesystem_path(segments:PathSegments, path_convention: Literal['posix','windows']):
        assert path_convention in ('posix', 'windows')
        if FileLocation._segments_is_absolute(segments):
            if path_convention == 'windows':
                path = '/'.join(segments[1:])
            else:
                path = '/' + '/'.join(segments[1:])
        else:
            path = '/'.join(segments)
        return path

    @staticmethod
    def _segments_to_uri_path(segments:PathSegments):
        uri_path = '/'.join(
            map(
                lambda segment: quote(segment,safe='') if segment is not None else '',
                segments
            )
        ) if segments != (None,) else '/'
        return uri_path

    @staticmethod
    def _split_path(path:str, base_path:Optional[str], Path: pathlib.PurePath):
        '''
        Docstring for _split_path
        
        :param path: the target path, maybe absolute or relative
        :type path: str
        :param base_path: base_path for computing relative sub_path form path
        :type base_path: Optional[str]
        :param Path: the Path class for spliting filesystem path
        :type Path: pathlib.PurePath
        '''
        # Rejects:
        # - relative/posix/path
        # - ./relative/posix/path
        # - relative/posix/path
        # - .\relative\windows\path
        # - relative\windows\path
        # - \windows\path\without\drive
        # Accepts:
        # - /posix/path
        # - C:/windows/path
        # - C:\windows\path

        # if base_path is None or base == ''
        # ==> sub_path = path, and subpath=path is absolute
        # if base_path is relative and not empty
        # ==> reject
        # if base_path is absolute
        # ==> sub_path is relative if path is relative
        # ==> sub_path maybe relative or absolute, if path is absolute
        # i.e.
        # path is absolute => sub_path is relative or absolute, base_path MUST be absolute
        # path is relative => sub_path is relative as path, base_path MUST be absolute
        if not base_path:
            # base_path is None
            # or base_path == ''
            # or base_path == Path('')
            p = Path(path)
            b = Path('')
            if not p.is_absolute():
                raise ValueError(f'path={path!r} MUST be absoulte when base is empty')
            base_path = b
            sub_path = p
        else:
            p = Path(path)
            b = Path(base_path)
            if not b.is_absolute():
                raise ValueError(f'base_path={base_path!r} should be either absoulte or empty')
            elif not p.is_absolute():
                assert b.is_absolute()
                base_path = b
                sub_path = p
            else:
                assert b.is_absolute()
                base_path = b
                try:
                    sub_path = p.relative_to(base_path)
                except ValueError as e:
                    sub_path = p
        return base_path, sub_path

    @staticmethod
    def segments_join(segments1:PathSegments, segments2:PathSegments):
        if FileLocation._segments_is_absolute(segments2):
            return segments2
        else:
            return segments1 + segments2

    def segments_relative_to(
        full: tuple[str | None, ...],
        base: tuple[str | None, ...],
    ) -> tuple[str, ...]:
        if not full[: len(base)] == base:
            raise ValueError("full path is not under base")
        rel = full[len(base):]
        if rel and rel[0] is None:
            raise ValueError("relative path cannot be absolute")
        return rel

    def segments_try_relative_to(
        full: tuple[str | None, ...],
        base: tuple[str | None, ...],
    ) -> tuple[str, ...]:
        if not full[: len(base)] == base:
            return full
        rel = full[len(base):]
        return rel

    @staticmethod
    def _segments_is_absolute(segments:tuple) -> bool:
        return segments and segments[0] is None
    
    def from_segments(
        segments: Iterable[str | None],
        *,
        scheme: str = "file",
        authority: str = "",
    ) -> FileLocation:

        segs = tuple(segments)

        # invariant enforcement
        if segs.count(None) > 1:
            raise ValueError("Only one None (absolute marker) allowed")

        if None in segs[1:]:
            raise ValueError("None only allowed as first segment")

        return FileLocation(
            scheme=scheme,
            authority=authority,
            base_segments=(None,) if segs[:1] == (None,) else (),
            sub_segments=segs[1:] if segs[:1] == (None,) else segs,
        )


if __name__ ==  '__main__':
    # For debug use
    # # f = FileLocation.from_filesystem_path("c:/asdf /df", path_convention="windows")
    # # f = FileLocation.from_filesystem_path("//server/dir/b", path_convention="posix")
    # # f = FileLocation.from_filesystem_path("c://server/./d", path_convention="posix")
    # f = FileLocation.from_segments((None, 'a:','b'))
    # # f = FileLocation.from_uri('file:///a/b',base_uri_path=None)
    # # f = FileLocation.from_uri('file:///a/',base_uri_path=None)
    # print(f"{f.to_filesystem_path('posix')!r}")
    # print(f"{f.to_filesystem_path('windows')!r}")
    # print(f.segments)
    # print(f.base_segments)
    # print(f.sub_segments)
    # print(f.uri)
    pass