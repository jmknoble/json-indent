#!/bin/sh

set -e
set -u

# This uses [python-venv](https://github.com/jmknoble/python-venv)
#
# Call this script with '-n' or '--dry-run' for a dry run

VENV_DIR="${HOME}/.venvs"

set -x

mkdir -p "${VENV_DIR}"

python-venv replace \
    -t venv \
    -r wheel \
    -e "${VENV_DIR}/json-indent" \
    --python /usr/bin/python3 \
    ${1:+"$@"}
