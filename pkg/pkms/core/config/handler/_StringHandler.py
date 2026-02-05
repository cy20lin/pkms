from ._NodeHandler import NodeHandler
from pkms.core.utility._SafeNestFormatter import SafeNestFormatter


from pkms.core.utility import BracesRefResolver

class StringHandler(NodeHandler):
    def __init__(self):
        self.resolver = BracesRefResolver()

    def accepts(self, node):
        return isinstance(node, str)

    def is_leaf(self, node):
        return True
    
    def resolve_leaf(self, node, *, context, getter):
        return self.resolver.resolve(node, context, getter)
