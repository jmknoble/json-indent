"""
Provide functions for comparing Python versions.
"""

from __future__ import absolute_import

import sys

from json_indent.util import padded


def get_python_version():
    """Return the Python version as a tuple."""
    vi = sys.version_info
    return (vi.major, vi.minor, vi.micro)


def pad_version_tuples(v1, v2):
    """Pad version tuples out to their longest length."""
    n = max(len(v1), len(v2))
    return (
        padded(v1, n, 0),
        padded(v2, n, 0),
    )


def compare_eq(x, y):
    """Use to compare values for equality with `map()`:py:func:."""
    return x == y


def compare_gt(x, y):
    """Use to compare values for inequality with `map()`:py:func:."""
    return x > y


def compare_lt(x, y):
    """Use to compare values for inequality with `map()`:py:func:."""
    return x < y


def version_is_at_least(v1, v2):
    """Return `True`-ish if v1 >= v2."""
    (v1, v2) = pad_version_tuples(v1, v2)
    for is_greater, is_equal in zip(map(compare_gt, v1, v2), map(compare_eq, v1, v2)):
        if is_greater:
            return True
        if not is_equal:
            return False
    return True


def version_is_at_most(v1, v2):
    """Return `True`-ish if v1 <= v2."""
    (v1, v2) = pad_version_tuples(v1, v2)
    for is_less, is_equal in zip(map(compare_lt, v1, v2), map(compare_eq, v1, v2)):
        if is_less:
            return True
        if not is_equal:
            return False
    return True


def version_is_greater_or_equal(v1, v2):
    """Alias for `~json_indent.pyversion.version_is_at_least()`:py:func:."""
    return version_is_at_least(v1, v2)


def version_is_less_or_equal(v1, v2):
    """Alias for `~json_indent.pyversion.version_is_at_most()`:py:func:."""
    return version_is_at_most(v1, v2)


def version_is_greater_than(v1, v2):
    """Return `True`-ish if v1 > v2."""
    return not version_is_less_or_equal(v1, v2)


def version_is_less_than(v1, v2):
    """Return `True`-ish if v1 < v2."""
    return not version_is_greater_or_equal(v1, v2)


def python_version_is_at_least(major, minor=0, micro=0):
    """Return `True`-ish if the Python version >= the given version."""
    return version_is_at_least(get_python_version(), (major, minor, micro))


def python_version_is_at_most(major, minor=0, micro=0):
    """Return `True`-ish if the Python version <= the given version."""
    return version_is_at_most(get_python_version(), (major, minor, micro))


def python_version_is_greater_or_equal(major, minor=0, micro=0):
    """Alias for `~json_indent.pyversion.python_version_is_at_least()`:py:func:."""
    return python_version_is_at_least(major, minor, micro)


def python_version_is_less_or_equal(major, minor=0, micro=0):
    """Alias for `~json_indent.pyversion.python_version_is_at_most()`:py:func:."""
    return python_version_is_at_most(major, minor, micro)


def python_version_is_greater_than(major, minor=0, micro=0):
    """Return `True`-ish if the Python version > the given version."""
    return version_is_greater_than(get_python_version(), (major, minor, micro))


def python_version_is_less_than(major, minor=0, micro=0):
    """Return `True`-ish if the Python version < the given version."""
    return version_is_less_than(get_python_version(), (major, minor, micro))
