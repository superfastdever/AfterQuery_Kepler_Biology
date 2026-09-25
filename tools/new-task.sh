#!/usr/bin/env bash
# Scaffold a new task directory from _template/.
#
#   tools/new-task.sh <slug>
#
# <slug> must be lowercase and at most three hyphen-separated words. It becomes
# the directory name, the [task].name suffix, and the name submitted on the
# platform -- all three must agree.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$ROOT/_template"

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

[ $# -eq 1 ] || die "usage: tools/new-task.sh <slug>"
slug="$1"

[[ "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+){0,2}$ ]] \
  || die "slug '$slug' must be lowercase and at most 3 hyphen-separated words"

dest="$ROOT/tasks/$slug"
[ -e "$dest" ] && die "$dest already exists"
[ -d "$TEMPLATE" ] || die "template not found at $TEMPLATE"

mkdir -p "$ROOT/tasks"
cp -R "$TEMPLATE" "$dest"

# The template's README documents how to use the template. It is not task
# content and must not ship in the submission zip. Design notes belong in
# docs/lessons-learned.md, which stays out of the bundle.
rm -f "$dest/README.md"

# Point the config at the new slug. Everything else is left as a TODO on
# purpose -- the structure check fails while placeholders remain.
sed -i.bak "s|afterquery/UNSET-slug|afterquery/$slug|" "$dest/task.toml"
rm -f "$dest/task.toml.bak"

chmod +x "$dest/solution/solve.sh" "$dest/tests/test.sh"

cat <<EOF
Created tasks/$slug/

Next:
  1. Write down the agent failure mode this task targets, and check
     docs/lessons-learned.md that it differs from earlier tasks.
  2. Build environment/, then tests/ (write the verifier before the solution),
     then solution/solve.sh, then cheat/.
  3. instruction.md is written by the repo owner, not by AI. See CLAUDE.md.

  tools/structure-check.py tasks/$slug
  tools/validate.sh tasks/$slug
EOF
