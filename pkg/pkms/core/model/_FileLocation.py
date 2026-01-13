from __future__ import annotations

from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, ConfigDict, Field
import pathlib


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
    # MAYBE deal with dir in the future
    # is_dir: bool 

    @property
    def path(self) -> str:
        if self.base_path or self.sub_path:
            p = (pathlib.Path(self.base_path) / self.sub_path).as_posix()
        else:
            p = '/'
        return p

    @property
    def uri(self) -> str:
        return pathlib.Path(self.path).absolute().as_uri()