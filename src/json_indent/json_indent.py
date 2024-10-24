"""
Provide main functionality for `json_indent`:py:mod: parser/indenter/formatter.
"""

from __future__ import absolute_import, print_function

import argparse
import collections
import difflib
import json
import logging
import os.path
import sys

import argcomplete

from json_indent import completion, get_version
from json_indent.iofile import TextIOFile
from json_indent.util import is_string, pop_with_default, to_unicode

__all__ = [
    "cli",
    "dump_json",
    "dump_json_file",
    "dump_json_text",
    "load_json",
    "load_json_file",
    "load_json_text",
    "main",
]

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

STATUS_OK = 0
STATUS_SYNTAX_ERROR = 1
STATUS_CHANGED = 99

JSON_TEXT_DEFAULT_FILENAME = "<text>"

DIFF_CONTEXT_LINES = 3

NEWLINE_FORMAT_LINUX = "linux"
NEWLINE_FORMAT_MICROSOFT = "microsoft"
NEWLINE_FORMAT_NATIVE = "native"

NEWLINE_FORMATS = [
    NEWLINE_FORMAT_LINUX,
    NEWLINE_FORMAT_MICROSOFT,
    NEWLINE_FORMAT_NATIVE,
]

NEWLINE_FORMAT_ALIAS_DOS = "dos"
NEWLINE_FORMAT_ALIAS_MACOS = "macos"
NEWLINE_FORMAT_ALIAS_MSFT = "msft"
NEWLINE_FORMAT_ALIAS_UNIX = "unix"
NEWLINE_FORMAT_ALIAS_WINDOWS = "windows"

NEWLINE_FORMAT_ALIASES = {
    NEWLINE_FORMAT_ALIAS_DOS: NEWLINE_FORMAT_MICROSOFT,
    NEWLINE_FORMAT_ALIAS_MACOS: NEWLINE_FORMAT_LINUX,
    NEWLINE_FORMAT_ALIAS_MSFT: NEWLINE_FORMAT_MICROSOFT,
    NEWLINE_FORMAT_ALIAS_UNIX: NEWLINE_FORMAT_LINUX,
    NEWLINE_FORMAT_ALIAS_WINDOWS: NEWLINE_FORMAT_MICROSOFT,
}

ALL_NEWLINE_FORMATS = sorted(NEWLINE_FORMATS + list(NEWLINE_FORMAT_ALIASES.keys()))

NEWLINE_VALUES = {
    NEWLINE_FORMAT_LINUX: "\n",
    NEWLINE_FORMAT_MICROSOFT: "\r\n",
    NEWLINE_FORMAT_NATIVE: None,
}


class JsonParseError(ValueError):
    def __init__(self, filename, exception):
        self.filename = filename
        self.exception = exception
        self.msg = "{filename}: {exception}".format(
            filename=filename, exception=exception
        )
        super(JsonParseError, self).__init__(self.msg)


def load_json_text(text, filename=None, **kwargs):
    """
    Parse and deserialize JSON data from a string.

    :Args:
        text
            Raw JSON text

        filename
            (optional) Input filename associated with the JSON text, if any

        kwargs
            (optional) Keyword arguments, most of which are passed unchanged to
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
        The JSON data parsed from `text`.
    """
    filename = JSON_TEXT_DEFAULT_FILENAME if filename is None else filename
    sort_keys = pop_with_default(kwargs, "sort_keys", False)
    unordered = pop_with_default(kwargs, "unordered", False)
    if sort_keys or not unordered:
        kwargs["object_pairs_hook"] = collections.OrderedDict
    try:
        data = json.loads(text, **kwargs)
    except json.JSONDecodeError as e:
        raise JsonParseError(filename, e)
    return data


def load_json_file(infile, **kwargs):
    """
    Parse and deserialize JSON data from a file.

    :Args:
        infile
            Open file-ish to load JSON data from

        kwargs
            Keyword arguments, passed unchanged to
            `~json_indent.load_json_text()`:py:func:

    :Returns:
        A tuple::

            (json_data, json_text)

        where `json_text` is the original text read from `infile`, and
        `json_data` is the deserialized result.
    """
    text = infile.read()
    text = to_unicode(text)
    data = load_json_text(text, filename=infile.name, **kwargs)
    return (data, text)


def load_json(thing, with_text=False, **kwargs):
    """
    Parse and deserialize JSON data from either a file or a string.

    :Args:
        thing
            Either a (Unicode) string or an open file-ish to load JSON data from

        with_text
            See *Returns* below.

        kwargs
            Keyword arguments, passed unchanged to
            `~json_indent.load_json_text()`:py:func:

    :Returns:
        If `with_text` is `True`-ish, return a tuple::

            (json_data, json_text)

        where `json_text` is the original text read from `infile`, and
        `json_data` is the parsed result.

        Otherwise (the default), return just `json_data`.
    """
    if is_string(thing):
        text = thing
        data = load_json_text(text, **kwargs)
    else:
        (data, text) = load_json_file(thing, **kwargs)

    return (data, text) if with_text else data


