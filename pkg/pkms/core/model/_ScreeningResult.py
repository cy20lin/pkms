from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Dict, List, Literal
from ._ScreeningStatus import ScreeningStatus
from ._ScreenedFile import ScreenedFile
from ._FileLocation import FileLocation

class ScreeningResult(BaseModel):
    """
    Result of screening a single candidate.
    """

    status: ScreeningStatus

    # Preserve file location for further processing in all status
    file_location: FileLocation

    # Extracted file identity and related data
    # FIXME: admitted differ form status APPROVED, select a good name
    admitted: Optional[ScreenedFile] = None

    reason: Optional[str] = Field(
        default=None,
        description="Human-readable explanation of the decision"
    )

    diagnostics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Machine-readable details for debugging or UI"
    )
