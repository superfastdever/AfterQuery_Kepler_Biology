#!/usr/bin/env bash
# Lazy attempt 3: truncated JSON, as a crashed or interrupted run would leave.
set -euo pipefail
mkdir -p /app/output
printf '{"hypothesis_weights": [0.1, 0.2,' > /app/output/posterior.json
printf '{"initial_restored_mask": 4, "survey": "inten'  > /app/output/policy.json
printf '{"roots": [{"initial_restored_mask"'           > /app/output/audit.json
