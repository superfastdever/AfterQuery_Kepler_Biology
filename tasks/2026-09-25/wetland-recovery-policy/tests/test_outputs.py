"""Sealed verifier tests.

The authoritative judgement is `checker.evaluate`, carried over verbatim from
the author's validated `check_outputs.py` so the graded contract cannot drift
from what the 19-case mutation suite was run against. The lighter tests around
it exist only to make the CTRF report say *which* part of the contract broke;
they never widen what passes.

Nothing here imports, executes, or unpickles an agent artifact. Artifacts are
read as untrusted text through `checker.strict_load`, and the trusted arrays
are loaded with `allow_pickle=False`.
"""

import numpy as np
import pytest

import checker
from checker import SCENARIOS, evaluate, probability, strict_load

OUTPUT = checker.Path("/app/output")
TRUTH = checker.Path(__file__).resolve().parent / "results"

ARTIFACTS = ("posterior.json", "policy.json", "audit.json")


@pytest.mark.parametrize("name", ARTIFACTS)
def test_artifact_present(name):
    """Each required artifact exists and is not empty."""
    path = OUTPUT / name
    assert path.is_file(), f"{path} was not produced"
    assert path.stat().st_size > 0, f"{path} is empty"


@pytest.mark.parametrize("name", ARTIFACTS)
def test_artifact_parses(name):
    """Each artifact is strict JSON: no duplicate keys, no NaN or Infinity."""
    strict_load(OUTPUT / name)


def test_posterior_shapes():
    """The posterior arrays have the required shapes and are probabilities."""
    post = strict_load(OUTPUT / "posterior.json")
    weights = probability(post["hypothesis_weights"], (6,))
    probability(post["selection_probability"], (6,))
    joint = probability(post["focal_joint"], (6, 32))
    assert np.isclose(weights.sum(), 1.0, atol=1e-8), "hypothesis weights must sum to 1"
    assert np.isclose(joint.sum(), 1.0, atol=1e-8), "focal joint must sum to 1"


def test_policy_structure():
    """The policy names a legal initial choice and all 32 distinct branches."""
    policy = strict_load(OUTPUT / "policy.json")
    assert type(policy["initial_restored_mask"]) is int
    assert policy["initial_restored_mask"] in (0, 1, 2, 4, 8)
    assert policy["survey"] in ("basic", "intensive")

    branches = policy["second_stage"]
    assert isinstance(branches, list) and len(branches) == 32, "need 32 branches"
    codes = [b["observation_code"] for b in branches]
    assert all(type(c) is int for c in codes), "observation codes must be integers"
    assert sorted(codes) == list(range(32)), "observation codes must be 0..31, each once"

    assert set(policy["scenario_risk"]) == set(SCENARIOS)


def test_audit_roots_complete():
    """The audit covers all ten initial choices exactly once."""
    audit = strict_load(OUTPUT / "audit.json")
    roots = audit["roots"]
    assert isinstance(roots, list) and len(roots) == 10, "need all ten audit roots"
    keys = [f"{r['initial_restored_mask']}-{r['survey']}" for r in roots]
    assert len(set(keys)) == 10, "audit roots must be distinct"


def test_scientific_evaluation():
    """The authoritative check.

    Recomputes the submitted policy's risk from the sealed reference arrays,
    so an agent's own reported risks and audit coefficients are never the
    source of truth. Any admissible policy within the stated optimality
    tolerance passes; the reference policy is not privileged.
    """
    result = evaluate(OUTPUT, TRUTH)
    assert result["reward"] == 1
