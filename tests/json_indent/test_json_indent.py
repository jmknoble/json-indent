"""Tests for json_ildent.json_indent"""

import argparse
import collections
import os
import os.path
import sys
import tempfile
import unittest

import json_indent.json_indent as ji

DUMMY_KEY_1 = "DummyKey1"
DUMMY_KEY_2 = "DummyKey2"
DUMMY_VALUE_1 = "DummyValue1"
DUMMY_VALUE_2 = "DummyValue2"
DUMMY_DICT = {DUMMY_KEY_1: DUMMY_VALUE_1}

DUMMY_JSON_DATA_DICT = {DUMMY_KEY_2: DUMMY_VALUE_2, DUMMY_KEY_1: [DUMMY_VALUE_1]}

DUMMY_JSON_DATA_ORDERED_DICT = collections.OrderedDict()
DUMMY_JSON_DATA_ORDERED_DICT[DUMMY_KEY_2] = DUMMY_VALUE_2
DUMMY_JSON_DATA_ORDERED_DICT[DUMMY_KEY_1] = [DUMMY_VALUE_1]

DUMMY_JSON_DATA_UNFORMATTED = """{{
"{key2}": "{value2}", "{key1}": ["{value1}"]
}}
""".format(
    key1=DUMMY_KEY_1, key2=DUMMY_KEY_2, value1=DUMMY_VALUE_1, value2=DUMMY_VALUE_2
)

DUMMY_JSON_DATA_FORMATTED = """{{
    "{key2}": "{value2}",
    "{key1}": [
        "{value1}"
    ]
}}
""".format(
    key1=DUMMY_KEY_1, key2=DUMMY_KEY_2, value1=DUMMY_VALUE_1, value2=DUMMY_VALUE_2
)

DUMMY_JSON_DATA_SORTED = """{{
    "{key1}": [
        "{value1}"
    ],
    "{key2}": "{value2}"
}}
""".format(
    key1=DUMMY_KEY_1, key2=DUMMY_KEY_2, value1=DUMMY_VALUE_1, value2=DUMMY_VALUE_2
)

DUMMY_JSON_DATA_COMPACT = '{{"{key2}":"{value2}","{key1}":["{value1}"]}}\n'.format(
    key1=DUMMY_KEY_1, key2=DUMMY_KEY_2, value1=DUMMY_VALUE_1, value2=DUMMY_VALUE_2
)

PLAIN_SEPARATORS = (",", ": ")
COMPACT_SEPARATORS = (",", ":")

PLAIN_KWARGS = {"indent": 4, "separators": PLAIN_SEPARATORS}
INDENT_KWARGS = {"indent": " " * 4, "separators": PLAIN_SEPARATORS}
SORTED_KWARGS = {"sort_keys": True, "indent": 4, "separators": PLAIN_SEPARATORS}
COMPACT_KWARGS = {"indent": None, "separators": COMPACT_SEPARATORS}

DUMMY_PROGRAM_NAME = "DummyProgramName"
DUMMY_PROGRAM_ARGS = [DUMMY_VALUE_1, DUMMY_VALUE_2]

CLI_OPTIONS = {
    # dest: [option_strings]
    "help": ["-h", "--help"],
    "output_filename": ["-o", "--output"],
    "inplace": ["-I", "--inplace", "--in-place"],
    "compact": ["-c", "--compact"],
    "indent": ["-n", "--indent"],
    "sort_keys": ["-s", "--sort-keys"],
    "debug": ["--debug"],
    "version": ["-V", "--version"],
}

CLI_ARGUMENTS = {
    # dest: nargs
    "input_filenames": "*"
}

DUMMY_PATH_1 = "DummyPath1"
DUMMY_PATH_2 = "DummyPath2"
DUMMY_PATHS = {DUMMY_PATH_1: None, "one/two/three": None, "/a/b/c": None, "-": None}
for path in DUMMY_PATHS:
    normalized_path = (
        "-"
        if path == "-"
        else os.path.normcase(os.path.normpath(os.path.realpath(path)))
    )
    DUMMY_PATHS[path] = normalized_path

ARGS_DEFAULT = []
ARGS_PLAIN = ["--indent", "4"]
ARGS_INDENT = ["--indent", " " * 4]
ARGS_SORTED = ["--indent", "4", "--sort-keys"]
ARGS_COMPACT = ["--compact"]

