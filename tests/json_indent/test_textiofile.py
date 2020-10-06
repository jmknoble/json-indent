"""Tests for json_indent.iofile"""

import os
import sys
import tempfile
import unittest

import json_indent.iofile as iof

DUMMY_PATH = "DummyPath"
DUMMY_INPUT_NEWLINE = "DummyInputNewline"
DUMMY_OUTPUT_NEWLINE = "DummyOutputNewline"
DUMMY_MODE = "DummyMode"
DUMMY_PURPOSE = "DummyPurpose"
DUMMY_IO_PROPERTY = "DummyIOProperty"


class TestTextIOFile(unittest.TestCase):
    def setUp(self):
        # Create temporary file for read/write testing
        self.testfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)

    def tearDown(self):
        self.testfile.close()
        os.remove(self.testfile.name)

    def test_TIOF_000_instantiate_empty(self):
        with self.assertRaises(TypeError) as context:  # noqa: F841
            iof.TextIOFile()
        e = context.exception
        message = e.args[0]
        expected_messages = {
            "python-2.7": "__init__() takes exactly 2 arguments (1 given)",
            "python-3.x": "__init__() missing 1 required positional argument: 'path'",
        }
        self.assertIn(message, expected_messages.values())

    def test_TIOF_010_instantiate(self):
        x = iof.TextIOFile(DUMMY_PATH)
        self.assertEqual(x.path, DUMMY_PATH)
        x = iof.TextIOFile(path=DUMMY_PATH)
        self.assertEqual(x.path, DUMMY_PATH)
        self.assertEqual(x.path, DUMMY_PATH)
        x = iof.TextIOFile(DUMMY_PATH, DUMMY_INPUT_NEWLINE)
        x = iof.TextIOFile(DUMMY_PATH, input_newline=DUMMY_INPUT_NEWLINE)
        x = iof.TextIOFile(DUMMY_PATH, DUMMY_INPUT_NEWLINE, DUMMY_OUTPUT_NEWLINE)
        x = iof.TextIOFile(
            DUMMY_PATH,
            input_newline=DUMMY_INPUT_NEWLINE,
            output_newline=DUMMY_OUTPUT_NEWLINE,
        )

    def test_TIOF_100_raise_open_error(self):
        x = iof.TextIOFile(DUMMY_PATH)
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

    def test_TIOF_110_get_io_property(self):
        x = iof.TextIOFile(DUMMY_PATH)
        self.assertIsNone(x._get_io_property("input", "newline"))
        self.assertIsNone(x._get_io_property("output", "newline"))

        x = iof.TextIOFile(
            DUMMY_PATH,
            input_newline=DUMMY_INPUT_NEWLINE,
            output_newline=DUMMY_OUTPUT_NEWLINE,
        )
        for (purpose, mode, newline, stream) in [
            ("input", "rt", DUMMY_INPUT_NEWLINE, sys.stdin),
            ("output", "wt", DUMMY_OUTPUT_NEWLINE, sys.stdout),
        ]:
            self.assertEqual(x._get_io_property(purpose, "target_mode"), mode)
            self.assertEqual(x._get_io_property(purpose, "newline"), newline)
            self.assertIs(x._get_io_property(purpose, "stdio_stream"), stream)

        with self.assertRaises(ValueError) as context:  # noqa: F841
            x._get_io_property(DUMMY_PURPOSE, "target_mode")
        with self.assertRaises(ValueError) as context:  # noqa: F841
            x._get_io_property(DUMMY_PURPOSE, "newline")
        with self.assertRaises(ValueError) as context:  # noqa: F841
            x._get_io_property(DUMMY_PURPOSE, "stdio_stream")
        with self.assertRaises(ValueError) as context:  # noqa: F841
            x._get_io_property(DUMMY_PURPOSE, DUMMY_IO_PROPERTY)

        with self.assertRaises(KeyError) as context:  # noqa: F841
            x._get_io_property("input", DUMMY_IO_PROPERTY)
        with self.assertRaises(KeyError) as context:  # noqa: F841
            x._get_io_property("output", DUMMY_IO_PROPERTY)

    def test_TIOF_120_close(self):
        for (path, openfile, should_be_closed) in [
            (self.testfile.name, open(self.testfile.name), True),
            ("-", sys.stdin, False),
            ("-", sys.stdout, False),
        ]:
            x = iof.TextIOFile(path)
            x.mode = DUMMY_MODE
            x.file = openfile
            x.close()
            self.assertIs(x.mode, None)
            self.assertIs(x.file, None)
            self.assertTrue(
                openfile.closed if should_be_closed else not openfile.closed
            )

    def test_TIOF_130_open_for_purpose(self):
        x = iof.TextIOFile(self.testfile.name)

        for (purpose, expected_mode) in [("input", "rt"), ("output", "wt")]:
            f = x._open_for_purpose(purpose)
            self.assertEqual(x.mode, expected_mode)
            self.assertIs(f, x.file)

            # Repeating should give same results even if open
            f = x._open_for_purpose(purpose)
            self.assertEqual(x.mode, expected_mode)
            self.assertIs(f, x.file)

            x.close()

    def test_TIOF_140_open_stdio_streams(self):
        x = iof.TextIOFile("-")
        for (purpose, expected_mode, expected_stream) in [
            ("input", "rt", sys.stdin),
            ("output", "wt", sys.stdout),
        ]:
            f = x._open_for_purpose(purpose)
            self.assertEqual(x.mode, expected_mode)
            self.assertEqual(f.fileno(), expected_stream.fileno())
            x.close()

    def test_TIOF_150_open_for_input(self):
        x = iof.TextIOFile(self.testfile.name)

        f = x.open_for_input()
        self.assertEqual(x.mode, "rt")
        self.assertIs(f, x.file)

        # Repeating should give same results even if open
        f = x.open_for_input()
        self.assertEqual(x.mode, "rt")
        self.assertIs(f, x.file)

        x.close()

    def test_TIOF_160_open_for_output(self):
        x = iof.TextIOFile(self.testfile.name)

        f = x.open_for_output()
        self.assertEqual(x.mode, "wt")
        self.assertIs(f, x.file)

        # Repeating should give same results even if open
        f = x.open_for_output()
        self.assertEqual(x.mode, "wt")
        self.assertIs(f, x.file)

        x.close()

    def test_TIOF_170_reopen(self):
        x = iof.TextIOFile(self.testfile.name)

        x.open_for_input()
        with self.assertRaises(iof.IOFileOpenError) as context:  # noqa: F841
            x.open_for_output()
        x.close()

        x.open_for_output()
        with self.assertRaises(iof.IOFileOpenError) as context:  # noqa: F841
            x.open_for_input()
        x.close()
