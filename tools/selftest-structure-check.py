#!/usr/bin/env python3
"""Negative tests for tools/structure-check.py.

A checker that never fails is worthless. This copies `_template`, breaks one
rule at a time, and asserts the corresponding check fires. The clean template
is also asserted to pass, so the suite catches over-strict rules too.

    python3 tools/selftest-structure-check.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "_template"
CHECKER = ROOT / "tools" / "structure-check.py"


def patch(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"selftest is stale: {old!r} not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# Each mutation takes the copied task dir and breaks exactly one rule.
# The second element is the rule name expected in the failure output.
MUTATIONS: list[tuple[str, callable, str]] = [
    ("missing required file",
     lambda d: (d / "instruction.md").unlink(),
     "layout"),

    ("allow_internet set",
     lambda d: patch(d / "task.toml", "gpus = 0", "gpus = 0\nallow_internet = true"),
     "environment"),

    ("cpus not a standard size",
     lambda d: patch(d / "task.toml", "cpus = 1", "cpus = 3"),
     "environment"),

    ("memory not a standard size",
     lambda d: patch(d / "task.toml", "memory_mb = 2048", "memory_mb = 3000"),
     "environment"),

    ("storage over maximum",
     lambda d: patch(d / "task.toml", "storage_mb = 10240", "storage_mb = 99999"),
     "environment"),

    ("agent timeout below floor",
     lambda d: patch(d / "task.toml", "timeout_sec = 9000.0", "timeout_sec = 600.0"),
     "agent"),

    ("verifier not separate",
     lambda d: patch(d / "task.toml",
                     'environment_mode = "separate"', 'environment_mode = "shared"'),
     "verifier"),

    ("unpinned python package",
     lambda d: patch(d / "tests" / "Dockerfile",
                     "pytest==9.1.1 pytest-json-ctrf==0.5.2",
                     "pytest pytest-json-ctrf==0.5.2"),
     "pins"),

    ("version-pinned apt package",
     lambda d: patch(d / "environment" / "Dockerfile",
                     "ca-certificates \\", "ca-certificates=20240203 \\"),
     "pins"),

    ("apt without list cleanup",
     lambda d: patch(d / "environment" / "Dockerfile",
                     "    && rm -rf /var/lib/apt/lists/*", ""),
     "apt"),

    ("verifier installs at run time",
     lambda d: patch(d / "tests" / "test.sh",
                     "pytest \\", "pip install requests==2.32.3\npytest \\"),
     "verifier-script"),

    ("verifier image missing artifact parent",
     lambda d: patch(d / "tests" / "Dockerfile", "RUN mkdir -p /app", ""),
     "verifier-image"),

    ("verifier image missing mandated pin",
     lambda d: patch(d / "tests" / "Dockerfile", "pytest==9.1.1", "pytest==9.0.0"),
     "verifier-image"),

    ("artifact never named in instruction",
     lambda d: patch(d / "instruction.md", "/app/output.json", "the output file"),
     "instruction"),

    ("wrong N in mandated suffix",
     lambda d: patch(d / "instruction.md",
                     "You have 9000 seconds", "You have 600 seconds"),
     "instruction"),

    ("mandated suffix missing",
     lambda d: patch(d / "instruction.md",
                     "You have 9000 seconds to complete this task. "
                     "Do not cheat by using online solutions or hints "
                     "specific to this task.", "Good luck."),
     "instruction"),

    ("no blank line before suffix",
     lambda d: patch(d / "instruction.md",
                     "-->\n\nYou have 9000", "-->\nYou have 9000"),
     "instruction"),

    ("canary marker present",
     lambda d: patch(d / "instruction.md", "# TODO: title",
                     "# TODO: title\n\nharbor-canary GUID 1234"),
     "forbidden"),

    ("platform pin in Dockerfile",
     lambda d: patch(d / "environment" / "Dockerfile",
                     "FROM ubuntu:24.04", "FROM --platform=linux/amd64 ubuntu:24.04"),
     "forbidden"),

    ("environment leaks tests path",
     lambda d: patch(d / "environment" / "Dockerfile",
                     "WORKDIR /app", "COPY ../tests/ground_truth.json /app/\nWORKDIR /app"),
     "leakage"),

    ("compose declares volumes",
     lambda d: (d / "environment" / "docker-compose.yaml").write_text(
         "services:\n  db:\n    image: postgres\nvolumes:\n  data:\n", encoding="utf-8"),
     "compose"),

    ("artifacts below first section",
     lambda d: patch(d / "task.toml",
                     'artifacts = ["/app/output.json"]', "")
               or patch(d / "task.toml", "[task]",
                        '[task]\n# moved too low\nartifacts = ["/app/output.json"]'),
     "task.toml"),

    ("invalid subcategory for category",
     lambda d: patch(d / "task.toml",
                     'subcategory = "Biology"', 'subcategory = "Frontend"'),
     "metadata"),

    ("missing required metadata field",
     lambda d: patch(d / "task.toml", "relevant_experience = \"\"", ""),
     "metadata"),

    ("task name not under afterquery/",
     lambda d: patch(d / "task.toml",
                     'name = "afterquery/TODO-slug"', 'name = "me/my-task"'),
     "task.toml"),
]


def run_checker(task_dir: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--allow-placeholders", str(task_dir)],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def failing_rules(output: str) -> set[str]:
    return set(re.findall(r"^\s*FAIL\s+([\w.-]+):", output, re.M))


def main() -> int:
    if not TEMPLATE.is_dir():
        print(f"error: {TEMPLATE} not found", file=sys.stderr)
        return 2

    passed = failed = 0

    # The clean template must pass, or every negative result below is suspect.
    code, out = run_checker(TEMPLATE)
    if code == 0:
        print("  ok    baseline: clean template passes")
        passed += 1
    else:
        print(f"  FAIL  baseline: clean template should pass but did not\n{out}")
        failed += 1

    for label, mutate, expected_rule in MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / TEMPLATE.name
            shutil.copytree(TEMPLATE, work)
            try:
                mutate(work)
            except AssertionError as exc:
                print(f"  FAIL  {label}: {exc}")
                failed += 1
                continue

            code, out = run_checker(work)
            rules = failing_rules(out)
            if code != 0 and expected_rule in rules:
                print(f"  ok    {label}  -> {expected_rule}")
                passed += 1
            elif code != 0:
                print(f"  FAIL  {label}: fired {sorted(rules)}, "
                      f"expected {expected_rule!r}")
                failed += 1
            else:
                print(f"  FAIL  {label}: checker did not detect the breakage")
                failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
