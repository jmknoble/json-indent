"""
Provide utility functions for strings, dicts, etc.
"""


def is_string(an_object):
    """
    Tell whether a given object refers to a string.

    We do this in a Python-version-indpendent way.

    :Args:
        an_object
            a given Python object

    :Returns:
        `True`-ish if `an_object` is a Python string, `False` otherwise
    """
    try:
        return isinstance(an_object, basestring)
    except NameError:  # Python 3: "NameError: name 'basestring' is not defined"
        return isinstance(an_object, str)


def to_unicode(text):
    """
    Convert the given string to a unicode string, if applicable.

    :Args:
        text
            A string to convert

    :Returns:
        The string converted to a unicode string, if supported by the Python
        interpreter, otherwise the string with no conversion
    """
    try:
        return unicode(text)  # Python 2.x
    except NameError:  # Python 3.x
        return text


def pop_with_default(a_dict, key, default=None):
    """
    Pop a key from a dict and return its value or a default value.

    :Args:
        a_dict
            Dictionary to look for `key` in

        key
            Key to look for in `a_dict`

        default
            Default value to return if `key` is not present

    :Returns:
        `a_dict`[`key`] if `key` is present, otherwise `default`
    """
    return a_dict.pop(key) if key in a_dict else default


def padded(a_list, n, value=None):
    """
    Return a copy of `a_list` with length `n`.
    """
    a_list = list(a_list)
    padding_length = n - len(a_list)
    if padding_length <= 0:
        return a_list
    padding = [value] * padding_length
    return a_list + padding
