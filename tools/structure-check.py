#!/usr/bin/env python3
"""Replicate Kepler's submit-time structure check locally.

Kepler rejects a bundle the moment it is submitted if any of these rules fail,
and the rest of the pipeline never runs. Catching them here costs seconds
instead of a submission.

    tools/structure-check.py tasks/<slug>
    tools/structure-check.py --allow-placeholders _template

Exit status is 0 when every rule passes, 1 otherwise.

Rules are transcribed from docs/kepler-instructions-general.md ("Bundle layout",
"task.toml", "Rules and limits", "Writing the verifier", "Common mistakes").
When that document changes, change this file with it.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

REQUIRED_FILES = (
    "instruction.md",
    "task.toml",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/test.sh",
    "tests/Dockerfile",
)

# Files scanned for dependency-pinning rules.
PIN_SCANNED = (
    "environment/Dockerfile",
    "tests/Dockerfile",
    "tests/test.sh",
    "solution/solve.sh",
)

# Life Sciences fields, as the submit form lists them. The form shows display
# names; task.toml carries slugs, and the exact slug strings are not yet known
# -- see "Open: bundle contract" in CLAUDE.md. Both spellings are accepted here
# so the rule is useful either way.
LIFE_SCIENCES_FIELDS = {
    "Ecology & Evolutionary Biology",
    "Neuroscience & Cognitive Science",
    "Medicine & Health Sciences",
    "Biology & Biotechnology",
}

# Repo owner's policy, NOT a platform rule: this field's pool is already well
# stocked, so tasks are steered to the thin ones. One line to relax if that
# changes.
BANNED_FIELDS = {"Biology & Biotechnology"}


def _norm_field(value: str) -> str:
    """Compare display names and slugs alike: 'ecology-evolutionary-biology'
    and 'Ecology & Evolutionary Biology' normalise to the same token."""
    return re.sub(r"[^a-z0-9]+", "", str(value).lower().replace("and", ""))


REQUIRED_METADATA = (
    "author_name",
    "author_email",
    "difficulty_explanation",
    "solution_explanation",
    "verification_explanation",
    "domain",
    "field",
    "subfield",
    "tags",
    "expert_time_estimate_hours",
    "relevant_experience",
)

VERIFIER_PINS = ("pytest==9.1.1", "pytest-json-ctrf==0.5.2")

ALLOWED_CPUS = {1, 2, 4, 8, 16}
ALLOWED_MEMORY_MB = {1024, 2048, 4096, 8192, 16384}
MAX_STORAGE_MB = 40960
AGENT_TIMEOUT_MIN = 9000
TIMEOUT_MAX = 18000

SUFFIX_TEMPLATE = (
    "You have {n} seconds to complete this task. "
    "Do not cheat by using online solutions or hints specific to this task."
)

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){0,2}$")

# Tokens that are flags or targets rather than package specs.
_NON_PACKAGE = re.compile(r"^(-|\$|/|\.|https?://|git\+)")

INSTALL_PY_RE = re.compile(
    r"\b(?:pip3?|uv\s+pip|python3?\s+-m\s+pip)\s+install\b([^\n]*)"
)
INSTALL_APT_RE = re.compile(r"\bapt(?:-get)?\s+install\b([^\n]*)")


@dataclass
class Report:
    """Collects rule outcomes so every rule runs, not just the first failure."""

    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passed: int = 0

    def ok(self, _rule: str) -> None:
        self.passed += 1

    def fail(self, rule: str, detail: str) -> None:
        self.failures.append(f"{rule}: {detail}")

    def warn(self, rule: str, detail: str) -> None:
        self.warnings.append(f"{rule}: {detail}")

    def check(self, rule: str, condition: bool, detail: str) -> bool:
        if condition:
            self.ok(rule)
        else:
            self.fail(rule, detail)
        return condition


def strip_comments(text: str) -> str:
    """Drop whole-line shell/Dockerfile comments.

    Done before continuation-unwrapping so a commented example command cannot
    be mistaken for a real one.
    """
    return "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
    )


def unwrap_continuations(text: str) -> str:
    """Join shell backslash-continuations so install commands read as one line."""
    return re.sub(r"\\\s*\n\s*", " ", text)


def code_of(path: Path) -> str:
    """File contents as executable code: comments removed, continuations joined."""
    return unwrap_continuations(strip_comments(read(path)))


def package_tokens(arglist: str) -> list[str]:
    """Package-looking tokens from an install command's arguments."""
    tokens = []
    for raw in arglist.split():
        tok = raw.strip("\"'\\")
        if not tok or _NON_PACKAGE.match(tok):
            continue
        tokens.append(tok)
    return tokens


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------

