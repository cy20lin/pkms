
from ._NodeHandler import NodeHandler
from typing import Any

class PrimitiveHandler(NodeHandler):
    def accepts(self, node: Any):
        return True

    def is_leaf(self, node):
        return True

    def resolve_leaf(self, node, *, context, getter):
        return node

    def iter_children(self, node:list):
        raise AssertionError

    def rebuild(self, node:list, children:list):
        raise AssertionError