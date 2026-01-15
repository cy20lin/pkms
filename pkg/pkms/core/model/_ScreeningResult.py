from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Dict, List, Literal
from ._ScreeningStatus import ScreeningStatus
from ._FileStamp import FileStamp
from ._FileLocation import FileLocation

class ScreeningResult(BaseModel):
    """
    Result of screening a single candidate.
    """

    status: ScreeningStatus

    # Preserve file location for further processing in all status
    file_location: FileLocation

    # Extracted file identity and related data
    file_stamp: Optional[FileStamp] = None

    reason: Optional[str] = Field(
        default=None,
        description="Human-readable explanation of the decision"
    )

    diagnostics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Machine-readable details for debugging or UI"
    )
