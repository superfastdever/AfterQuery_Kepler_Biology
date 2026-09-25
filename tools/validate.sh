#!/usr/bin/env bash
# Run the two gates Kepler runs on the real harness.
#
#   tools/validate.sh tasks/<slug> [--check]
#
#   oracle -> solution/solve.sh stands in for the agent; must score exactly 1
#   nop    -> nothing is done at all;                     must score exactly 0
#
# --check additionally runs harbor's LLM rubric review, which needs an API key.
#
# A failure here is a guaranteed pipeline failure, so never submit a bundle
# that has not passed both.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

die() { printf 'error: %s\n' "$1" >&2; exit 1; }

[ $# -ge 1 ] || die "usage: tools/validate.sh tasks/<slug> [--check]"
task="$(cd "$1" 2>/dev/null && pwd)" || die "no such directory: $1"
shift
run_rubric=0
[ "${1:-}" = "--check" ] && run_rubric=1

command -v harbor >/dev/null 2>&1 || die "harbor not installed (uv tool install harbor)"
docker info >/dev/null 2>&1 || die "docker daemon is not running"

jobs_dir="$ROOT/build/harbor-jobs"
mkdir -p "$jobs_dir"

# Structure first: no point burning a container build on a bundle that would be
# rejected at submit. This always runs against the REAL bundle.
printf '== structure check ==\n'
python3 "$ROOT/tools/structure-check.py" "$task" || die "structure check failed"

# Some sandboxes intercept TLS, which breaks `pip install` inside Docker
# builds. Harbor must then run against a CA-patched copy; the real bundle stays
# clean. See tools/_local_ca_patch.py.
CA_BUNDLE="${CCR_CA_BUNDLE:-/root/.ccr/ca-bundle.crt}"
run_target="$task"
if [ -f "$CA_BUNDLE" ]; then
  printf '\n== local TLS proxy detected ==\n'
  patched="$ROOT/build/.local-validation/$(basename "$task")"
  python3 "$ROOT/tools/_local_ca_patch.py" "$task" "$patched" --ca "$CA_BUNDLE" \
    || die "could not prepare the local validation copy"
  run_target="$patched"
  printf 'Running harbor against the patched copy at build/.local-validation/.\n'
  printf 'The committed bundle is unmodified. Re-validate on a machine without\n'
  printf 'a TLS-intercepting proxy before trusting this as a final gate.\n'
fi

# Read the reward harbor wrote for the most recent job.
reward_of() {
  local job_root="$1"
  local f
  f="$(find "$job_root" -name reward.txt -type f -printf '%T@ %p\n' 2>/dev/null \
        | sort -rn | head -1 | cut -d' ' -f2-)"
  [ -n "$f" ] && tr -d '[:space:]' < "$f"
}

run_agent() {
  local agent="$1" expected="$2" job
  job="$jobs_dir/$(basename "$task")-$agent-$(date +%s)"
  printf '\n== %s run (expecting reward %s) ==\n' "$agent" "$expected"
  harbor run -p "$run_target" -a "$agent" -e docker -o "$job" -y >"$job.log" 2>&1
  local status=$? actual
  actual="$(reward_of "$job")"
  if [ -z "$actual" ]; then
    printf 'FAIL %s: no reward.txt produced (harbor exit %d)\n' "$agent" "$status"
    printf '  log: %s\n' "$job.log"
    tail -25 "$job.log" 2>/dev/null | sed 's/^/  | /'
    return 1
  fi
  if [ "$actual" != "$expected" ]; then
    printf 'FAIL %s: reward %s, expected %s\n' "$agent" "$actual" "$expected"
    printf '  log: %s\n' "$job.log"
    return 1
  fi
  printf 'ok   %s: reward %s\n' "$agent" "$actual"
  return 0
}

rc=0
run_agent oracle 1 || rc=1
run_agent nop    0 || rc=1

if [ "$run_rubric" -eq 1 ]; then
  printf '\n== rubric review ==\n'
  harbor check "$task" -m anthropic/claude-opus-4-8 || rc=1
fi

printf '\n'
if [ "$rc" -eq 0 ]; then
  printf 'validate: PASS (oracle=1, nop=0)\n'
  printf 'Re-run this a few times: the verifier must be deterministic.\n'
else
  printf 'validate: FAIL\n'
  printf 'If oracle scored 0, read the verifier log before touching the solution.\n'
  printf 'Most first failures are an artifact path the verifier cannot find, or a\n'
  printf 'tool that was never installed in the verifier image.\n'
fi
exit "$rc"
