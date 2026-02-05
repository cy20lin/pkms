from .handler import (
    DefaultHandler,
    PrimitiveHandler,
    TupleHandler,
    ListHandler,
    TupleHandler,
    StringHandler,
    DictHandler,
    NodeHandler,
)


class ResolverPolicy:
    def __init__(self):
        self.handlers: list[NodeHandler] = [
            DictHandler(),
            ListHandler(),
            TupleHandler(),
            StringHandler(),
            PrimitiveHandler(),
        ]

    def _handler_for(self, node) -> NodeHandler:
        for h in self.handlers:
            if h.accepts(node):
                return h
        raise TypeError(type(node))

    def is_leaf(self, node):
        return self._handler_for(node).is_leaf(node)

    def resolve_leaf(self, node, *, context, getter):
        return self._handler_for(node).resolve_leaf(
            node, context=context, getter=getter
        )

    def iter_children(self, node):
        return self._handler_for(node).iter_children(node)

    def rebuild(self, node, children):
        return self._handler_for(node).rebuild(node, children)