def check_layout(task: Path, rep: Report) -> None:
    for rel in REQUIRED_FILES:
        rep.check("layout", (task / rel).is_file(), f"missing required file {rel}")


def check_task_toml(task: Path, cfg: dict, rep: Report,
                    allow_placeholders: bool) -> None:
    raw = read(task / "task.toml")

    # `artifacts` must sit above the first [section].
    first_section = None
    artifacts_line = None
    for i, line in enumerate(raw.splitlines()):
        s = line.strip()
        if first_section is None and s.startswith("[") and not s.startswith("[["):
            first_section = i
        if artifacts_line is None and re.match(r"^artifacts\s*=", s):
            artifacts_line = i
    if rep.check("task.toml", artifacts_line is not None,
                 "no top-level `artifacts = [...]` declaration"):
        rep.check(
            "task.toml",
            first_section is None or artifacts_line < first_section,
            "`artifacts` must appear above the first [section]",
        )

    name = cfg.get("task", {}).get("name", "")
    if rep.check("task.toml", isinstance(name, str) and name.startswith("afterquery/"),
                 f'[task].name must be "afterquery/<slug>", got {name!r}'):
        if allow_placeholders:
            return  # the template legitimately carries a placeholder slug
        slug = name.split("/", 1)[1]
        rep.check("task.toml", bool(SLUG_RE.match(slug)),
                  f"slug {slug!r} must be lowercase, at most 3 hyphen-separated words")
        rep.check("task.toml", slug == task.name,
                  f"slug {slug!r} must equal the directory name {task.name!r}")


def check_metadata(cfg: dict, rep: Report, allow_placeholders: bool) -> None:
    md = cfg.get("metadata", {})
    for key in REQUIRED_METADATA:
        if key not in md:
            rep.fail("metadata", f"missing required field {key}")
            continue
        val = md[key]
        empty = val == "" or val == [] or val == 0
        if empty and not allow_placeholders:
            rep.fail("metadata", f"{key} is empty")
        else:
            rep.ok("metadata")

    field = md.get("field")
    if field and not (allow_placeholders and str(field).startswith("TODO")):
        known = {_norm_field(f): f for f in LIFE_SCIENCES_FIELDS}
        norm = _norm_field(field)
        allowed = sorted(LIFE_SCIENCES_FIELDS - BANNED_FIELDS)
        if rep.check("metadata", norm in known,
                     f"field {field!r} is not an in-scope Life Sciences field "
                     f"(expected one of {allowed}, as a slug or display name)"):
            rep.check(
                "metadata",
                known[norm] not in BANNED_FIELDS,
                f"field {known[norm]!r} is excluded by repo policy, not by the "
                "platform: its pool is well stocked, so tasks go to the thin "
                "fields instead (see CLAUDE.md). Relax BANNED_FIELDS to change.",
            )

    hrs = md.get("expert_time_estimate_hours")
    if isinstance(hrs, (int, float)) and not allow_placeholders:
        rep.check("metadata", hrs > 0, "expert_time_estimate_hours must be > 0")

    # Reviewers read these first; a one-liner reads as filler.
    for key in ("difficulty_explanation", "solution_explanation",
                "verification_explanation", "relevant_experience"):
        val = md.get(key, "")
        if isinstance(val, str) and val and len(val) < 120:
            rep.warn("metadata", f"{key} is very short ({len(val)} chars) "
                                 "-- reviewers reject generic text here")


