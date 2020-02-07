#!/bin/sh

set -e
set -u

if [ $# -lt 1 ]; then
    echo "error: please supply at least one hook name to run manually" >&2
    exit 1
fi

if [ $# -eq 0 ]; then
    set -- --all-files
else
    case "$*" in
        -a|--all-files|-h|--help)
            :
            ;;
        "-a "*|"--all-files "*|"-h "*|"--help "*)
            :
            ;;
        *" -a"|*" --all-files"|*" -h"|*" --help")
            :
            ;;
        *" -a "*|*" --all-files "*|*" -h "*|*" --help "*)
            :
            ;;
        "--files "*|*" --files "*)
            :
            ;;
        *)
            set -- --all-files ${1:+"$@"}
    esac
fi

set -x

pre-commit run --hook-stage manual "$@"
