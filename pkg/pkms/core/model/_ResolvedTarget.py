from __future__ import annotations

from typing import Optional, Dict, List, Literal, Any
from pydantic import BaseModel, ConfigDict, Field
from ._FileLocation import FileLocation
from ._FileType import FileType
from ._ResolutionStatus import ResolutionStatus

class ResolvedTarget(BaseModel):
    status: ResolutionStatus
    file_id: str
    file_extension: str
    file_kind: Optional[str]
    title: Optional[str]
    file_location: Optional[FileLocation]
    file_type: Optional[FileType]