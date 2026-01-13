from __future__ import annotations

from typing import Optional, Dict, List, Literal, Any
from pydantic import BaseModel, ConfigDict, Field

class ScreenedFile(BaseModel):
    """
    A file that has passed screening and
    is admitted into the indexing pipeline.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str = Field(
        description="Stable PKMS file identifier"
    )

    uid: Optional[str] = Field(
        default=None,
        description="Optional content-based or metadata-based UID"
    )

    extension: str = Field(
        description="Normalized file extension ('' allowed)"
    )

    kind: str = Field(
        description="snapshot | editable (or future extension)"
    )

    # Metadata
    title: str = Field(
        ...,
        description="Primary title for display and search"
    )

    importance: int = Field(
        default=0,
        ge=0,
        description="User-defined importance level"
    )

    # Integrity
    size: int = Field(
        default=None,
        description="File size in bytes"
    )

    created_datetime: str
    modified_datetime: str
    # accessed_datetime: str

    hash_sha256: str = Field(
        default=None,
        description="SHA256 hash of the file in string"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Screening-derived metadata hints"
    )