# test_file_location.py
import os
import pytest
from pkms.core.model import FileLocation

def test_segments_concat():
    loc = FileLocation(
        scheme="file",
        authority="",
        base_segments=(None, "a", "b"),
        sub_segments=("c", "d"),
    )

    assert loc.segments == (None, "a", "b", "c", "d")

def test_posix_filesystem_paths_simple():
    loc = FileLocation(
        scheme="file",
        authority="",
        base_segments=(None, "home", "user"),
        sub_segments=("docs", "a.txt"),
    )
    assert loc.to_filesystem_base_path('posix') == "/home/user"
    assert loc.to_filesystem_sub_path('posix') == "docs/a.txt"
    assert loc.to_filesystem_path('posix') == "/home/user/docs/a.txt"

def test_windows_filesystem_paths_simple():
    loc = FileLocation(
        scheme="file",
        authority="",
        base_segments=(None, "c:", "Users", "user"),
        sub_segments=("docs", "a.txt"),
    )
    assert loc.to_filesystem_base_path('windows') == "c:/Users/user"
    assert loc.to_filesystem_sub_path('windows') == "docs/a.txt"
    assert loc.to_filesystem_path('windows') == "c:/Users/user/docs/a.txt"

###
# Layer 0: PathSegments invariant
#
import pytest
from pydantic import ValidationError



# ---------- helpers ----------

def make_fl(base_segments, sub_segments=()):
    return FileLocation(
        base_segments=base_segments,
        sub_segments=sub_segments,
    )


# ---------- valid cases ----------

def test_empty_segments_are_valid():
    fl = make_fl(())
    assert fl.base_segments == ()
    assert fl.sub_segments == ()


def test_relative_single_segment():
    fl = make_fl(("a",))
    assert fl.base_segments == ("a",)


def test_relative_multi_segments():
    fl = make_fl(("a", "b", "c"))
    assert fl.base_segments == ("a", "b", "c")


def test_absolute_marker_only():
    fl = make_fl((None,))
    assert fl.base_segments == (None,)


def test_absolute_with_children():
    fl = make_fl((None, "a", "b"))
    assert fl.base_segments == (None, "a", "b")


def test_sub_segments_can_be_empty_or_relative():
    fl = make_fl((None, "a"), ("b", "c"))
    assert fl.sub_segments == ("b", "c")


# ---------- invalid cases ----------

@pytest.mark.parametrize(
    "segments",
    [
        ("a", None),
        (None, "a", None),
        ("a", None, "b"),
        (None, None),
        (None, None, "a"),
    ],
)
def test_none_not_allowed_after_first_position(segments):
    with pytest.raises(ValidationError) as exc:
        make_fl(segments)

    msg = str(exc.value)
    assert "Only the first path segment may be None" in msg


@pytest.mark.parametrize(
    "segments",
    [
        ("a", "b", None),
        ("x", None, "y", "z"),
    ],
)
def test_none_in_sub_segments_is_invalid(segments):
    with pytest.raises(ValidationError):
        make_fl((), segments)

# Layer1

