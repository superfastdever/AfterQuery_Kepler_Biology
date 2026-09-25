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
