from dataclasses import dataclass, field
from typing import Any, Iterator

@dataclass
class Frame:
    node: Any
    depth: int
    children_iter: Iterator[Any] | None = None
    resolved_children: list[Any] = field(default_factory=list)
