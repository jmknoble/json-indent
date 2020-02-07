#!/bin/sh

set -e
set -u

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

pre-commit run ${1:+"$@"}
