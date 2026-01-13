from typing import Iterable, List
from pkms.core.component.screener import (
    Screener,
    ScreenerConfig,
    ScreenerRuntime
)
import pathspec
import logging
import pathlib
from pkms.core.model import FileLocation
from pkms.core.model import ScreenCandidate
from pkms.core.model import ScreeningResult
from pkms.core.component.screener import (
    Screener,
    ScreenerConfig,
    ScreenerRuntime
)
import os

def _try_append_slash(path:str):
    return path+'/' if not path.endswith('/') else path

class PathspecScreenerConfig = ScreenerConfig
class PathspecScreener(Screener):
    Config = PathspecScreenerConfig
    def __init__(self, config:PathspecScreenerConfig):
        super().__init__(config=config)
    
    def screen(
        self,
        candidates: Iterable[ScreenCandidate],
    ) -> List[ScreeningResult]:
        """
        Screen candidate files.

        - Must NOT perform indexing
        - Must NOT perform database writes
        - Must return explicit screening decisions

        :param candidates: iterable of ScreenCandidate
        :return: list of ScreeningResult (order-preserving)
        """
        raise NotImplementedError






