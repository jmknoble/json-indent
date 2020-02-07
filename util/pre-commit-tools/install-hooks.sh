#!/bin/sh

set -e
set -u

HOOK_CONFIG=".pre-commit-config.yaml"

if [ ! -f "${HOOK_CONFIG}" ]; then
    echo "warning: no '${HOOK_CONFIG}' file found ..." >&2
    echo "warning: some hook installation steps will fail." >&2
    echo "(you can re-run this script after creating a '${HOOK_CONFIG}' file)" >&2
    echo "(you can create a sample '${HOOK_CONFIG}' using 'seed-hook-config.sh')" >&2
    echo "" >&2
fi

set -x

pre-commit install -f --install-hooks -t pre-commit
