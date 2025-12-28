from __future__ import annotations

from typing import Optional, Dict, Literal
from pydantic import BaseModel, ConfigDict, Field

class IndexedDocument(BaseModel):
    """
    Normalized output of an Indexer.
    This is the only object allowed to cross into the Upserter.
    """
    # TODO: 2025-12-26 Decide should allow extra props or not
    # NOTE: => 2025-12-26 allow for now for faster iteration
    model_config = ConfigDict(extra="allow")

    # Identity
    file_id: str = Field(
        ...,
        description="Human-visible stable identifier (from filename)"
    )

    file_uid: Optional[str] = Field(
        default=None,
        description="Strong unique identifier (uuid / cuid / hash)"
    )

    # Location

    file_uri: str = Field(
        ...,
        description="Canonical file URI (file://...)"
    )

    # Integrity
    file_size: int = Field(
        default=None,
        description="File size in bytes"
    )

    # TODO: Think what type should be used for hash, bytearray or string ?
    file_hash_sha256: str = Field(
        default=None,
        description="SHA256 hash of the file in string"
    )

    # Classification

    file_extension: str = Field(
        ...,
        description="File extension with leading dot, or empty string"
    )


    file_kind: Literal["snapshot", "editable"] = Field(
        ...,
        description="Content mutability classification"
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

    origin_uri: Optional[str] = Field(
        default=None,
        description="Original source URI (e.g. http(s) URL)"
    )

    #
    file_created_datetime: str
    file_modified_datetime: str
    index_created_datetime: str
    index_updated_datetime: str

    # Content
    text: Optional[str] = Field(
        default=None,
        description="Extracted full-text content"
    )

    extra: Dict[str, object] = Field(
        default_factory=dict,
        description="Unstructured or indexer-specific metadata"
    )