def check_resources(task: Path, cfg: dict, rep: Report) -> None:
    ver = cfg.get("verifier", {})
    rep.check("verifier", ver.get("environment_mode") == "separate",
              '[verifier].environment_mode must be "separate"')
    vt = ver.get("timeout_sec")
    if isinstance(vt, (int, float)):
        rep.check("verifier", vt <= TIMEOUT_MAX,
                  f"[verifier].timeout_sec {vt} exceeds {TIMEOUT_MAX}")

    at = cfg.get("agent", {}).get("timeout_sec")
    if rep.check("agent", isinstance(at, (int, float)), "[agent].timeout_sec missing"):
        rep.check("agent", AGENT_TIMEOUT_MIN <= at <= TIMEOUT_MAX,
                  f"[agent].timeout_sec {at} outside "
                  f"[{AGENT_TIMEOUT_MIN}, {TIMEOUT_MAX}]")

    env = cfg.get("environment", {})
    rep.check("environment", "allow_internet" not in env,
              "allow_internet must not be set, with either value")
    rep.check("environment", env.get("cpus") in ALLOWED_CPUS,
              f"cpus {env.get('cpus')!r} must be one of {sorted(ALLOWED_CPUS)}")
    rep.check("environment", env.get("memory_mb") in ALLOWED_MEMORY_MB,
              f"memory_mb {env.get('memory_mb')!r} must be one of "
              f"{sorted(ALLOWED_MEMORY_MB)}")
    storage = env.get("storage_mb")
    if isinstance(storage, int):
        rep.check("environment", storage <= MAX_STORAGE_MB,
                  f"storage_mb {storage} exceeds {MAX_STORAGE_MB}")
    gpus = env.get("gpus", 0)
    rep.check("environment", gpus in (0, 1), f"gpus must be 0 or 1, got {gpus!r}")
    if gpus == 1:
        gt = env.get("gpu_types")
        rep.check("environment", isinstance(gt, list) and len(gt) == 1,
                  "gpus = 1 requires exactly one gpu_types class")
        rep.check("environment",
                  not (task / "environment/docker-compose.yaml").is_file(),
                  "a GPU task cannot use environment/docker-compose.yaml")


def check_pins(task: Path, rep: Report) -> None:
    for rel in PIN_SCANNED:
        path = task / rel
        if not path.is_file():
            continue
        text = code_of(path)
        for args in INSTALL_PY_RE.findall(text):
            if "-r" in args.split() or "--requirement" in args:
                continue
            for tok in package_tokens(args):
                rep.check("pins", "==" in tok,
                          f"{rel}: python package {tok!r} is not pinned with ==")
        for args in INSTALL_APT_RE.findall(text):
            for tok in package_tokens(args):
                rep.check("pins", "=" not in tok,
                          f"{rel}: apt package {tok!r} must not be version-pinned")


def check_apt_hygiene(task: Path, rep: Report) -> None:
    for rel in ("environment/Dockerfile", "tests/Dockerfile"):
        path = task / rel
        if not path.is_file():
            continue
        text = code_of(path)
        if not INSTALL_APT_RE.search(text):
            continue
        rep.check("apt", "apt-get update" in text,
                  f"{rel}: apt-get install without apt-get update")
        rep.check("apt", "rm -rf /var/lib/apt/lists/*" in text,
                  f"{rel}: must end apt usage with rm -rf /var/lib/apt/lists/*")


