# pkms/core/models/file_descriptor.py
from pydantic import BaseModel

class FileDescriptor(BaseModel):
    path: str
    uri: str
    size: int
    extension: str
    created_datetime: str
    modified_datetime: str

    model_config = {"frozen": True}