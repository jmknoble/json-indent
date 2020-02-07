#!/bin/sh

set -e
set -u

PrintSampleConfig() {
    (set -x; pre-commit sample-config)
}

HOOK_CONFIG=".pre-commit-config.yaml"

if [ -f "${HOOK_CONFIG}" ]; then
    echo "warning: '${HOOK_CONFIG}' file already exists!" >&2
    echo "warning: printing sample config to stdout instead." >&2
    echo "(you may redirect stdout to the file of your choice)." >&2
    PrintSampleConfig
else
    echo "storing sample config in '${HOOK_CONFIG}'" >&2
    PrintSampleConfig >"${HOOK_CONFIG}"
fi
