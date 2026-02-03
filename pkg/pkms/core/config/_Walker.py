from ._Frame import Frame
from ._exceptions import ConfigResolutionError

class Walker:
    def __init__(self, *, policy, max_depth=64):
        self.policy = policy
        self.max_depth = max_depth

    def walk(self, root, *, context):
        stack: list[Frame] = []
        stack.append(Frame(node=root, depth=0))

        result = None

        while stack:
            frame = stack[-1]

            if frame.depth > self.max_depth:
                raise ConfigResolutionError(f"Maximum depth {self.max_depth} exceeded at node {frame.node}")

            # leaf node
            if self.policy.is_leaf(frame.node):
                value = self.policy.resolve_leaf(
                    frame.node, context=context
                )
                stack.pop()
                if stack:
                    stack[-1].resolved_children.append(value)
                else:
                    result = value
                continue

            # first time we see this node
            if frame.children_iter is None:
                frame.children_iter = self.policy.iter_children(frame.node)

            try:
                child = next(frame.children_iter)
                stack.append(
                    Frame(node=child, depth=frame.depth + 1)
                )
            except StopIteration:
                # all children resolved
                value = self.policy.rebuild(
                    frame.node,
                    frame.resolved_children,
                )
                stack.pop()
                if stack:
                    stack[-1].resolved_children.append(value)
                else:
                    result = value

        return result
