"""Verifier tests. Baked into the verifier image; the agent never sees this file.

Rules these tests must obey:

* Check the CONTENT of the result, never an exit code, a file's mere existence,
  or a string the agent can print at will.
* Compare against ground truth the agent could not have guessed. Ground truth
  lives here in tests/, never in environment/.
* Be deterministic. No unseeded randomness, no wall-clock dependence, no bare
  float equality -- always compare floats with an explicit tolerance.
* Assume nothing exists. The agent may have written nothing, or garbage.
  A missing or malformed artifact must fail cleanly, not error out ambiguously.
"""

import json
import math
from pathlib import Path

import pytest

# Every path here must match `artifacts` in task.toml AND be named explicitly
# in instruction.md.
OUTPUT_PATH = Path("/app/output.json")

# Ground truth. Keep it in this directory -- it is sealed from the agent.
TRUTH_PATH = Path(__file__).parent / "ground_truth.json"

# Tolerance for float comparison. Tighten to whatever the science actually
# supports; never compare floats exactly.
RTOL = 1e-6


@pytest.fixture(scope="module")
def submission():
    """Load the agent's artifact, failing cleanly if it is absent or malformed."""
    if not OUTPUT_PATH.is_file():
        pytest.fail(f"expected artifact {OUTPUT_PATH} was not produced")
    try:
        text = OUTPUT_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        pytest.fail(f"could not read {OUTPUT_PATH}: {exc}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        pytest.fail(f"{OUTPUT_PATH} is not valid JSON: {exc}")


@pytest.fixture(scope="module")
def truth():
    return json.loads(TRUTH_PATH.read_text(encoding="utf-8"))


def test_schema(submission):
    """The artifact has the shape the instruction demands."""
    # TODO: assert required keys and types. Reject extra leniency -- a vague
    # schema check is how a lazy attempt slips through.
    raise NotImplementedError("write the real schema assertions")


def test_values_match_ground_truth(submission, truth):
    """The numbers are right, within a stated tolerance."""
    # TODO: replace with the real comparison.
    for key, expected in truth.items():
        actual = submission.get(key)
        assert actual is not None, f"missing key: {key}"
        if isinstance(expected, float):
            assert math.isclose(actual, expected, rel_tol=RTOL), (
                f"{key}: expected {expected}, got {actual}"
            )
        else:
            assert actual == expected, f"{key}: expected {expected}, got {actual}"


def test_rejects_the_lazy_attempt(submission):
    """Evidence of real work, not a plausible-looking guess.

    Ask what the laziest passing attempt would be -- constants, a copied input,
    a degenerate answer -- and make this test reject it. The pipeline runs an
    adversarial probe that tries exactly this.
    """
    # TODO: implement.
    raise NotImplementedError("write the anti-cheat assertions")
