import re
import string
from typing import Any, Mapping, Sequence

# ----------------------------------------------------------------------
# Helper that walks the root using a list of keys / indices.
# ----------------------------------------------------------------------
def get_nest_item(root: Any, steps: list[Any]) -> Any:
    """
    Walk ``root`` by performing ``root[step]`` for every ``step`` in *steps*.
    ``step`` may be a string (dictionary key) or an int (list/tuple index).

    Raises:
        KeyError / IndexError / TypeError – if a step cannot be satisfied.
        ValueError – if an integer index is out of the configured safe range.
    """
    obj = root
    for step in steps:
        # ``obj`` must support the root protocol for the given step.
        try:
            obj = obj[step]
        except Exception as exc:
            # Add context to the error – it is extremely helpful when the
            # format string is long.
            raise type(exc)(f"Failed to resolve step {step!r} on {obj!r}: {exc}") from exc
    return obj


# ----------------------------------------------------------------------
# The formatter
# ----------------------------------------------------------------------
class SafeNestFormatter(string.Formatter):
    """
    *Only* ``{field}`` syntax with *nested getitem* look‑ups is allowed.
    Dot‑notation (``a.b.c``) and bracket‑notation (``a[0]["b"]``) are parsed
    into a sequence of keys/indices that are then resolved via ``obj[key]``.
    Attribute access (``obj.attr``) is explicitly forbidden.
    """

    # ------------------------------------------------------------------
    # Configuration (tweak these constants to tighten / loosen the policy)
    # ------------------------------------------------------------------
    MAX_NESTING = 30            # maximum number of look‑ups in a single field
    MAX_INDEX   = 10_000        # reject integer indices > this value
    MAX_WIDTH   = 1_000         # same limit you already had for format specifiers
    # ------------------------------------------------------------------

    _BRACKET_RE = re.compile(
        r"""
        (?P<dot>\.)?                # optional leading dot (ignored after the 1st token)
        (?:
            # ----  a) plain identifier  -------------------------
            (?P<name>[A-Za-z_]\w*)                  # foo, bar_123 …
            |
            # ----  b) numeric identifier (dot‑number) -------
            (?P<num>\d+)                            # 0, 1, 42 …
            |
            # ----  c) bracketed indexing -----------------------
            \[
                (?:
                    (?P<int>\d+)                     # [0] , [123] # pure integer index
                    |
                    (?P<str>'[^']*' | "[^"]*")       # ['key'] , ["key"] # quoted string index
                )
            \]
        )
        """,
        re.VERBOSE,
    )

    # ------------------------------------------------------------------
    #   1)  Turn the *field_name* string into a list of look‑up steps.
    # ------------------------------------------------------------------
    @classmethod
    def _tokenise(cls, field_name: str) -> list[Any]:
        """
        Convert a field name like ``a.b[0]["c"].d`` into the list
        ``['a', 'b', 0, 'c', 'd']``.
        A ``ValueError`` is raised for any syntax we do not understand.
        """
        if not field_name:
            raise ValueError("Empty field name")

        pos = 0 
        steps: list[Any] = []

        while pos < len(field_name):
            m = cls._BRACKET_RE.match(field_name, pos)
            if not m:
                # Capture the offending snippet for a nice error message.
                snippet = field_name[pos : pos + 10]
                raise ValueError(f"Invalid field syntax near '{snippet}'")

            dot = m.group("dot")
            if not steps and dot:
                # DOT should present initially, e.g. `.prop`
                raise ValueError('Invalid field with prefix dot')
            elif steps and not dot and not field_name[pos] == '[':
                # DOT should present to connect steps afterward if not bracketed, e.g. `a["b"].c`
                raise ValueError('Invalid field without dot connecting between steps')
            else:
                # Nothing to do – just a separator.
                pass

            # Resolve the token.
            if m.group("name"):
                steps.append(m.group("name"))
            elif m.group("num"):                    # numeric identifier after a dot
                idx = int(m.group("num"))
                if idx > cls.MAX_INDEX:
                    raise ValueError(f"Index {idx!r} exceeds safe limit ({cls.MAX_INDEX})")
                steps.append(idx)
            elif m.group("int"):
                idx = int(m.group("int"))
                if idx > cls.MAX_INDEX:
                    raise ValueError(f"Index {idx!r} exceeds safe limit ({cls.MAX_INDEX})")
                steps.append(idx)
            elif m.group("str"):
                # Strip the surrounding quotes; keep the raw string as key.
                raw = m.group("str")
                steps.append(raw[1:-1])
            else:
                # Should never happen because the regex has exhaustive groups.
                raise RuntimeError("Regex matched but produced no token")

            pos = m.end()

        # Safety guard – too deep a nesting can be used for DoS.
        if len(steps) > cls.MAX_NESTING:
            raise ValueError(
                f"Field '{field_name}' is too deeply nested (>{cls.MAX_NESTING} levels)"
            )
        if any(step == '' for step in steps):
            raise RuntimeError(f'Empty step is not allowed, steps={steps!r}')
        return steps

    # ------------------------------------------------------------------
    #   2)  Resolve a field name against the supplied *root*.
    # ------------------------------------------------------------------
    def get_field(self, field_name, args, kwargs):
        """
        ``field_name`` is the *raw* string that appears between the braces.
        We look for a ``root`` keyword argument that holds the root data
        container (the same thing you passed to ``format_map`` before).

        Example:
            fmt = SafeNestFormatter()
            fmt.format("{user.name.first}", root=data)
        """
        # The root data container must be supplied under the name ``root``.
        # (You can rename the kw‑arg if you like – just change the lookup below.)
        try:
            root = kwargs["root"]
        except KeyError as exc:
            raise KeyError(
                "SafeNestFormatter expects a keyword argument named 'root' that "
                "holds the top‑level container."
            ) from exc

        # 1️⃣ Tokenise the field name into look‑up steps.
        steps = self._tokenise(field_name)

        # 2️⃣ Walk the container using ``get_nest_item``.
        value = get_nest_item(root, steps)

        # ``get_field`` in the base class returns a tuple ``(obj, used_key)``.
        # ``used_key`` is the *original* string that the formatter used to fetch
        # the value from *args / kwargs* – we reuse the raw field name here.
        return (value, field_name)

    # ------------------------------------------------------------------
    #   3)  Attribute access – *always* forbidden.
    # ------------------------------------------------------------------
    def get_attribute(self, obj, attr, format_spec):
        raise AttributeError(
            f"Attribute access is disallowed for security reasons: tried to get "
            f"'{attr}' on {obj!r}"
        )

    # ------------------------------------------------------------------
    #   4)  Optional width/precision throttling (your original code)
    # ------------------------------------------------------------------
    def format_field(self, value, format_spec):
        try:
            if format_spec:
                # Look for any integer that could be used as width/precision.
                # This is a very cheap “good‑enough” test.  If you need
                # stricter validation, replace the generator with a proper regex.
                numbers = (int(num) for num in re.findall(r"\d+", format_spec))
                if any(n > self.MAX_WIDTH for n in numbers):
                    raise ValueError(
                        f"Format width/precision exceeds safe limit ({self.MAX_WIDTH})"
                    )
        except ValueError as exc:
            raise ValueError(
                f"Unsafe format specification '{format_spec}': {exc}"
            ) from exc

        return super().format_field(value, format_spec)

    # ------------------------------------------------------------------
    #   5)  Convenience wrapper – behaves like ``str.format`` but forces the
    #       safety contract.
    # ------------------------------------------------------------------
    def vformat(self, format_string, args, kwargs):
        """
        ``string.Formatter.vformat`` is the core implementation that calls
        ``get_field``, ``get_attribute`` and ``format_field``.  We forward to it
        unchanged – the overrides above already contain all the safety logic.
        """
        return super().vformat(format_string, args, kwargs)


