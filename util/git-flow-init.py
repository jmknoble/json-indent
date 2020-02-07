#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys

import utilutil.argparsing as argparsing
import utilutil.runcommand as runcommand

DESCRIPTION = (
    "Initialize git-flow for the currently cloned git project, "
    "using standard settings."
)

EPILOG = (
    "To pass arguments to 'git-flow init', add '--', followed by "
    "the arguments, to the end of the command line.  "
    "For example, to add '--force', use: '%(prog)s -- --force'"
)

PERMANENT_BRANCHES = ["master", "develop"]


def _verify_branch_exists(branch, origin="origin"):
    """Return `True` if `branch` is a valid/known Git branch"""
    output = runcommand.run_command(
        [
            "git",
            "branch",
            "-r",
            "--list",
            "{origin}/{branch}".format(origin=origin, branch=branch),
        ],
        return_output=True,
    )
    return len(output.strip()) > 0


def _git_flow_init(extra_args, dry_run=False):
    """Initialize git-flow"""
    command = [
        "git",
        "flow",
        "init",
        "--defaults",
        "--feature",
        "feature/",
        "--bugfix",
        "bugfix/",
        "--release",
        "release/",
        "--hotfix",
        "hotfix/",
        "--support",
        "support/",
        "--tag",
        "v",
    ]
    command.extend(extra_args)
    return runcommand.run_command(
        command, check=False, dry_run=dry_run, show_trace=True
    )


def _add_arguments(argparser):
    """Add command-line arguments to an argument parser"""
    argparsing.add_dry_run_argument(argparser)
    argparsing.add_chdir_argument(argparser)
    argparser.add_argument(
        "args",
        metavar="...",
        nargs=argparse.REMAINDER,
        help="arguments to pass to 'git-flow init', if any",
    )
    return argparser


def main(*argv):
    """Do the thing"""
    (prog, argv) = argparsing.grok_argv(argv)
    argparser = argparsing.setup_argparse(
        prog=prog, description=DESCRIPTION, epilog=EPILOG
    )
    _add_arguments(argparser)
    args = argparser.parse_args(argv)

    if args.working_dir is not None:
        runcommand.print_trace(["cd", args.working_dir], dry_run=args.dry_run)
        os.chdir(args.working_dir)

    for branch in PERMANENT_BRANCHES:
        if not _verify_branch_exists(branch):
            message = (
                "{prog}: error: branch '{branch}' not found: "
                "cannot initialize git-flow\n"
                "{prog}: (perhaps you need to use gitflower on this repo first?)"
            ).format(prog=prog, branch=branch)
            print(message, file=sys.stderr)
            return 1

    extra_args = args.args[1:] if args.args and args.args[0] == "--" else args.args
    return _git_flow_init(extra_args, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
