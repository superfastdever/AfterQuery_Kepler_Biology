#!/usr/bin/env bash
# Reference solution. Stands in for the agent during the oracle run and must
# score exactly 1.
#
# Everything is recomputed from /app/input inside this container. No
# precomputed answer is carried in.

set -euo pipefail

# Resolve beside this script rather than assuming a mount point: harbor decides
# where solution/ lands, and that is not guaranteed to be /app/solution.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "${HERE}/run_oracle.py"

# Fail loudly here rather than leaving the verifier to report a missing file.
for artifact in posterior.json policy.json audit.json; do
  test -s "/app/output/${artifact}" || {
    echo "reference solution did not produce /app/output/${artifact}" >&2
    exit 1
  }
done
