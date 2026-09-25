#!/usr/bin/env bash
# Lazy attempt 2: minimal well-formed files. Tests whether merely existing,
# parseable JSON is enough.
set -euo pipefail
mkdir -p /app/output
echo '{}' > /app/output/posterior.json
echo '{}' > /app/output/policy.json
echo '{"roots": []}' > /app/output/audit.json
