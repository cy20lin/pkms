
from ._ComponentRuntime import ComponentRuntime
from ._ComponentConfig import ComponentConfig

from abc import ABC
from typing import Optional

class Component(ABC):
    """
    Base class for PKMS components.
    """

    Config: type[ComponentConfig] = ComponentConfig
    Runtime: type[ComponentRuntime] = ComponentRuntime

    def __init__(
        self,
        *,
        config: ComponentConfig,
        runtime: Optional[ComponentRuntime],
    ):
        self.config = config
        self.runtime = runtime