def dump_json_text(data, **kwargs):
    """
    Serialize and format JSON text from a possibly structured object.

    We do this according to parameters in keyword arguments, and we add a final
    trailing newline.

    :Args:
        data
            Data to serialize

        kwargs
            Keyword arguments, passed to `json.dumps()`:py:func:

    :Returns:
        The serialized JSON text
    """
    text = json.dumps(data, **kwargs)
    text += "\n"
    text = to_unicode(text)
    return text


def dump_json_file(data, outfile, **kwargs):
    """
    Serialize, format, and write JSON text to a file from an object.

    We do this according to parameters in keyword arguments, and we add a final
    trailing newline.

    :Args:
        data
            Data to serialize

        outfile
            Open file-ish to write JSON data to

        kwargs
            Keyword arguments, most of which are passed to
            `json.dump()`:py:func: (but see below).

    :Keyword Args:
        fp
            If this keyword argument is supplied, it is ignored, as the file to
            write to is required as `outfile`.

    :Returns:
        The serialized JSON text
    """
    if "fp" in kwargs:
        kwargs.pop("fp")
    text = dump_json_text(data, **kwargs)
    outfile.write(text)
    return text


def dump_json(data, outfile=None, **kwargs):
    """
    Serialize, format, and write JSON text to a file or string.

    We do this according to parameters in keyword arguments, and we add a final
    trailing newline.

    :Args:
        data
            Data to serialize

        outfile
            (optional) Open file-ish to write JSON data to

        kwargs
            Keyword arguments, most of which are passed to
            `json.dump()`:py:func: (but see below).

    :Keyword Args:
        fp
            If this keyword argument is supplied, it is ignored, as the file to
            write to is required as `outfile`.

    :Returns:
        The serialized JSON text
    """
    if "fp" in kwargs:
        kwargs.pop("fp")
    if outfile is not None:
        text = dump_json_file(data, outfile, **kwargs)
    else:
        text = dump_json_text(data, **kwargs)
    return text


def _compute_diff(filename, input_text, output_text, context_lines=DIFF_CONTEXT_LINES):
    input_filename = os.path.join("a", filename)
    output_filename = os.path.join("b", filename)

    input_lines = input_text.split("\n")
    output_lines = output_text.split("\n")

    return difflib.unified_diff(
        input_lines,
        output_lines,
        fromfile=input_filename,
        tofile=output_filename,
        n=context_lines,
        # TODO: Remove this if we start using readlines() to get input/output text.
        lineterm="",
    )


