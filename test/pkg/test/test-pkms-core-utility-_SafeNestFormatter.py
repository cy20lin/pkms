import re
import string
import pytest
import logging


from pkms.core.utility import(
    SafeNestFormatter, get_nest_item 
)

# Logger setup
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# A tiny reusable fixture that returns a rich nested data structure.
# ----------------------------------------------------------------------
def _make_deep(max_level=30, next_key='n', level_key='l'):
    assert max_level >= 0
    level_data = None
    for i in reversed(range(1, max_level+1)):
        level_data = { level_key: i, next_key: level_data}
    return level_data

@pytest.fixture
def data():
    return {
        "user": {
            "name": {"first": "Ada", "last": "Lovelace"},
            "contacts": [
                {"type": "email", "value": "ada@example.com"},
                {"type": "phone", "value": "+1‑555‑123‑4567"},
            ],
        },
        "a": [{"b": 42}, {"c": "hello"}],
        "big_index": list(range(2000)),
        "deep": _make_deep(max_level=30, next_key='n', level_key='l'),  # 30 levels deep
    }

# ----------------------------------------------------------------------
# Helper – a thin wrapper around the formatter that mirrors the usual
# ``str.format`` call but forces the ``root=`` keyword.
# ----------------------------------------------------------------------
def fmt(template: str, root: dict) -> str:
    return SafeNestFormatter().format(template, root=root)


# ----------------------------------------------------------------------
# 1️⃣  Tokeniser tests – we test the private classmethod directly.
# ----------------------------------------------------------------------
@pytest.mark.parametrize(
    "field,expected",
    [
        ("a", ["a"]),
        ("a.b", ["a", "b"]),
        ("a[0]", ["a", 0]),
        ("a[0].b", ["a", 0, "b"]),
        ("a[0][1].c", ["a", 0, 1, "c"]),
        ("a['foo']", ["a", "foo"]),
        ('a["foo"]', ["a", "foo"]),
        ("nested[12].value[3].x", ["nested", 12, "value", 3, "x"]),
    ],
)
def test_tokeniser_basic(field, expected):
    steps = SafeNestFormatter._tokenise(field)
    assert steps == expected


@pytest.mark.parametrize(
    "bad_field",
    [
        "",                 # empty
        ".a",               # prefix dot
        "a..b",             # double dot
        "a[",               # missing closing ]
        "a[]",              # empty brackets
        "a[foo",            # missing ]
        "a[0]b",            # missing dot between tokens
        "a[0].",            # trailing dot
        "a[0].b[",          # dangling [
        "a[99999999]",      # index > MAX_INDEX (default 10_000)
        "a[0][1][2][3][4].b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z",  # > MAX_NESTING
    ]
)
def test_tokeniser_rejects_invalid_syntax(bad_field):
    # assert bad_field == ''
    with pytest.raises(ValueError, match="Invalid field|Empty field|exceeds|too deep"):
        SafeNestFormatter._tokenise(bad_field)


# ----------------------------------------------------------------------
# 2️⃣  Successful formatting – nested getitem access only.
# ----------------------------------------------------------------------
def test_simple_dot_notation(data):
    assert fmt("{user.name.first}", data) == "Ada"
    assert fmt("{user.name.last}", data) == "Lovelace"


def test_mixed_dot_and_bracket(data):
    # contacts[1] → second contact (phone); then .value → the phone number
    assert fmt("{user.contacts[1].value}", data) == "+1‑555‑123‑4567"
    # a[0].b → first dict in list “a”, then key “b”
    assert fmt("{a[0].b}", data) == "42"
    # a[1].c → second dict in list “a”, then key “c”
    assert fmt("{a[1].c}", data) == "hello"


def test_quoted_string_keys(data):
    # Use a key that contains a dot or a space – it must be quoted.
    data["weird"] = {"key.with.dots": 123, "sp ace": "ok"}
    assert fmt("{weird['key.with.dots']}", data) == "123"
    assert fmt('{weird["sp ace"]}', data) == "ok"


def test_deep_nesting_is_allowed_up_to_limit(data):
    # The fixture creates 1+30 levels (`deep.n.n.n.n.val`)
    # 30 is the default MAX_NESTING – it should succeed.
    assert fmt("{deep"+".n"*29+"}", data) == "{'l': 30, 'n': None}"
    assert fmt("{deep"+".n"*28+".l}", data) == "29"


# ----------------------------------------------------------------------
# 3️⃣  Safety / error handling
# ----------------------------------------------------------------------
@pytest.mark.parametrize(
    "template,expected_exc,match",
    [
        # Attribute access is never allowed, and such access would be 
        # redirected to __getitem__ access for safty
        ("{user.__dict__}", KeyError, "Failed to resolve"), # accessing non existing key "__dict__" on dict type
        ("{user.name.first.__class__}", TypeError, "string indices must be integers"), # accessing index with non-int "__class__" on str type
        # Index out of range / missing key
        ("{user.contacts[99].value}", IndexError, "list index out of range"),
        ("{a[5].b}", IndexError, "list index out of range"),
        ("{nonexistent}", KeyError, "nonexistent"),
        # Too‑large integer index (MAX_INDEX = 10_000)
        ("{big_index[15000]}", ValueError, "exceeds safe limit"),
        # Exceed max nesting depth (MAX_NESTING = 30), supplied depth=31
        ("{deep."+'n.'*29 +"l}", ValueError, "too deep"),
        # Width/precision limit in format specifier (MAX_WIDTH = 1_000)
        ("{user.name.first:1001}", ValueError, "exceeds safe limit"),
    ],
)
def test_errors_and_limits(template, expected_exc, match, data):
    with pytest.raises(expected_exc, match=match):
        fmt(template, data)


