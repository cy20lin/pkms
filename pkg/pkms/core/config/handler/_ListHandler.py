from ._NodeHandler import NodeHandler

class ListHandler(NodeHandler):
    def accepts(self, node:list):
        return isinstance(node, list)

    def is_leaf(self, node):
        return False

    def resolve_leaf(self, node, *, context):
        raise AssertionError

    def iter_children(self, node:list):
        return iter(node)

    def rebuild(self, node:list, children:list):
        assert len(node) == len(children)
        return list(children)