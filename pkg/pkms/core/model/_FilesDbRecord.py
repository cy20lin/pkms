from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class FilesDbRecord(BaseModel):
    """
    Persistence model.
    Must be 1-to-1 aligned with SQLite UPSERT_SQL parameters.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,  # immutable once created (very important)
    )

    # Identity
    file_id: str
    file_uid: Optional[str]

    # Location
    file_uri: str

    # Integrity
    file_size: int
    file_hash_sha256: str

    # Classification
    file_extension: str
    file_kind: str

    # Metadata
    importance: int
    title: str
    origin_uri: Optional[str]

    # Time
    record_created_datetime: str
    record_updated_datetime: str
    file_created_datetime: str
    file_modified_datetime: str

    # Content
    text: Optional[str]
    extra: str  # JSON string