def check_verifier_image(task: Path, artifacts: list[str], rep: Report) -> None:
    path = task / "tests/Dockerfile"
    if not path.is_file():
        return
    text = code_of(path)

    for pin in VERIFIER_PINS:
        rep.check("verifier-image", pin in text,
                  f"tests/Dockerfile must install {pin}")

    rep.check("verifier-image", re.search(r"COPY\s+\.\s+/tests/?", text) is not None,
              "tests/Dockerfile must bake tests in with `COPY . /tests/`")

    # Every artifact's parent directory must be pre-created.
    for art in artifacts:
        parent = str(Path(art).parent)
        if parent in ("/", ""):
            continue
        rep.check(
            "verifier-image",
            re.search(rf"mkdir\s+-p[^\n]*{re.escape(parent)}\b", text) is not None,
            f"tests/Dockerfile must `mkdir -p {parent}` "
            f"(parent of declared artifact {art})",
        )


def check_verifier_script(task: Path, rep: Report) -> None:
    path = task / "tests/test.sh"
    if not path.is_file():
        return
    text = code_of(path)

    # Nothing may be installed at verify time.
    for pattern, label in (
        (r"\bapt(?:-get)?\s+(?:install|update)\b", "apt"),
        (r"\bcurl\b", "curl"),
        (r"\b(?:pip3?|uv\s+pip|uvx)\s", "pip/uv"),
    ):
        rep.check("verifier-script", re.search(pattern, text) is None,
                  f"tests/test.sh must not use {label} at verify time -- "
                  "bake it into tests/Dockerfile")

    rep.check("verifier-script", "/logs/verifier/reward.txt" in text,
              "tests/test.sh must write /logs/verifier/reward.txt")
    rep.check("verifier-script", "ctrf" in text.lower(),
              "tests/test.sh must emit a CTRF report (pytest --ctrf)")


def check_instruction(task: Path, cfg: dict, artifacts: list[str],
                      rep: Report, allow_placeholders: bool) -> None:
    path = task / "instruction.md"
    if not path.is_file():
        return
    text = read(path)

    at = cfg.get("agent", {}).get("timeout_sec")
    if isinstance(at, (int, float)):
        expected = SUFFIX_TEMPLATE.format(n=int(at))
        body = text.rstrip("\n")
        if rep.check("instruction", body.endswith(expected),
                     "must end with the mandated sentence "
                     f"(N = {int(at)}); got: ...{body[-90:]!r}"):
            before = body[: -len(expected)]
            rep.check("instruction", before.endswith("\n\n"),
                      "the mandated sentence must be preceded by a blank line")
        trailing = len(text) - len(text.rstrip("\n"))
        rep.check("instruction", trailing <= 1,
                  f"at most one trailing newline allowed, found {trailing}")

    for art in artifacts:
        rep.check("instruction", art in text,
                  f"declared artifact {art} is never named in instruction.md")

    rel_hits = re.findall(r"(?<![\w/.])(?:\./)?(?:output|result|answer)\w*\.\w+", text)
    if rel_hits and not allow_placeholders:
        rep.warn("instruction",
                 f"possible relative output path(s): {sorted(set(rel_hits))} "
                 "-- the instruction must use absolute paths")


def check_leakage(task: Path, rep: Report) -> None:
    """Nothing in environment/ may reference the solution or the tests."""
    env_dir = task / "environment"
    if not env_dir.is_dir():
        return
    code_like = {".sh", ".py", ".bash"}
    for path in env_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            # Comments in a Dockerfile can legitimately mention tests/; only
            # real instructions constitute a leak.
            if path.name == "Dockerfile" or path.suffix in code_like:
                text = code_of(path)
            else:
                text = read(path)
        except Exception:
            continue
        for needle in ("solution/", "/tests/", "tests/", "ground_truth"):
            if needle in text:
                rep.fail(
                    "leakage",
                    f"environment/{path.relative_to(env_dir)} references "
                    f"{needle!r} -- the agent can read anything in this image",
                )
                break
        else:
            rep.ok("leakage")


