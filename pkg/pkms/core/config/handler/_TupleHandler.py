from ._NodeHandler import NodeHandler

class TupleHandler(NodeHandler):
    def accepts(self, node:tuple):
        return isinstance(node, tuple)

    def is_leaf(self, node):
        return False

    def resolve_leaf(self, node, *, context):
        raise AssertionError

    def iter_children(self, node:tuple):
        return iter(enumerate(node))

    def rebuild(self, node:tuple, children:list):
        assert len(node) == len(children)
        return tuple(children)