# ----------------------------------------------------------------------
# Example usage & simple tests
# ----------------------------------------------------------------------
if __name__ == "__main__":
    data = {
        "user": {
            "name": {"first": "Ada", "last": "Lovelace"},
            "contacts": [
                {"type": "email", "value": "ada@example.com"},
                {"type": "phone", "value": "+1‑000‑000‑0000"},
            ],
        },
        "a": [{"b": 42}, {"c": "hello"}],
    }

    fmt = SafeNestFormatter()
    x = fmt._tokenise("a[0]b")
    print(x)

    # Simple dot‑only nesting
    print(fmt.format("{user.name.first}", root=data))          # Ada

    # Mixed dot + bracket indexing
    print(fmt.format("{user.contacts[1].value}", root=data))   # +1‑000‑000‑0000

    # Indexing into a list of dicts
    print(fmt.format("{a[0].b}", root=data))                  # 42
    print(fmt.format("{a[1].c}", root=data))                  # hello

    # ------------------------------------------------------------------
    #  Demonstrating the protection mechanisms
    # ------------------------------------------------------------------
    try:
        fmt.format("{user.__dict__}", root=data)
    except KeyError as e:
        print("✔ Attribute blocked:", e)

    try:
        fmt.format("{user.contacts[999].value}", root=data)
    except Exception as e:          # will raise IndexError wrapped by get_nest_item
        print("✔ Bad index blocked:", e)

    try:
        fmt.format("{user.name.first[0]}", root=data)  # attempts a *second* level
    except Exception as e:
        print("✔ Nested getitem on a string blocked:", e)

    # Too‑large width in format specifier → DoS protection
    try:
        fmt.format("{user.name.first:10000}", root=data)
    except ValueError as e:
        print("✔ Width limit enforced:", e)

