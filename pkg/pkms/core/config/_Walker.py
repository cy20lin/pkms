from ._Frame import Frame
from ._exceptions import ConfigResolutionError
from ._ResolverContext import ResolverContext
from ._ResolverContextNestItemGetter import ResolverContextNestItemGetter 
from ._ResolverPolicy import ResolverPolicy

class Walker:
    def __init__(self, *, policy: ResolverPolicy, max_depth: int=64):
        self.policy = policy
        self.max_depth = max_depth
    
    @staticmethod
    def get_result_storage(frames: list[Frame], default={}):
        if frames:
            return frames[-1].resolved_children
        else:
            return default


    def walk(self, base, *, context, base_keys):
        stack: list[Frame] = []
        stack.append(Frame(key=None, node=base, depth=0))
        result_storage = {}
        resolver_context = ResolverContext(
            external=context,
            frames=stack,
            frames_base=base_keys
        )
        resolver_item_getter = ResolverContextNestItemGetter()

        while stack:
            frame = stack[-1]

            if frame.depth > self.max_depth:
                raise ConfigResolutionError(f"Maximum depth {self.max_depth} exceeded at node {frame.node}")

            # leaf node
            if self.policy.is_leaf(frame.node):
                value = self.policy.resolve_leaf(
                    frame.node, context=resolver_context, getter=resolver_item_getter
                )
                stack.pop()
                storage = self.get_result_storage(stack, default=result_storage)
                storage[frame.key] = value
                continue

            # first time we see this node
            if frame.children_iter is None:
                frame.children_iter = self.policy.iter_children(frame.node)

            try:
                child_key,child_value = next(frame.children_iter)
                stack.append(
                    Frame(key=child_key, node=child_value, depth=frame.depth + 1)
                )
            except StopIteration:
                # all children resolved
                value = self.policy.rebuild(frame.node, frame.resolved_children.values())
                stack.pop()
                storage = self.get_result_storage(stack, default=result_storage)
                storage[frame.key] = value

        return result_storage[None]
