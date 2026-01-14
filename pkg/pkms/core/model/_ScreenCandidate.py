from typing import TypeAlias
from ._FileLocation import FileLocation

ScreenCandidate: TypeAlias = FileLocation
"""
A candidate file discovered by Globber,
pending screening before indexing.
"""

__all__ = ['ScreenCandidate']