@pytest.mark.parametrize(
    'uri,base_uri_path,scheme,authority,base_segments,sub_segments',
    [
        ('file:///'   , None, 'file'  , ''  , (), (None,'')        ), # should preserve empty segment
        ('file:///a/b', None, 'file'  , ''  , (), (None, 'a', 'b') ),

        ('scheme:'    , None, 'scheme', None, (), ()               ),
        ('scheme:a'   , None, 'scheme', None, (), ('a',)           ),
        ('scheme:a/'  , None, 'scheme', None, (), ('a', '')        ),
        ('scheme:a/b' , None, 'scheme', None, (), ('a', 'b')       ),
        ('scheme:a/b/', None, 'scheme', None, (), ('a', 'b', '')   ),

        ('scheme:/'    , None, 'scheme', None, (), (None, '')             ),
        ('scheme:/a'   , None, 'scheme', None, (), (None, 'a',)           ),
        ('scheme:/a/'  , None, 'scheme', None, (), (None, 'a', '')        ),
        ('scheme:/a/b' , None, 'scheme', None, (), (None, 'a', 'b')       ),
        ('scheme:/a/b/', None, 'scheme', None, (), (None, 'a', 'b', '')   ),

        ('scheme://'    , None, 'scheme', '', (), ()             ),
        ('scheme://a'   , None, 'scheme', 'a', (), ()           ),
        ('scheme://a/'  , None, 'scheme', 'a', (), (None, '')        ),
        ('scheme://a/b' , None, 'scheme', 'a', (), (None, 'b')       ),
        ('scheme://a/b/', None, 'scheme', 'a', (), (None, 'b', '')   ),

        ('scheme:///'    , None, 'scheme', '', (), (None, '')             ),
        ('scheme:///a'   , None, 'scheme', '', (), (None, 'a',)           ),
        ('scheme:///a/'  , None, 'scheme', '', (), (None, 'a', '')        ),
        ('scheme:///a/b' , None, 'scheme', '', (), (None, 'a', 'b')       ),
        ('scheme:///a/b/', None, 'scheme', '', (), (None, 'a', 'b', '')   ),

        (''    , None, '', None, (), ()               ),
        ('a'   , None, '', None, (), ('a',)           ),
        ('a/'  , None, '', None, (), ('a', '')        ),
        ('a/b' , None, '', None, (), ('a', 'b')       ),
        ('a/b/', None, '', None, (), ('a', 'b', '')   ),

        ('/'    , None, '', None, (), (None, '')             ),
        ('/a'   , None, '', None, (), (None, 'a',)           ),
        ('/a/'  , None, '', None, (), (None, 'a', '')        ),
        ('/a/b' , None, '', None, (), (None, 'a', 'b')       ),
        ('/a/b/', None, '', None, (), (None, 'a', 'b', '')   ),

        ('//'    , None, '', '', (), ()             ),
        ('//a'   , None, '', 'a', (), ()           ),
        ('//a/'  , None, '', 'a', (), (None, '')        ),
        ('//a/b' , None, '', 'a', (), (None, 'b')       ),
        ('//a/b/', None, '', 'a', (), (None, 'b', '')   ),

        ('///'    , None, '', '', (), (None, '')             ),
        ('///a'   , None, '', '', (), (None, 'a',)           ),
        ('///a/'  , None, '', '', (), (None, 'a', '')        ),
        ('///a/b' , None, '', '', (), (None, 'a', 'b')       ),
        ('///a/b/', None, '', '', (), (None, 'a', 'b', '')   ),

    ],
)
def test_from_uri_split(uri, base_uri_path, scheme, authority, base_segments, sub_segments):
    fl = FileLocation.from_uri(uri, base_uri_path=base_uri_path)
    assert fl.scheme == scheme
    assert fl.authority == authority
    assert fl.base_segments == base_segments
    assert fl.sub_segments == sub_segments



@pytest.mark.parametrize(
    "base_segments,sub_segments,expected_path",
    [
        ((), (), ""),
        # NOTE: for segment (None,) there is no proper representation in URI
        # use '/' as approximation
        ((None,), (), "/"), 
         # Follow RFC 3986:
         # For consistency, # URI producers and normalizers 
         # should use uppercase hexadecimal digits
         # for all percent encodings.
         # so %2F not %2f
        ((None, "a", "b/c"), (), "/a/b%2Fc"),
        ((None, "a", "b"), (), "/a/b"),
        (("a", "b"), (), "a/b"),
        ((None, "a"), ("b", "c"), "/a/b/c"),
    ],
)
def test_uri_path_rendering(base_segments, sub_segments, expected_path):
    fl = FileLocation(
        base_segments=base_segments,
        sub_segments=sub_segments,
    )
    assert fl.uri_path == expected_path

# # Layer2
# import pytest

@pytest.mark.parametrize( 
    "base,sub,expected",
    [
        ((), (), ()),
        (("a",), ("b",), ("a", "b")),
        ((None, "a"), ("b",), (None, "a", "b")),
        (("a",), (None, "b"), (None, "b")),
        ((None, "a"), (None, "b"), (None, "b")),
        ((None, "a"), (), (None, "a")),
    ],
)
def test_segments_join(base, sub, expected):
    fl = FileLocation(
        base_segments=base,
        sub_segments=sub,
    )
    assert fl.segments == expected

# Layer3
@pytest.mark.parametrize(
    "segments,expected",
    [
        ((), ""),
        (("a", "b"), "a/b"),
        ((None,), "/"),
        ((None, "a", "b"), "/a/b"),
    ],
)
def test_posix_projection(segments, expected):
    fl = FileLocation.from_segments(segments)
    assert fl.to_filesystem_path("posix") == expected

@pytest.mark.parametrize(
    "segments,expected",
    [
        (("a", "b"), "a/b"),
        ((None, "a:", "b"), "a:/b"),
    ],
)
def test_windows_projection(segments, expected):
    fl = FileLocation.from_segments(segments)
    assert fl.to_filesystem_path("windows") == expected