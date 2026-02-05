from dataclasses import dataclass, field
from typing import Any, Iterator

@dataclass
class Frame:
    key: None | str | int
    node: Any
    depth: int
    children_iter: Iterator[Any] | None = None
    resolved_children: dict[str|int,Any] = field(default_factory=dict)
