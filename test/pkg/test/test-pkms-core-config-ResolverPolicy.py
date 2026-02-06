"""Tests for the config resolver components: Walker and ResolverPolicy.

The tests cover:
- Leaf detection and resolution for primitive, string, dict, list, and tuple nodes.
- Child iteration and rebuilding of container nodes.
- Walker traversal including max‑depth error handling.
"""

import pytest

from pkms.core.config._Walker import Walker
from pkms.core.config._ResolverPolicy import ResolverPolicy
from pkms.core.config._exceptions import ConfigResolutionError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def policy():
    return ResolverPolicy()

@pytest.fixture
def walker(policy):
    # Use a small max_depth for normal tests; specific max‑depth test overrides it.
    return Walker(policy=policy, max_depth=64)

@pytest.fixture
def dummy_context():
    # BracesRefResolver expects a dict as the root context.
    return {}

# ---------------------------------------------------------------------------
# ResolverPolicy unit tests
# ---------------------------------------------------------------------------

def test_is_leaf_primitive(policy):
    assert policy.is_leaf(42) is True
    assert policy.is_leaf(True) is True
    assert policy.is_leaf(None) is True

def test_is_leaf_string(policy):
    assert policy.is_leaf("hello") is True

def test_is_leaf_container(policy):
    assert policy.is_leaf({"k": 1}) is False
    assert policy.is_leaf([1, 2]) is False
    assert policy.is_leaf((1, 2)) is False

def test_resolve_leaf_string(policy, dummy_context):
    # No braces in the string, resolver should return the original value.
    value = "plain_string"
    assert policy.resolve_leaf(value, context=dummy_context) == value

def test_iter_children_dict(policy):
    node = {"a": 1, "b": 2}
    children = list(policy.iter_children(node))
    assert children == [1, 2]

def test_iter_children_list(policy):
    node = [10, 20, 30]
    children = list(policy.iter_children(node))
    assert children == node

def test_iter_children_tuple(policy):
    node = ("x", "y")
    children = list(policy.iter_children(node))
    assert children == ["x", "y"]

def test_rebuild_dict(policy):
    original = {"a": 1, "b": 2}
    children = [10, 20]
    rebuilt = policy.rebuild(original, children)
    assert rebuilt == {"a": 10, "b": 20}

def test_rebuild_list(policy):
    original = [1, 2, 3]
    children = [4, 5, 6]
    rebuilt = policy.rebuild(original, children)
    assert rebuilt == [4, 5, 6]

def test_rebuild_tuple(policy):
    original = ("x", "y")
    children = ["a", "b"]
    rebuilt = policy.rebuild(original, children)
    assert rebuilt == ("a", "b")

def test_unsupported_node_type(policy):
    class Custom:  # not handled by any handler
        pass
    with pytest.raises(TypeError):
        policy.is_leaf(Custom())

# ---------------------------------------------------------------------------
# Walker integration tests
# ---------------------------------------------------------------------------

def test_walker_resolves_structure(walker, dummy_context):
    config = {
        "num": 1,
        "text": "hello",
        "list": [2, 3],
        "tuple": ("a", "b"),
        "nested": {"inner": "value"},
    }
    result = walker.walk(config, context=dummy_context)
    assert result == config

def test_walker_max_depth_error():
    policy = ResolverPolicy()
    # Create a deeply nested list exceeding the default max_depth of 64.
    depth = 70
    nested = []
    current = nested
    for _ in range(depth):
        new = []
        current.append(new)
        current = new
    walker = Walker(policy=policy, max_depth=64)
    with pytest.raises(ConfigResolutionError):
        walker.walk(nested, context={})

"""
The tests cover:
- Leaf detection and resolution for primitive, string, dict, list, and tuple nodes.
- Child iteration and rebuilding of container nodes.
- Walker traversal including max‑depth error handling.
"""

import pytest

from pkms.core.config._Walker import Walker
from pkms.core.config._ResolverPolicy import ResolverPolicy
from pkms.core.config._exceptions import ConfigResolutionError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def policy():
    return ResolverPolicy()

@pytest.fixture
def walker(policy):
    # Use a small max_depth for normal tests; specific max‑depth test overrides it.
    return Walker(policy=policy, max_depth=64)

@pytest.fixture
def dummy_context():
    # BracesRefResolver expects a dict as the root context.
    return {}

# ---------------------------------------------------------------------------
# ResolverPolicy unit tests
# ---------------------------------------------------------------------------

def test_is_leaf_primitive(policy):
    assert policy.is_leaf(42) is True
    assert policy.is_leaf(True) is True
    assert policy.is_leaf(None) is True

def test_is_leaf_string(policy):
    assert policy.is_leaf("hello") is True

def test_is_leaf_container(policy):
    assert policy.is_leaf({"k": 1}) is False
    assert policy.is_leaf([1, 2]) is False
    assert policy.is_leaf((1, 2)) is False

def test_resolve_leaf_string(policy, dummy_context):
    # No braces in the string, resolver should return the original value.
    value = "plain_string"
    from pkms.core.utility import SimpleNestItemGetter
    assert policy.resolve_leaf(value, context=dummy_context, getter=SimpleNestItemGetter()) == value

def test_iter_children_dict(policy):
    node = {"a": 1, "b": 2}
    children = list(policy.iter_children(node))
    assert children == list(node.items())

def test_iter_children_list(policy):
    node = [10, 20, 30]
    children = list(policy.iter_children(node))
    assert children == list(enumerate(node))

def test_iter_children_tuple(policy):
    node = ("x", "y")
    children = list(policy.iter_children(node))
    assert children == list(enumerate(node))

def test_rebuild_dict(policy):
    original = {"a": 1, "b": 2}
    children = [10, 20]
    rebuilt = policy.rebuild(original, children)
    assert rebuilt == {"a": 10, "b": 20}

def test_rebuild_list(policy):
    original = [1, 2, 3]
    children = [4, 5, 6]
    rebuilt = policy.rebuild(original, children)
    assert rebuilt == [4, 5, 6]

def test_rebuild_tuple(policy):
    original = ("x", "y")
    children = ["a", "b"]
    rebuilt = policy.rebuild(original, children)
    assert rebuilt == ("a", "b")

def test_unsupported_node_type(policy):
    class Custom:  # not handled by any handler
        pass
    with pytest.raises(TypeError):
        policy.is_leaf(Custom())

# ---------------------------------------------------------------------------
# Walker integration tests
# ---------------------------------------------------------------------------

def test_walker_resolves_structure(walker, dummy_context):
    config = {
        "num": 1,
        "text": "hello",
        "list": [2, 3],
        "tuple": ("a", "b"),
        "nested": {"inner": "value"},
    }
    result = walker.walk(config, context=dummy_context, base_keys=())
    assert result == config

def test_walker_max_depth_error():
    policy = ResolverPolicy()
    # Create a deeply nested list exceeding the default max_depth of 64.
    depth = 70
    nested = []
    current = nested
    for _ in range(depth):
        new = []
        current.append(new)
        current = new
    walker = Walker(policy=policy, max_depth=64)
    with pytest.raises(ConfigResolutionError):
        walker.walk(nested, context={}, base_keys=())

