from pydantic import BaseModel
from typing import List, Dict

class ReadyStatus(BaseModel):
    status: str
    app: str
    version: str
    capabilities: Dict[str, object]