def _setup_argparser(prog):
    default_indent = 2
    default_inplace = False
    default_newlines = NEWLINE_FORMAT_NATIVE
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

    file_group = argp.add_argument_group(title="file-handling options")
    file_group.add_argument(
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
    file_group.add_argument(
        "-I",
        "--inplace",
        "--in-place",
        action="store_true",
        default=default_inplace,
        help="write changes to input file in place (default: {})".format(
            default_inplace
        ),
    )
    file_group.add_argument(
        "--pre-commit",
        action="store_true",
        help="Shortcut for '--inplace --changed'",
    )

    diff_group = argp.add_argument_group(title="diff options")
    diff_mutex_group = diff_group.add_mutually_exclusive_group()
    diff_mutex_group.add_argument(
        "-C",
        "--changed",
        "--show-changed",
        dest="show_changed",
        action="store_true",
        default=False,
        help="when used with '--inplace', note when a file has changed",
    )
    diff_mutex_group.add_argument(
        "-D",
        "--diff",
        "--show-diff",
        dest="show_diff",
        action="store_true",
        default=False,
        help="when used with '--inplace', show differences when a file has changed",
    )

    newlines_group = argp.add_argument_group(title="newline options")
    newlines_mutex_group = newlines_group.add_mutually_exclusive_group()
    newlines_mutex_group.add_argument(
        "--newlines",
        dest="newlines",
        action="store",
        choices=ALL_NEWLINE_FORMATS,
        default=default_newlines,
        help="newline format (default: {})".format(default_newlines),
    )
    newlines_mutex_group.add_argument(
        "-L",
        "--linux",
        dest="newlines",
        action="store_const",
        const=NEWLINE_FORMAT_LINUX,
        help="same as '--newlines {}'".format(NEWLINE_FORMAT_LINUX),
    )
    newlines_mutex_group.add_argument(
        "-M",
        "--microsoft",
        dest="newlines",
        action="store_const",
        const=NEWLINE_FORMAT_MICROSOFT,
        help="same as '--newlines {}'".format(NEWLINE_FORMAT_MICROSOFT),
    )
    newlines_mutex_group.add_argument(
        "-N",
        "--native",
        dest="newlines",
        action="store_const",
        const=NEWLINE_FORMAT_NATIVE,
        help="same as '--newlines {}'".format(NEWLINE_FORMAT_NATIVE),
    )

    json_group = argp.add_argument_group(title="JSON options")
    json_group.add_argument(
        "-c",
        "--compact",
        action="store_true",
        default=default_compact,
        help="compact JSON onto one line with minimal whitespace (default: {})".format(
            default_compact
        ),
    )
    json_group.add_argument(
        "-n",
        "--indent",
        action="store",
        default=default_indent,
        help="number of spaces or string for indenting (default: {})".format(
            default_indent
        ),
    )
    json_group.add_argument(
        "-s",
        "--sort-keys",
        action="store_true",
        default=default_sort,
        help="sort output alphabetically by key (default: same order as read)",
    )

    completion_group = argp.add_argument_group(title="autocompletion options")
    completion_group.add_argument(
        "--completion-help",
        action="store_true",
        help="Print instructions for enabling shell command-line autocompletion",
    )
    completion_group.add_argument(
        "--bash-completion",
        action="store_true",
        help="Print autocompletion code for Bash-compatible shells to evaluate",
    )

    argp.add_argument(
        "--debug",
        action="store_true",
        default=default_debug,
        help="turn on debug messages (default: {})".format(default_debug),
    )
    argp.add_argument("-V", "--version", action="version", version=get_version(prog))

    return argp


def _check_newlines(cli_args):
    if cli_args.newlines not in NEWLINE_FORMATS:
        cli_args.newlines = NEWLINE_FORMAT_ALIASES[cli_args.newlines]


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
        output_filename = _normalize_path(cli_args.output_filename)
        input_filename = _normalize_path(cli_args.input_filenames[0])
        if input_filename != "-" and input_filename == output_filename:
            raise RuntimeError(
                "input file and output file are the same; "
                "use '--inplace' to modify files in place"
            )
    else:
        if cli_args.output_filename is not None:
            raise RuntimeError("output files do not make sense with '--inplace'")

        for input_filename in cli_args.input_filenames:
            if input_filename == "-":
                raise RuntimeError(
                    "reading from stdin does not make sense with '--inplace'"
                )


def _check_completion_args(cli_args):
    return any([cli_args.completion_help, cli_args.bash_completion])


def _do_completion(cli_args, prog):
    if cli_args.completion_help:
        print(completion.get_instructions(prog, ["--bash-completion"]))
    elif cli_args.bash_completion:
        print(completion.get_commands(prog))


def _check_pre_commit_args(cli_args):
    if not cli_args.pre_commit:
        return
    cli_args.inplace = True
    if not cli_args.show_diff:
        cli_args.show_changed = True


def _check_diff_args(cli_args):
    if cli_args.show_changed and not cli_args.inplace:
        raise RuntimeError("'-C/--show-changed' only makes sense with '--inplace'")
    if cli_args.show_diff and not cli_args.inplace:
        raise RuntimeError("'-D/--show-diff' only makes sense with '--inplace'")


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

    return (program, program_args)


def _compose_kwargs(cli_args):
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

    return (load_kwargs, dump_kwargs)


def cli(*program_args):
    """Process command-line."""
    (prog, program_args) = _check_program_args(program_args)
    argparser = _setup_argparser(prog)
    argcomplete.autocomplete(argparser)
    cli_args = argparser.parse_args(program_args)

    if _check_completion_args(cli_args):
        _do_completion(cli_args, prog)
        return STATUS_OK

    _check_pre_commit_args(cli_args)
    _check_diff_args(cli_args)
    _check_newlines(cli_args)
    _check_input_and_output_filenames(cli_args)

    (load_kwargs, dump_kwargs) = _compose_kwargs(cli_args)

    overall_status = STATUS_OK

    for input_filename in cli_args.input_filenames:
        file_status = STATUS_OK
        input_iofile = TextIOFile(
            input_filename,
            input_newline="",
            output_newline=NEWLINE_VALUES[cli_args.newlines],
        )
        output_iofile = (
            input_iofile
            if cli_args.inplace
            else TextIOFile(
                cli_args.output_filename,
                input_newline="",
                output_newline=NEWLINE_VALUES[cli_args.newlines],
            )
        )

        input_iofile.open_for_input()

        try:
            (data, input_text) = load_json(
                input_iofile.file, with_text=True, **load_kwargs
            )
        except ValueError as e:
            if not cli_args.inplace:
                raise SystemExit(e)
            overall_status = STATUS_SYNTAX_ERROR
            file_status = STATUS_SYNTAX_ERROR
            print(e, file=sys.stderr)

        input_iofile.close()

        if file_status != STATUS_SYNTAX_ERROR:
            output_iofile.open_for_output()
            dump_json(data, output_iofile.file, **dump_kwargs)
            output_iofile.close()
            if cli_args.inplace and (cli_args.show_changed or cli_args.show_diff):
                output_iofile.open_for_input()
                output_text = output_iofile.file.read()
                if input_text != output_text:
                    file_status = STATUS_CHANGED
                    if overall_status != STATUS_SYNTAX_ERROR:
                        overall_status = file_status
                    print(
                        "Reformatted {}".format(output_iofile.file.name),
                        file=sys.stderr,
                    )
                    if cli_args.show_diff:
                        for line in _compute_diff(
                            output_iofile.file.name, input_text, output_text
                        ):
                            print(line)
                output_iofile.close()

    return overall_status


def main(*program_args):
    """Provide main functionality."""
    return cli(*program_args)


if __name__ == "__main__":
    sys.exit(main())
