"""Tests for json_indent.util"""

from __future__ import absolute_import

import unittest

import json_indent.pyversion as pv
import json_indent.util as jiu

DUMMY_KEY_1 = "DummyKey1"
DUMMY_KEY_2 = "DummyKey2"
DUMMY_VALUE_1 = "DummyValue1"
DUMMY_VALUE_2 = "DummyValue2"
DUMMY_DICT = {DUMMY_KEY_1: DUMMY_VALUE_1}

# Keep flake8 from complaining
try:
    unicode()  # Python 2.x
except NameError:  # Python 3.x

    class unicode(str):
        pass


class TestJsonIndentUtil(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_JIU_000_pop_with_default(self):
        a_dict = DUMMY_DICT.copy()
        value = jiu.pop_with_default(a_dict, DUMMY_KEY_1)
        self.assertEqual(value, DUMMY_VALUE_1)
        self.assertNotIn(DUMMY_KEY_1, a_dict)
        self.assertEqual(len(a_dict), 0)

        a_dict = DUMMY_DICT.copy()
        value = jiu.pop_with_default(a_dict, DUMMY_KEY_2)
        self.assertIs(value, None)
        self.assertIn(DUMMY_KEY_1, a_dict)
        self.assertEqual(len(a_dict), 1)

        a_dict = DUMMY_DICT.copy()
        value = jiu.pop_with_default(a_dict, DUMMY_KEY_2, DUMMY_VALUE_2)
        self.assertEqual(value, DUMMY_VALUE_2)
        self.assertIn(DUMMY_KEY_1, a_dict)
        self.assertEqual(len(a_dict), 1)

        a_dict = DUMMY_DICT.copy()
        value = jiu.pop_with_default(a_dict, key=DUMMY_KEY_2, default=DUMMY_VALUE_2)
        self.assertEqual(value, DUMMY_VALUE_2)
        self.assertIn(DUMMY_KEY_1, a_dict)
        self.assertEqual(len(a_dict), 1)

    def test_JIU_100_to_unicode(self):
        x = jiu.to_unicode("x")
        if pv.python_version_is_at_least(3):
            self.assertIsInstance(x, str)
            self.assertEqual(x, "x")
        else:
            self.assertIsInstance(x, unicode)
            # fmt: off
            self.assertEqual(x, u"x")
            # fmt: on

    def test_JIU_200_is_string(self):
        for thing, expected in [
            ("x", True),
            (1, False),
            (1.0, False),
            ([1], False),
            ({"x": 1}, False),
            ({1}, False),
            (None, False),
        ]:
            result = jiu.is_string(thing)
            self.assertEqual(result, expected)

    def test_JIU_201_is_string_unicode(self):
        if pv.python_version_is_less_than(3):
            # fmt: off
            for thing, expected in [
                (u"x", True),
            ]:
                result = jiu.is_string(thing)
                self.assertEqual(result, expected)
            # fmt: on

    def test_JIU_300_padded(self):
        for original, n, expected in [
            ([], 2, [None, None]),
            ([1], 2, [1, None]),
            ([1, 2], 2, [1, 2]),
            ([1, 2, 3], 2, [1, 2, 3]),
        ]:
            x = jiu.padded(original, n)
            self.assertListEqual(x, expected)

    def test_JIU_300_padded_value(self):
        for original, n, value, expected in [
            ([], 2, 0, [0, 0]),
            ([1], 2, 0, [1, 0]),
            ([1, 2], 2, 0, [1, 2]),
            ([1, 2, 3], 2, 0, [1, 2, 3]),
        ]:
            x = jiu.padded(original, n, value)
            self.assertListEqual(x, expected)

            x = jiu.padded(original, n, value=value)
            self.assertListEqual(x, expected)
