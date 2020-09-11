"""
Provide main functionality for `json_indent`:py:mod: parser/indenter/formatter.
"""

from __future__ import absolute_import

import argparse
import collections
import json
import logging
import os.path
import sys

from json_indent import get_version
from json_indent.iofile import IOFile

__all__ = ["cli", "dump_json", "load_json", "main"]

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class JsonParseError(ValueError):
    def __init__(self, filename, exception):
        self.filename = filename
        self.exception = exception
        self.msg = "{filename}: {exception}".format(filename=filename, exception=exception)
        super(JsonParseError, self).__init__(self.msg)


def _pop_with_default(a_dict, key, default=None):
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


def load_json(infile, **kwargs):
    """
    Read JSON data from a file into a (possibly ordered) dictionary.

    :Args:
        infile
            Open file to load JSON data from

        kwargs
            Keyword arguments, most of which are passed unchanged to
            `json.load()`:py:func: (but see below).

    :Keyword Args:
        sort_keys
            Whether the caller intends to sort keys when writing JSON data
            (default if not present: `False`).

        unordered
            Whether the resulting dictionary need not (`True`) or must
            (`False`) preserve the order of keys from the JSON data (default:
            `False`, i.e., preserve key order).

    :Returns:
        A dictionary-ish containing the JSON data read from `infile`.
    """
    sort_keys = _pop_with_default(kwargs, "sort_keys", False)
    unordered = _pop_with_default(kwargs, "unordered", False)
    if sort_keys or not unordered:
        kwargs["object_pairs_hook"] = collections.OrderedDict
    try:
        json_dict = json.load(fp=infile, **kwargs)
    except json.JSONDecodeError as e:
        raise JsonParseError(infile.name, e)
    return json_dict


def dump_json(json_dict, outfile, **kwargs):
    """
    Write formatted JSON data to a file from a dictionary.

    We do this according to parameters in keyword arguments, and we add a final
    trailing newline.

    :Args:
        json_dict
            Dictionary-ish containing data to write

        outfile
            Open file to write JSON data to

        kwargs
            Keyword arguments, most of which are passed to
            `json.dump()`:py:func: (but see below).

    :Keyword Args:
        fp
            If this keyword argument is supplied, it is ignored, as the file to
            write to is required as `outfile`.

    :Returns:
        Nothing
    """
    if "fp" in kwargs:
        kwargs.pop("fp")
    json.dump(json_dict, fp=outfile, **kwargs)
    outfile.write("\n")


def _setup_argparser():
    default_indent = 2
    default_inplace = False
    default_sort = False
    default_compact = False
    default_debug = False

    argp = argparse.ArgumentParser(
        add_help=True, description="Parse/indent/pretty-print JSON data."
    )
    argp.add_argument(
        "input_filenames",
        nargs="*",
        action="store",
        default=[],
        metavar="INPUTFILE",
        help="input file[s], or '-' for stdin (default: stdin)",
    )
    argp.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output_filename",
        default=None,
        metavar="OUTPUTFILE",
        help=(
            "output file, or '-' for stdout (default: stdout); "
            "conflicts with '--inplace'"
        ),
    )
    argp.add_argument(
        "-I",
        "--inplace",
        "--in-place",
        action="store_true",
        default=default_inplace,
        help="write changes to input file in place (default: {})".format(
            default_inplace
        ),
    )
    argp.add_argument(
        "-c",
        "--compact",
        action="store_true",
        default=default_compact,
        help="compact JSON onto one line with minimal whitespace (default: {})".format(
            default_compact
        ),
    )
    argp.add_argument(
        "-n",
        "--indent",
        action="store",
        default=default_indent,
        help="number of spaces or string for indenting (default: {})".format(
            default_indent
        ),
    )
    argp.add_argument(
        "-s",
        "--sort-keys",
        action="store_true",
        default=default_sort,
        help="sort output alphabetically by key (default: same order as read)",
    )
    argp.add_argument(
        "--debug",
        action="store_true",
        default=default_debug,
        help="turn on debug messages (default: {})".format(default_debug),
    )
    argp.add_argument("-V", "--version", action="version", version=get_version())
    return argp


def _normalize_path(path):
    """Fully regularize a given filesystem path."""
    if path != "-":
        path = os.path.normcase(os.path.normpath(os.path.realpath(path)))
    return path


def _check_input_and_output_filenames(cli_args):
    """Check args found by `argparse.ArgumentParser`:py:class: and regularize."""
    if len(cli_args.input_filenames) == 0:
        cli_args.input_filenames.append("-")  # default to stdin

    if not cli_args.inplace:
        if cli_args.output_filename is None:
            cli_args.output_filename = "-"  # default to stdout
        if len(cli_args.input_filenames) > 1:
            raise RuntimeError(
                "to process more than one input file at a time, use '--inplace'"
            )
        cli_args.output_filename = _normalize_path(cli_args.output_filename)
        cli_args.input_filenames[0] = _normalize_path(cli_args.input_filenames[0])
        if (
            cli_args.input_filenames[0] != "-"
            and cli_args.input_filenames[0] == cli_args.output_filename
        ):
            raise RuntimeError(
                "input file and output file are the same; "
                "use '--inplace' to modify files in place"
            )
    else:
        if cli_args.output_filename is not None:
            raise RuntimeError("output files do not make sense with '--inplace'")

        for i in range(len(cli_args.input_filenames)):
            if cli_args.input_filenames[i] == "-":
                raise RuntimeError(
                    "reading from stdin does not make sense with '--inplace'"
                )
            cli_args.input_filenames[i] = _normalize_path(cli_args.input_filenames[i])


def _check_program_args(program_args):
    """Check arguments supplied to main program and add defaults."""
    if program_args:
        program = None
        program_args = list(program_args)
    else:
        program = sys.argv[0]
        program_args = sys.argv[1:]

    if "--debug" in program_args:
        logger.setLevel(logging.DEBUG)
        logger.debug("Called with: {args}".format(args=[program] + program_args))

    return program_args


def cli(*program_args):
    """Process command-line."""
    program_args = _check_program_args(program_args)
    argparser = _setup_argparser()
    cli_args = argparser.parse_args(program_args)
    _check_input_and_output_filenames(cli_args)

    load_kwargs = {}
    dump_kwargs = {}

    if cli_args.compact:
        item_separator = ","
        key_separator = ":"
        indent = None
    else:
        item_separator = ","
        key_separator = ": "
        try:
            indent = int(cli_args.indent)
        except ValueError:
            # invalid literal for int() with base 10
            indent = cli_args.indent

    load_kwargs["sort_keys"] = cli_args.sort_keys

    dump_kwargs["indent"] = indent
    dump_kwargs["separators"] = (item_separator, key_separator)
    dump_kwargs["sort_keys"] = cli_args.sort_keys

    for input_filename in cli_args.input_filenames:
        input_iofile = IOFile(input_filename)
        output_iofile = (
            input_iofile if cli_args.inplace else IOFile(cli_args.output_filename)
        )

        input_iofile.open_for_input()

        try:
            data = load_json(input_iofile.file, **load_kwargs)
        except ValueError as e:
            raise SystemExit(e)

        input_iofile.close()

        output_iofile.open_for_output()
        dump_json(data, output_iofile.file, **dump_kwargs)
        output_iofile.close()


def main(*program_args):
    """Provide main functionality."""
    cli(*program_args)
    sys.exit(0)


if __name__ == "__main__":
    main()
