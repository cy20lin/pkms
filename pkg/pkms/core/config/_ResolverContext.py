from ._Frame import Frame
from dataclasses import dataclass, field

@dataclass
class ResolverContext:
    # external static immutable context
    external: dict = field(default_factory=dict)
    # current working frames context
    frames: list[Frame] = field(default_factory=dict)
    frames_base: tuple[int|str,...] = field(default_factory=tuple)
