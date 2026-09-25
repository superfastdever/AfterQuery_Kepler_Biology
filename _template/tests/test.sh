#!/usr/bin/env bash
# Verifier entry point.
#
# Contract: this script MUST leave exactly "0" or "1" in
# /logs/verifier/reward.txt on every code path, including crashes. Partial
# credit does not exist.
#
# Install nothing here. Every tool must already be in tests/Dockerfile.

set -uo pipefail

mkdir -p /logs/verifier

# Default to failure. If anything below dies unexpectedly, the reward is
# already written and is 0.
echo 0 > /logs/verifier/reward.txt

pytest \
  --ctrf /logs/verifier/ctrf.json \
  /tests/test_outputs.py \
  -rA
status=$?

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
fi

# Exit 0 regardless: the reward file carries the verdict, and a non-zero exit
# here reads as a verifier malfunction rather than a failed attempt.
exit 0
