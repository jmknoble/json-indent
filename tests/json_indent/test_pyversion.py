"""Tests for json_indent.pyversion"""

from __future__ import absolute_import

import sys
import unittest

import json_indent.pyversion as pv

EQUAL_VERSIONS = [
    ((), ()),
    ((), (0,)),
    ((0,), ()),
    ((0,), (0,)),
    ((1,), (1,)),
    ((1,), (1, 0)),
    ((1, 0), (1,)),
    ((1, 2), (1, 2)),
    ((1, 2), (1, 2, 0)),
    ((1, 2, 0), (1, 2)),
    ((1, 2, 3), (1, 2, 3)),
]

UNEQUAL_VERSIONS = [
    ((1,), ()),
    ((1,), (0,)),
    ((1, 2), ()),
    ((1, 2), (0,)),
    ((1, 2), (1,)),
    ((1, 2), (0, 0)),
    ((1, 2), (1, 0)),
    ((1, 2, 0), ()),
    ((1, 2, 0), (0,)),
    ((1, 2, 0), (1,)),
    ((1, 2, 0), (0, 0)),
    ((1, 2, 0), (1, 0)),
    ((1, 2, 0), (0, 0, 0)),
    ((1, 2, 3), (1, 2)),
    ((1, 2, 3), (1, 2, 0)),
]