ARGS_DEBUG = ["--debug"] if "DEBUG" in os.environ else []


def deep_convert_to_plain_dict(an_odict):
    """
    Recursively convert `an_odict` and any of its dictionary subelements from
    `collections.OrderedDict`:py:class: to plain `dict`:py:class:

    .. note:: This is naive, in that it will not properly handle dictionaries
        with recursive object references.

    :Args:
        an_odict
            a (presumably) `collections.OrderedDict`:py:class: to convert

    :Returns:
        an "unordered" (i.e., plain) `dict`:py:class: with all ordered
        dictionaries converted to `dict`:py:class:
    """
    a_dict = {}
    for (key, value) in an_odict.items():
        if type(value) is collections.OrderedDict:
            a_dict[key] = deep_convert_to_plain_dict(value)
        else:
            a_dict[key] = value
    return a_dict


class TestJsonIndent(unittest.TestCase):
    def setUp(self):
        # Create temporary file for read/write testing
        self.infile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.outfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)

    def tearDown(self):
        for f in (self.infile, self.outfile):
            f.close()
            os.remove(f.name)

    def dummy_cli_args(self):
        return argparse.Namespace(
            input_filenames=[],
            output_filename=None,
            inplace=False,
            compact=False,
            indent=2,
            sort_keys=False,
            debug=False,
        )

    def assertOrderedDictEqual(self, odict1, odict2, strict=True):
        """
        Assert that `odict1` and `odict2` are "equal" from the perspective of a
        dictionary, but with an additional constraint of being ordered
        dictionaries as well.

        :Args:
            odict1
                a `collections.OrderedDict`:py:class: object

            odict2
                another `collections.OrderedDict`:py:class: object to compare with
                `odict1`

            strict
                (OPTIONAL) If `True`-ish, assert the order of the keys in
                `odict1` is equivalent to that of `odict2`.
        """
        self.assertIs(type(odict1), collections.OrderedDict)
        self.assertIs(type(odict2), collections.OrderedDict)
        if strict:
            self.assertListEqual(list(odict1.keys()), list(odict2.keys()))
        dict1 = deep_convert_to_plain_dict(odict1)
        dict2 = deep_convert_to_plain_dict(odict2)
        self.assertDictEqual(dict1, dict2)

    def assertDictishEqual(self, dictish1, dictish2, ordered, strict=True):
        """
        Assert that `dictish1` and `dictish2` are "equal" from the perspective
        of a dictionary, with a possible additional constraint on being ordered
        dictionaries.

        :Args:
            dictish1
                a `dict`-ish object

            dictish2
                another `dict`-ish object to compare with `dictish1`

            ordered
                if `True`-ish, compare as ordered dictionaries

            strict
                (OPTIONAL) If `True`-ish, and `ordered` is also `True`-ish,
                assert the order of the keys in `odict1` is equivalent to that
                of `odict2`.
        """
        if ordered:
            self.assertOrderedDictEqual(dictish1, dictish2, strict)
        else:
            self.assertDictEqual(dictish1, dictish2)

    def test_JSI_000_pop_with_default(self):
        a_dict = DUMMY_DICT.copy()
        value = ji._pop_with_default(a_dict, DUMMY_KEY_1)
        self.assertEqual(value, DUMMY_VALUE_1)
        self.assertNotIn(DUMMY_KEY_1, a_dict)
        self.assertEqual(len(a_dict), 0)

        a_dict = DUMMY_DICT.copy()
        value = ji._pop_with_default(a_dict, DUMMY_KEY_2)
        self.assertIs(value, None)
        self.assertIn(DUMMY_KEY_1, a_dict)
        self.assertEqual(len(a_dict), 1)

        a_dict = DUMMY_DICT.copy()
        value = ji._pop_with_default(a_dict, DUMMY_KEY_2, DUMMY_VALUE_2)
        self.assertEqual(value, DUMMY_VALUE_2)
        self.assertIn(DUMMY_KEY_1, a_dict)
        self.assertEqual(len(a_dict), 1)

        a_dict = DUMMY_DICT.copy()
        value = ji._pop_with_default(a_dict, key=DUMMY_KEY_2, default=DUMMY_VALUE_2)
        self.assertEqual(value, DUMMY_VALUE_2)
        self.assertIn(DUMMY_KEY_1, a_dict)
        self.assertEqual(len(a_dict), 1)

    def test_JSI_100_load_json(self):
        with open(self.infile.name, "w") as f:
            f.write(DUMMY_JSON_DATA_UNFORMATTED)

        with open(self.infile.name, "r") as f:
            json_dict = ji.load_json(f)
            self.assertDictishEqual(
                json_dict, DUMMY_JSON_DATA_ORDERED_DICT, ordered=True
            )

        for (ordered, expected_dict) in [
            (True, DUMMY_JSON_DATA_ORDERED_DICT),
            (False, DUMMY_JSON_DATA_DICT),
        ]:
            with open(self.infile.name, "r") as f:
                json_dict = ji.load_json(f, unordered=not ordered)
                self.assertDictishEqual(json_dict, expected_dict, ordered=ordered)
            with open(self.infile.name, "r") as f:
                json_dict = ji.load_json(f, sort_keys=not ordered)
                self.assertDictishEqual(json_dict, expected_dict, ordered=ordered)

    def test_JSI_110_dump_json(self):
        with open(self.outfile.name, "w") as f:
            # Ensure file exists and is empty
            pass

        for (kwargs, json_dict, expected_json_data) in [
            (PLAIN_KWARGS, DUMMY_JSON_DATA_ORDERED_DICT, DUMMY_JSON_DATA_FORMATTED),
            (INDENT_KWARGS, DUMMY_JSON_DATA_ORDERED_DICT, DUMMY_JSON_DATA_FORMATTED),
            (SORTED_KWARGS, DUMMY_JSON_DATA_DICT, DUMMY_JSON_DATA_SORTED),
            (COMPACT_KWARGS, DUMMY_JSON_DATA_ORDERED_DICT, DUMMY_JSON_DATA_COMPACT),
        ]:
            with open(self.outfile.name, "w") as f:
                ji.dump_json(json_dict, f, **kwargs)
            with open(self.outfile.name, "r") as f:
                self.assertEqual(f.read(), expected_json_data)

    def test_JSI_200_check_program_args(self):
        program_args = ji._check_program_args(DUMMY_PROGRAM_ARGS)
        self.assertListEqual(program_args, DUMMY_PROGRAM_ARGS)

        sys.argv = [DUMMY_PROGRAM_NAME] + DUMMY_PROGRAM_ARGS
        program_args = ji._check_program_args(tuple())
        self.assertListEqual(program_args, DUMMY_PROGRAM_ARGS)

    def test_JSI_210_setup_argparser(self):
        argparser = ji._setup_argparser()
        self.assertIsInstance(argparser, argparse.ArgumentParser)
        self.assertGreater(len(argparser.description), 0)
        for action in argparser._actions:
            self.assertTrue(action.dest in CLI_OPTIONS or action.dest in CLI_ARGUMENTS)
            if action.dest in CLI_OPTIONS:
                self.assertSetEqual(
                    set(action.option_strings), set(CLI_OPTIONS[action.dest])
                )
            else:
                self.assertEqual(action.nargs, CLI_ARGUMENTS[action.dest])

    def test_JSI_220_normalize_path(self):
        for (path, expected_path) in DUMMY_PATHS.items():
            test_path = ji._normalize_path(path)
            self.assertEqual(test_path, expected_path)

    def test_JSI_230_check_io_filenames_with_defaults(self):
        cli_args = self.dummy_cli_args()
        ji._check_input_and_output_filenames(cli_args)
        self.assertListEqual(cli_args.input_filenames, ["-"])
        self.assertEqual(cli_args.output_filename, "-")

    def test_JSI_231_check_io_filenames_with_stdio(self):
        cli_args = self.dummy_cli_args()
        cli_args.input_filenames = ["-"]
        cli_args.output_filename = "-"
        ji._check_input_and_output_filenames(cli_args)
        self.assertListEqual(cli_args.input_filenames, ["-"])
        self.assertEqual(cli_args.output_filename, "-")

    def test_JSI_232_check_io_filenames_with_input_filename(self):
        cli_args = self.dummy_cli_args()
        cli_args.input_filenames = [DUMMY_PATH_1]
        ji._check_input_and_output_filenames(cli_args)
        self.assertListEqual(cli_args.input_filenames, [DUMMY_PATH_1])
        self.assertEqual(cli_args.output_filename, "-")

    def test_JSI_233_check_io_filenames_with_multiple_input_filenames(self):
        cli_args = self.dummy_cli_args()
        cli_args.input_filenames = [DUMMY_PATH_1, DUMMY_PATH_2]
        with self.assertRaises(RuntimeError) as context:  # noqa: F841
            ji._check_input_and_output_filenames(cli_args)
        errmsg = context.exception.args[0]
        self.assertEqual(
            errmsg, "to process more than one input file at a time, use '--inplace'"
        )

    def test_JSI_234_check_io_filenames_with_same_filenames(self):
        cli_args = self.dummy_cli_args()
        cli_args.input_filenames = [DUMMY_PATH_1]
        cli_args.output_filename = DUMMY_PATH_1
        with self.assertRaises(RuntimeError) as context:  # noqa: F841
            ji._check_input_and_output_filenames(cli_args)
        errmsg = context.exception.args[0]
        self.assertTrue(errmsg.startswith("input file and output file are the same"))

    def test_JSI_235_check_io_filenames_with_inplace(self):
        cli_args = self.dummy_cli_args()
        cli_args.input_filenames = [DUMMY_PATH_1]
        cli_args.inplace = True
        ji._check_input_and_output_filenames(cli_args)

    def test_JSI_236_check_io_filenames_with_inplace_and_multiple_filenames(self):
        cli_args = self.dummy_cli_args()
        cli_args.input_filenames = [DUMMY_PATH_1, DUMMY_PATH_2]
        cli_args.inplace = True
        ji._check_input_and_output_filenames(cli_args)

    def test_JSI_237_check_io_filenames_with_inplace_and_output_filename(self):
        for output_filename in [DUMMY_PATH_2, "-"]:
            cli_args = self.dummy_cli_args()
            cli_args.input_filenames = [DUMMY_PATH_1]
            cli_args.output_filename = output_filename
            cli_args.inplace = True
            with self.assertRaises(RuntimeError) as context:  # noqa: F841
                ji._check_input_and_output_filenames(cli_args)
            errmsg = context.exception.args[0]
            self.assertEqual(errmsg, "output files do not make sense with '--inplace'")

    def test_JSI_238_check_io_filenames_with_inplace_and_stdio(self):
        cli_args = self.dummy_cli_args()
        cli_args.input_filenames = ["-"]
        cli_args.inplace = True
        with self.assertRaises(RuntimeError) as context:  # noqa: F841
            ji._check_input_and_output_filenames(cli_args)
        errmsg = context.exception.args[0]
        self.assertEqual(
            errmsg, "reading from stdin does not make sense with '--inplace'"
        )

    def test_JSI_300_cli(self):
        for (test_args, expected_json_data) in [
            (ARGS_PLAIN, DUMMY_JSON_DATA_FORMATTED),
            (ARGS_INDENT, DUMMY_JSON_DATA_FORMATTED),
            (ARGS_SORTED, DUMMY_JSON_DATA_SORTED),
            (ARGS_COMPACT, DUMMY_JSON_DATA_COMPACT),
        ]:
            with open(self.infile.name, "w") as f:
                f.write(DUMMY_JSON_DATA_UNFORMATTED)
            args = (
                test_args
                + ARGS_DEBUG
                + ["--output", self.outfile.name, self.infile.name]
            )
            ji.cli(*args)
            with open(self.outfile.name, "r") as f:
                self.assertEqual(f.read(), expected_json_data)

    def test_JSI_301_cli_inplace(self):
        for (test_args, expected_json_data) in [
            (ARGS_PLAIN, DUMMY_JSON_DATA_FORMATTED),
            (ARGS_INDENT, DUMMY_JSON_DATA_FORMATTED),
            (ARGS_SORTED, DUMMY_JSON_DATA_SORTED),
            (ARGS_COMPACT, DUMMY_JSON_DATA_COMPACT),
        ]:
            with open(self.infile.name, "w") as f:
                f.write(DUMMY_JSON_DATA_UNFORMATTED)
            args = test_args + ARGS_DEBUG + ["--inplace", self.infile.name]
            ji.cli(*args)
            with open(self.infile.name, "r") as f:
                self.assertEqual(f.read(), expected_json_data)

    def test_JSI_310_cli_version(self):
        with self.assertRaises(SystemExit) as context:  # noqa: F841
            ji.cli(*["--version"])

    def test_JSI_320_cli_version_via_main(self):
        with self.assertRaises(SystemExit) as context:  # noqa: F841
            ji.main(*["--version"])
