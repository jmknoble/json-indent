"""Tests for json_indent.iofile"""

import os
import sys
import tempfile
import unittest

import json_indent.iofile as iof

DUMMY_PATH = "DummyPath"
DUMMY_MODE = "DummyMode"
DUMMY_PURPOSE = "DummyPurpose"
DUMMY_IO_PROPERTY = "DummyIOProperty"


class TestIOFile(unittest.TestCase):
    def setUp(self):
        # Create temporary file for read/write testing
        self.testfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)

    def tearDown(self):
        self.testfile.close()
        os.remove(self.testfile.name)

    def test_IOF_000_instantiate_empty(self):
        with self.assertRaises(TypeError) as context:  # noqa: F841
            iof.IOFile()
        e = context.exception
        message = e.args[0]
        expected_messages = {
            "python-2.7": "__init__() takes exactly 2 arguments (1 given)",
            "python-3.x": "__init__() missing 1 required positional argument: 'path'",
        }
        self.assertIn(message, expected_messages.values())

    def test_IOF_010_instantiate(self):
        x = iof.IOFile(DUMMY_PATH)
        self.assertEqual(x.path, DUMMY_PATH)
        x = iof.IOFile(path=DUMMY_PATH)
        self.assertEqual(x.path, DUMMY_PATH)

    def test_IOF_100_raise_open_error(self):
        x = iof.IOFile(DUMMY_PATH)
        x.mode = DUMMY_MODE
        with self.assertRaises(iof.IOFileOpenError) as context:  # noqa: F841
            x._raise_open_error(DUMMY_PURPOSE)
        e = context.exception
        self.assertIsInstance(e, iof.IOFileOpenError)
        self.assertEqual(e.path, DUMMY_PATH)
        self.assertEqual(e.mode, DUMMY_MODE)
        self.assertEqual(e.purpose, DUMMY_PURPOSE)
        message = e.args[0]
        expected_message = "{path}: error opening for {purpose} (mode: {mode})".format(
            path=DUMMY_PATH, mode=DUMMY_MODE, purpose=DUMMY_PURPOSE
        )
        self.assertEqual(message, expected_message)

    def test_IOF_110_get_io_property(self):
        x = iof.IOFile(DUMMY_PATH)
        for (purpose, mode, stream) in [
            ("input", "r", sys.stdin),
            ("output", "w", sys.stdout),
        ]:
            self.assertEqual(x._get_io_property(purpose, "target_mode"), mode)
            self.assertIs(x._get_io_property(purpose, "stdio_stream"), stream)

        with self.assertRaises(ValueError) as context:  # noqa: F841
            x._get_io_property(DUMMY_PURPOSE, "target_mode")
        with self.assertRaises(ValueError) as context:  # noqa: F841
            x._get_io_property(DUMMY_PURPOSE, "stdio_stream")
        with self.assertRaises(ValueError) as context:  # noqa: F841
            x._get_io_property(DUMMY_PURPOSE, DUMMY_IO_PROPERTY)

        with self.assertRaises(KeyError) as context:  # noqa: F841
            x._get_io_property("input", DUMMY_IO_PROPERTY)
        with self.assertRaises(KeyError) as context:  # noqa: F841
            x._get_io_property("output", DUMMY_IO_PROPERTY)

    def test_IOF_120_close(self):
        for (path, openfile, should_be_closed) in [
            (self.testfile.name, open(self.testfile.name), True),
            ("-", sys.stdin, False),
            ("-", sys.stdout, False),
        ]:
            x = iof.IOFile(path)
            x.mode = DUMMY_MODE
            x.file = openfile
            x.close()
            self.assertIs(x.mode, None)
            self.assertIs(x.file, None)
            self.assertTrue(
                openfile.closed if should_be_closed else not openfile.closed
            )

    def test_IOF_130_open_for_purpose(self):
        x = iof.IOFile(self.testfile.name)

        for (purpose, expected_mode) in [("input", "r"), ("output", "w")]:
            f = x._open_for_purpose(purpose)
            self.assertEqual(x.mode, expected_mode)
            self.assertIs(f, x.file)

            # Repeating should give same results even if open
            f = x._open_for_purpose(purpose)
            self.assertEqual(x.mode, expected_mode)
            self.assertIs(f, x.file)

            x.close()

    def test_IOF_140_open_stdio_streams(self):
        x = iof.IOFile("-")
        for (purpose, expected_mode, expected_stream) in [
            ("input", "r", sys.stdin),
            ("output", "w", sys.stdout),
        ]:
            f = x._open_for_purpose(purpose)
            self.assertEqual(x.mode, expected_mode)
            self.assertIs(f, expected_stream)
            x.close()

    def test_IOF_150_open_for_input(self):
        x = iof.IOFile(self.testfile.name)

        f = x.open_for_input()
        self.assertEqual(x.mode, "r")
        self.assertIs(f, x.file)

        # Repeating should give same results even if open
        f = x.open_for_input()
        self.assertEqual(x.mode, "r")
        self.assertIs(f, x.file)

        x.close()

    def test_IOF_160_open_for_output(self):
        x = iof.IOFile(self.testfile.name)

        f = x.open_for_output()
        self.assertEqual(x.mode, "w")
        self.assertIs(f, x.file)

        # Repeating should give same results even if open
        f = x.open_for_output()
        self.assertEqual(x.mode, "w")
        self.assertIs(f, x.file)

        x.close()

    def test_IOF_170_reopen(self):
        x = iof.IOFile(self.testfile.name)

        x.open_for_input()
        with self.assertRaises(iof.IOFileOpenError) as context:  # noqa: F841
            x.open_for_output()
        x.close()

        x.open_for_output()
        with self.assertRaises(iof.IOFileOpenError) as context:  # noqa: F841
            x.open_for_input()
        x.close()
