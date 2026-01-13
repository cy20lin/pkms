from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from ._FileLocation import FileLocation

class ScreenCandidate(FileLocation):
    """
    A candidate file discovered by Globber,
    pending screening before indexing.
    """
    pass

