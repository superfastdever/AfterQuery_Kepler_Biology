#!/usr/bin/env bash
# Build the submission zip for a task.
#
#   tools/package.sh <slug>
#
# Kepler takes "one zip of the task directory contents", so the archive has
# instruction.md, task.toml, environment/ and so on at its top level -- not
# nested inside a <slug>/ or a date folder.
#
# The structure check runs first and the zip is not written if it fails.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

[ $# -eq 1 ] || die "usage: tools/package.sh <slug>"
slug="$1"

# Tasks live in tasks/<date>/<slug>/; a bare tasks/<slug>/ predating the dated
# layout still resolves.
task="$(find "$ROOT/tasks" -mindepth 2 -maxdepth 3 -type d -name "$slug" 2>/dev/null | head -1)"
[ -n "$task" ] && [ -d "$task" ] || die "no such task: $slug (looked under tasks/)"

command -v zip >/dev/null 2>&1 || die "zip is not installed (apt-get install zip)"

python3 "$ROOT/tools/structure-check.py" "$task" \
  || die "structure check failed -- not packaging"

mkdir -p "$ROOT/build"
out="$ROOT/build/$slug.zip"
rm -f "$out"

# task-meta.json is repo bookkeeping, not task content: it never ships.
( cd "$task" && zip -rq "$out" . \
    -x 'task-meta.json' \
       '.DS_Store' '*/.DS_Store' '__pycache__/*' '*/__pycache__/*' \
       '*.pyc' '.pytest_cache/*' '*/.pytest_cache/*' )

# Advance the recorded status, then refresh the index.
python3 - "$task" <<'PY'
import json, sys
from pathlib import Path
meta_path = Path(sys.argv[1]) / "task-meta.json"
if meta_path.is_file():
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    # Never move a task backwards: a repackage of a submitted task stays
    # submitted.
    order = ["building", "validated", "packaged", "submitted", "approved", "rejected"]
    cur = meta.get("status", "building")
    if cur in order and order.index(cur) < order.index("packaged"):
        meta["status"] = "packaged"
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
PY
python3 "$ROOT/tools/task-list.py" >/dev/null

printf 'wrote build/%s.zip (%s)\n' "$slug" "$(du -h "$out" | cut -f1)"
printf '\ncontents:\n'
unzip -l "$out" | sed 's/^/  /'
printf '\nReminder: the domain and field in task.toml must match the submit form.\n'
