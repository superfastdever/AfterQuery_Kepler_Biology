#!/usr/bin/env bash
# Verifier entry point.
#
# Contract: leave exactly "0" or "1" in /logs/verifier/reward.txt on every code
# path. Reward is written as 0 first and only flipped to 1 on a clean pytest
# run, so any crash, timeout or unexpected exit leaves a failing reward behind
# rather than no reward at all.
#
# Installs nothing: every dependency is baked into tests/Dockerfile.

set -uo pipefail

mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt

cd /tests

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