class TestJsonIndentPyVersion(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_JPV_000_get_python_version(self):
        pv.get_python_version()

    def test_JPV_001_get_python_version_has_length(self):
        self.assertEqual(len(pv.get_python_version()), 3)

    def test_JPV_002_get_python_version_value(self):
        sys_ver = (
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro,
        )
        self.assertTupleEqual(pv.get_python_version(), sys_ver)

    def test_JPV_010_pad_version_tuples(self):
        for v1, v2, expected_v1, expected_v2 in [
            ((), (4, 5, 6), [0, 0, 0], [4, 5, 6]),
            ((1,), (4, 5, 6), [1, 0, 0], [4, 5, 6]),
            ((1, 2), (4, 5, 6), [1, 2, 0], [4, 5, 6]),
            ((1, 2, 3), (4, 5, 6), [1, 2, 3], [4, 5, 6]),
            ((1, 2, 3, 4), (4, 5, 6), [1, 2, 3, 4], [4, 5, 6, 0]),
        ]:
            (p1, p2) = pv.pad_version_tuples(v1, v2)
            self.assertListEqual(p1, expected_v1)
            self.assertListEqual(p2, expected_v2)

    def test_JPV_020_compare_eq(self):
        for x, y, expected in [
            (0, 0, True),
            (1, 0, False),
            (0, 1, False),
            (1, 1, True),
            (-1, 1, False),
            (1, -1, False),
            (-1, -1, True),
        ]:
            self.assertEqual(pv.compare_eq(x, y), expected)

    def test_JPV_030_compare_gt(self):
        for x, y, expected in [
            (0, 0, False),
            (1, 0, True),
            (0, 1, False),
            (1, 1, False),
            (-1, 1, False),
            (1, -1, True),
            (-1, -1, False),
        ]:
            self.assertEqual(pv.compare_gt(x, y), expected)

    def test_JPV_040_compare_lt(self):
        for x, y, expected in [
            (0, 0, False),
            (1, 0, False),
            (0, 1, True),
            (1, 1, False),
            (-1, 1, True),
            (1, -1, False),
            (-1, -1, False),
        ]:
            self.assertEqual(pv.compare_lt(x, y), expected)

    def test_JPV_100_version_is_at_least_equal(self):
        for v1, v2 in EQUAL_VERSIONS:
            self.assertTrue(pv.version_is_at_least(v1, v2))
            self.assertTrue(pv.version_is_greater_or_equal(v1, v2))
            self.assertTrue(pv.version_is_at_least(v2, v1))
            self.assertTrue(pv.version_is_greater_or_equal(v2, v1))

    def test_JPV_101_version_is_at_least_unequal(self):
        for v1, v2 in UNEQUAL_VERSIONS:
            self.assertTrue(pv.version_is_at_least(v1, v2))
            self.assertTrue(pv.version_is_greater_or_equal(v1, v2))
            self.assertFalse(pv.version_is_at_least(v2, v1))
            self.assertFalse(pv.version_is_greater_or_equal(v2, v1))

    def test_JPV_110_version_is_at_most_equal(self):
        for v1, v2 in EQUAL_VERSIONS:
            self.assertTrue(pv.version_is_at_most(v1, v2))
            self.assertTrue(pv.version_is_less_or_equal(v1, v2))
            self.assertTrue(pv.version_is_at_most(v2, v1))
            self.assertTrue(pv.version_is_less_or_equal(v2, v1))

    def test_JPV_111_version_is_at_most_unequal(self):
        for v1, v2 in UNEQUAL_VERSIONS:
            self.assertTrue(pv.version_is_at_most(v2, v1))
            self.assertTrue(pv.version_is_less_or_equal(v2, v1))
            self.assertFalse(pv.version_is_at_most(v1, v2))
            self.assertFalse(pv.version_is_less_or_equal(v1, v2))

    def test_JPV_120_version_is_greater_than_equal(self):
        for v1, v2 in EQUAL_VERSIONS:
            self.assertFalse(pv.version_is_greater_than(v1, v2))
            self.assertFalse(pv.version_is_greater_than(v2, v1))

    def test_JPV_121_version_is_greater_than_unequal(self):
        for v1, v2 in UNEQUAL_VERSIONS:
            self.assertTrue(pv.version_is_greater_than(v1, v2))
            self.assertFalse(pv.version_is_greater_than(v2, v1))

    def test_JPV_130_version_is_less_than_equal(self):
        for v1, v2 in EQUAL_VERSIONS:
            self.assertFalse(pv.version_is_less_than(v1, v2))
            self.assertFalse(pv.version_is_less_than(v2, v1))

    def test_JPV_131_version_is_less_than_unequal(self):
        for v1, v2 in UNEQUAL_VERSIONS:
            self.assertTrue(pv.version_is_less_than(v2, v1))
            self.assertFalse(pv.version_is_less_than(v1, v2))

    def test_JPV_200_python_version_is_at_least(self):
        vi = sys.version_info
        for major, minor, micro, expected in [
            (vi.major, vi.minor, vi.micro, True),
            (vi.major + 1, vi.minor, vi.micro, False),
            (vi.major, vi.minor + 1, vi.micro, False),
            (vi.major, vi.minor, vi.micro + 1, False),
            (vi.major - 1, vi.minor, vi.micro, True),
            (vi.major, vi.minor - 1, vi.micro, True),
            (vi.major, vi.minor, vi.micro - 1, True),
        ]:
            result = pv.python_version_is_at_least(major, minor, micro)
            self.assertEqual(result, expected)
            result = pv.python_version_is_at_least(major, minor=minor, micro=micro)
            self.assertEqual(result, expected)

            result = pv.python_version_is_greater_or_equal(major, minor, micro)
            self.assertEqual(result, expected)
            result = pv.python_version_is_greater_or_equal(major, minor=minor, micro=micro)
            self.assertEqual(result, expected)

    def test_JPV_210_python_version_is_at_most(self):
        vi = sys.version_info
        for major, minor, micro, expected in [
            (vi.major, vi.minor, vi.micro, True),
            (vi.major + 1, vi.minor, vi.micro, True),
            (vi.major, vi.minor + 1, vi.micro, True),
            (vi.major, vi.minor, vi.micro + 1, True),
            (vi.major - 1, vi.minor, vi.micro, False),
            (vi.major, vi.minor - 1, vi.micro, False),
            (vi.major, vi.minor, vi.micro - 1, False),
        ]:
            result = pv.python_version_is_at_most(major, minor, micro)
            self.assertEqual(result, expected)
            result = pv.python_version_is_at_most(major, minor=minor, micro=micro)
            self.assertEqual(result, expected)

            result = pv.python_version_is_less_or_equal(major, minor, micro)
            self.assertEqual(result, expected)
            result = pv.python_version_is_less_or_equal(major, minor=minor, micro=micro)
            self.assertEqual(result, expected)

    def test_JPV_220_python_version_is_greater_than(self):
        vi = sys.version_info
        for major, minor, micro, expected in [
            (vi.major, vi.minor, vi.micro, False),
            (vi.major + 1, vi.minor, vi.micro, False),
            (vi.major, vi.minor + 1, vi.micro, False),
            (vi.major, vi.minor, vi.micro + 1, False),
            (vi.major - 1, vi.minor, vi.micro, True),
            (vi.major, vi.minor - 1, vi.micro, True),
            (vi.major, vi.minor, vi.micro - 1, True),
        ]:
            result = pv.python_version_is_greater_than(major, minor, micro)
            self.assertEqual(result, expected)
            result = pv.python_version_is_greater_than(major, minor=minor, micro=micro)
            self.assertEqual(result, expected)

    def test_JPV_230_python_version_is_less_than(self):
        vi = sys.version_info
        for major, minor, micro, expected in [
            (vi.major, vi.minor, vi.micro, False),
            (vi.major + 1, vi.minor, vi.micro, True),
            (vi.major, vi.minor + 1, vi.micro, True),
            (vi.major, vi.minor, vi.micro + 1, True),
            (vi.major - 1, vi.minor, vi.micro, False),
            (vi.major, vi.minor - 1, vi.micro, False),
            (vi.major, vi.minor, vi.micro - 1, False),
        ]:
            result = pv.python_version_is_less_than(major, minor, micro)
            self.assertEqual(result, expected)
            result = pv.python_version_is_less_than(major, minor=minor, micro=micro)
            self.assertEqual(result, expected)
