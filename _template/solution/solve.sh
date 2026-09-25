#!/usr/bin/env bash
# Reference solution. Runs in the agent's environment container in place of the
# agent during the oracle run, which must score exactly 1.
#
# This directory is mounted ONLY for the oracle run. The agent never sees it.
#
# Python packages installed here must be pinned with ==.

set -euo pipefail

# Time this script. [agent].timeout_sec should be several times its runtime.

# TODO: produce every artifact declared in task.toml, at the exact absolute
# paths the instruction names.

echo "TODO: implement the reference solution" >&2
exit 1
