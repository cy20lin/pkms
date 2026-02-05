from ._NodeHandler import NodeHandler

class DictHandler(NodeHandler):
    def accepts(self, node):
        return isinstance(node, dict)

    def is_leaf(self, node):
        return False

    def resolve_leaf(self, node, *, context, getter):
        raise AssertionError

    def iter_children(self, node:dict):
        return iter(node.items())

    def rebuild(self, node, children):
        assert len(node) == len(children)
        return dict(zip(node.keys(), children))