# ----------------------------------------------------------------------
# 4️⃣  Direct tests of the low‑level helper ``get_nest_item``.
# ----------------------------------------------------------------------
def test_get_nest_item_simple_dict():
    root = {"a": {"b": 1}}
    assert get_nest_item(root, ["a", "b"]) == 1


def test_get_nest_item_list_and_dict_mix():
    root = {"x": [{"y": 10}, {"z": 20}]}
    assert get_nest_item(root, ["x", 1, "z"]) == 20


def test_get_nest_item_raises_on_missing_key():
    root = {"a": {}}
    with pytest.raises(KeyError):
        get_nest_item(root, ["a", "missing"])


def test_get_nest_item_raises_on_wrong_type():
    root = {"a": 5}
    # Trying to sub‑script an int should raise TypeError (or whatever the object raises)
    with pytest.raises(Exception) as exc:
        get_nest_item(root, ["a", "anything"])
    assert isinstance(exc.value, (TypeError, KeyError))


# ----------------------------------------------------------------------
# 5️⃣  Integration test – ensure that the formatter *continues* after a
#     successful substitution but raises on the *first* unsafe field.
# ----------------------------------------------------------------------
def test_mixed_safe_and_unsafe_fields(data):
    # The first field is safe, the second tries attribute access → should raise.
    tmpl = "{user.name.first} – {user.__class__}"
    with pytest.raises(KeyError, match="Failed to resolve"):
        fmt(tmpl, data)


# ----------------------------------------------------------------------
# 6️⃣  Verify that the formatter does not touch the original root.
# ----------------------------------------------------------------------
def test_formatter_is_readonly(data):
    # Make a shallow copy and compare after formatting – the formatter must not modify the dict.
    import copy
    original = copy.deepcopy(data)
    fmt("{user.name.first} {a[0].b} {user.contacts[0].value}", data)
    assert data == original, "Formatter mutated the input root"


# ----------------------------------------------------------------------
# 7️⃣  Edge case – format specifiers that contain numbers but are still safe.
# ----------------------------------------------------------------------
def test_format_specifiers_allow_small_numbers(data):
    # ``{:0>5}`` pads with zeros to a width of 5 – numbers are < MAX_WIDTH → OK
    assert fmt("{user.name.first:0>5}", data) == "00Ada"
    # ``{a[0].b:.2f}`` – the ``2`` is a precision, also safe
    assert fmt("{a[0].b:.2f}", data) == "42.00"


# ----------------------------------------------------------------------
# 8️⃣  Validate that the internal regex does NOT permit stray dots.
# ----------------------------------------------------------------------
def test_invalid_dot_places():
    with pytest.raises(ValueError):
        SafeNestFormatter._tokenise(".a")
    with pytest.raises(ValueError):
        SafeNestFormatter._tokenise("a..b")
    with pytest.raises(ValueError):
        SafeNestFormatter._tokenise("a.")  # trailing dot

# ----------------------------------------------------------------------
# 9️⃣  Verify that the class constants can be overridden safely (optional).
# ----------------------------------------------------------------------
def test_custom_limits():
    class TinyFormatter(SafeNestFormatter):
        MAX_NESTING = 3
        MAX_INDEX   = 2
        MAX_WIDTH   = 5

    tiny = TinyFormatter()
    # Within limits – OK
    assert tiny.format("{a[1].b}", root={"a": [{}, {"b": 99}]}) == "99"

    # Exceed nesting
    with pytest.raises(ValueError, match="too deep"):
        tiny.format("{a[0].b.c}", root={"a": [{"b": {"c": 1}}]})

    # Exceed index limit
    with pytest.raises(ValueError, match="exceeds safe limit"):
        tiny.format("{a[3]}", root={"a": [0, 1, 2, 3]})

    # Exceed width limit
    with pytest.raises(ValueError, match="exceeds safe limit"):
        tiny.format("{a[0]:99999}", root={"a": [1]})

#
# 10. test dot‑notation to also work with numeric keys
# e.g. "{data.1.x}" ==> data[1]["x"]

def test_numeric_dot_access():
    # A list of dicts inside a dict
    data = {"data": [ {"x": 10}, {"x": 20}, {"x": 30} ]}

    # dot‑numeric syntax
    assert fmt("{data.0.x}", data) == "10"
    assert fmt("{data.2.x}", data) == "30"

    # still works with the original bracket form
    assert fmt("{data[1].x}", data) == "20"

# --------------------------
# script entry point
# --------------------------

if __name__ == "__main__":
    import sys
    code = pytest.main([__file__])
    sys.exit(code)