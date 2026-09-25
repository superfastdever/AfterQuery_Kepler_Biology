#!/usr/bin/env bash
# Scaffold a new task from _template/.
#
#   tools/new-task.sh <slug> [YYYY-MM-DD]
#
# The task lands in tasks/<date>/<slug>/, where <date> is today unless given.
# Grouping by creation date keeps the tree readable as tasks accumulate and
# gives task_list.md a stable ordering.
#
# <slug> must be lowercase and at most three hyphen-separated words. It becomes
# the directory name, the [task].name suffix, and the name submitted on the
# platform -- all three must agree.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$ROOT/_template"

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

[ $# -ge 1 ] && [ $# -le 2 ] || die "usage: tools/new-task.sh <slug> [YYYY-MM-DD]"
slug="$1"
date_dir="${2:-$(date -u +%F)}"

[[ "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+){0,2}$ ]] \
  || die "slug '$slug' must be lowercase and at most 3 hyphen-separated words"
[[ "$date_dir" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] \
  || die "date '$date_dir' must be YYYY-MM-DD"

# A slug must be unique across every date folder: it is the submitted task name.
if existing="$(find "$ROOT/tasks" -mindepth 2 -maxdepth 2 -type d -name "$slug" 2>/dev/null | head -1)" \
   && [ -n "$existing" ]; then
  die "slug '$slug' already exists at ${existing#"$ROOT"/}"
fi

dest="$ROOT/tasks/$date_dir/$slug"
[ -e "$dest" ] && die "$dest already exists"
[ -d "$TEMPLATE" ] || die "template not found at $TEMPLATE"

mkdir -p "$ROOT/tasks/$date_dir"
cp -R "$TEMPLATE" "$dest"

# The template's README documents how to use the template. It is not task
# content and must not ship in the submission zip. Design notes belong in
# docs/task-ideas.md, which stays out of the bundle.
rm -f "$dest/README.md"

# Point the config at the new slug. Everything else is left as a placeholder on
# purpose -- the structure check fails while any remain.
sed -i.bak "s|afterquery/UNSET-slug|afterquery/$slug|" "$dest/task.toml"
rm -f "$dest/task.toml.bak"

# Repo-side bookkeeping: what the platform bundle has no field for. Excluded
# from the submission zip by tools/package.sh.
#
# The timestamp must agree with the folder it sits in, or task_list.md sorts
# wrongly: backdated tasks get midnight on their stated date, today's get now.
if [ "$date_dir" = "$(date -u +%F)" ]; then
  created="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
else
  created="${date_dir}T00:00:00Z"
fi

cat > "$dest/task-meta.json" <<EOF
{
  "slug": "$slug",
  "created": "$created",
  "status": "building",
  "completed": null,
  "summary": "",
  "failure_mode": ""
}
EOF

chmod +x "$dest/solution/solve.sh" "$dest/tests/test.sh"

python3 "$ROOT/tools/task-list.py" >/dev/null

rel="${dest#"$ROOT"/}"
cat <<EOF
Created $rel/

Next:
  1. Fill in failure_mode and summary in task-meta.json. Check
     docs/lessons-learned.md that the failure mode differs from earlier tasks.
  2. Build environment/, then tests/ (write the verifier before the solution),
     then solution/solve.sh, then cheat/.
  3. instruction.md is written by the repo owner, not by AI. See CLAUDE.md.

  tools/structure-check.py $rel
  tools/validate.sh $rel
EOF
