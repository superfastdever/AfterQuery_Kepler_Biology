#!/usr/bin/env bash
# Build the submission zip for a task.
#
#   tools/package.sh <slug>
#
# Kepler takes "one zip of the task directory contents", so the archive has
# instruction.md, task.toml, environment/ and so on at its top level -- not
# nested inside a <slug>/ folder.
#
# The structure check runs first and the zip is not written if it fails.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

[ $# -eq 1 ] || die "usage: tools/package.sh <slug>"
slug="$1"
task="$ROOT/tasks/$slug"
[ -d "$task" ] || die "no such task: tasks/$slug"

command -v zip >/dev/null 2>&1 || die "zip is not installed (apt-get install zip)"

# Hard stop: this repo submits under the Scientific computing dataset, whose
# guide advertises "a stricter, science-specific bundle contract". Until that
# contract is vendored and the tooling re-checked against it, any zip built
# here is validated only against the General dataset's laxer rules. Building
# and validating a task is fine; shipping one is not.
if [ ! -f "$ROOT/docs/kepler-instructions-scientific-computing.md" ] \
   && [ "${KEPLER_ALLOW_UNKNOWN_CONTRACT:-0}" != "1" ]; then
  die "the Scientific computing bundle contract is not vendored.
  docs/kepler-instructions-scientific-computing.md is missing, so this bundle
  has only been checked against the General dataset's rules. Vendor the real
  contract and re-check tools/structure-check.py against it before packaging.
  See CLAUDE.md, 'Open: bundle contract'.
  To override deliberately: KEPLER_ALLOW_UNKNOWN_CONTRACT=1 tools/package.sh $slug"
fi

python3 "$ROOT/tools/structure-check.py" "$task" \
  || die "structure check failed -- not packaging"

mkdir -p "$ROOT/build"
out="$ROOT/build/$slug.zip"
rm -f "$out"

( cd "$task" && zip -rq "$out" . \
    -x '.DS_Store' '*/.DS_Store' '__pycache__/*' '*/__pycache__/*' \
       '*.pyc' '.pytest_cache/*' '*/.pytest_cache/*' )

printf 'wrote build/%s.zip (%s)\n' "$slug" "$(du -h "$out" | cut -f1)"
printf '\ncontents:\n'
unzip -l "$out" | sed 's/^/  /'
printf '\nReminder: submit with category Science and label Biology.\n'