def check_forbidden(task: Path, rep: Report) -> None:
    for path in task.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = read(path)
        except Exception:
            continue
        rel = path.relative_to(task)
        # Canary markers are themselves comments, so scan the raw text.
        rep.check("forbidden", "harbor-canary" not in text,
                  f"{rel}: eval-set canary marker is not allowed")
        if path.name == "Dockerfile":
            rep.check("forbidden", "FROM --platform=" not in code_of(path),
                      f"{rel}: FROM --platform= pins are not allowed")


def check_compose(task: Path, rep: Report) -> None:
    compose = task / "environment/docker-compose.yaml"
    if not compose.is_file():
        return
    text = read(compose)
    rep.check("compose", not re.search(r"^\s*volumes\s*:", text, re.M),
              "docker-compose.yaml must not declare volumes of any kind")


def check_contract(rep: Report) -> None:
    """Warn while the submission dataset's own guide is not vendored.

    This repo submits under the **Scientific computing** dataset, whose guide
    advertises "a stricter, science-specific bundle contract". Only the General
    variant has been vendored, so rules this checker enforces may be too loose
    -- or simply wrong -- for the dataset the work is actually filed under.

    A warning, not a failure: it must not block building and validating. The
    hard stop lives in tools/package.sh, since packaging is what produces a
    submission.
    """
    docs = Path(__file__).resolve().parent.parent / "docs"
    if not (docs / "kepler-instructions-scientific-computing.md").is_file():
        rep.warn(
            "contract",
            "the Scientific computing bundle contract is not vendored in docs/; "
            "this checker encodes the General dataset's rules, which are known "
            "to be laxer. Do not submit until it is in and these rules are "
            "re-checked against it (see CLAUDE.md, 'Open: bundle contract')",
        )


def check_placeholders(task: Path, rep: Report) -> None:
    markers = ("TODO", "NotImplementedError", "TODO-slug")
    for path in task.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = read(path)
        except Exception:
            continue
        hit = next((m for m in markers if m in text), None)
        rep.check("placeholders", hit is None,
                  f"{path.relative_to(task)} still contains {hit!r}")


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("task_dir", type=Path)
    ap.add_argument("--allow-placeholders", action="store_true",
                    help="skip the unfilled-template checks (used for _template/)")
    args = ap.parse_args()

    task = args.task_dir.resolve()
    if not task.is_dir():
        print(f"error: {task} is not a directory", file=sys.stderr)
        return 2

    rep = Report()
    check_layout(task, rep)

    cfg: dict = {}
    toml_path = task / "task.toml"
    if toml_path.is_file():
        try:
            cfg = tomllib.loads(read(toml_path))
        except tomllib.TOMLDecodeError as exc:
            rep.fail("task.toml", f"does not parse: {exc}")

    artifacts = [a for a in cfg.get("artifacts", []) if isinstance(a, str)]
    if not artifacts and cfg:
        rep.warn("task.toml", "`artifacts` is empty -- the verifier will see "
                              "nothing the agent produced")

    if cfg:
        check_task_toml(task, cfg, rep, args.allow_placeholders)
        check_metadata(cfg, rep, args.allow_placeholders)
        check_resources(task, cfg, rep)
        check_instruction(task, cfg, artifacts, rep, args.allow_placeholders)

    check_pins(task, rep)
    check_apt_hygiene(task, rep)
    check_verifier_image(task, artifacts, rep)
    check_verifier_script(task, rep)
    check_leakage(task, rep)
    check_forbidden(task, rep)
    check_compose(task, rep)
    check_contract(rep)
    if not args.allow_placeholders:
        check_placeholders(task, rep)

    label = task.name
    for w in rep.warnings:
        print(f"  warn  {w}")
    for f in rep.failures:
        print(f"  FAIL  {f}")

    if rep.failures:
        print(f"\n{label}: {len(rep.failures)} failure(s), "
              f"{rep.passed} check(s) passed, {len(rep.warnings)} warning(s)")
        return 1

    print(f"\n{label}: all {rep.passed} checks passed, "
          f"{len(rep.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
