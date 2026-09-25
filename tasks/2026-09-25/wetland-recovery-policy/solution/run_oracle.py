"""Reference solution driver.

Recomputes the whole analysis from the public inputs in /app/input inside the
agent's own container, then writes the three required artifacts. Nothing is
copied from the author's precomputed results: solvability has to be
demonstrated by the calculation actually running here.

`reference.py` sits beside this file and is imported as a module, so its
module-level BASE (which points at the author's tree) is never used.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference import Model, run  # noqa: E402

INPUT = Path("/app/input")
OUTPUT = Path("/app/output")
SCENARIOS = ["early", "late", "persistent"]


def format_outputs(summary, arrays):
    """Shape the reference results into the agent-facing artifact contract.

    Same mapping as the author's export_outputs.format_outputs. Its sibling
    export() is deliberately not reused: that one re-reads the author's stored
    answer instead of recomputing.
    """
    best = summary["best"]
    outputs = {
        "posterior.json": {
            "selection_probability": summary["selection_probability"],
            "hypothesis_weights": summary["hypothesis_weights"],
            "focal_joint": arrays["focal_joint"].tolist(),
        },
        "policy.json": {
            "initial_restored_mask": best["restored"],
            "survey": best["survey"],
            "second_stage": [
                {"observation_code": o, "added_mask": a}
                for o, a in enumerate(best["policy"])
            ],
            "scenario_risk": dict(zip(SCENARIOS, best["risk"])),
            "scenario_weights": best["scenario_weights"],
            "worst_risk": best["worst_risk"],
        },
        "audit.json": {"roots": []},
    }
    for root in summary["roots"]:
        losses = arrays[root["id"] + "-loss"]
        mass = arrays[root["id"] + "-mass"]
        outputs["audit.json"]["roots"].append(
            {
                "initial_restored_mask": root["restored"],
                "survey": root["survey"],
                "added_masks": root["additions"],
                "scenarios": {
                    name: {
                        "branch_probability": mass[k].tolist(),
                        "joint_collapse": losses[k].tolist(),
                    }
                    for k, name in enumerate(SCENARIOS)
                },
            }
        )
    return outputs


def main() -> int:
    started = time.perf_counter()

    model = Model(json.loads((INPUT / "model.json").read_text()))
    archive = json.loads((INPUT / "archive.json").read_text())
    summary, arrays = run(model, archive)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, data in format_outputs(summary, arrays).items():
        # allow_nan=False so a non-finite value fails here rather than
        # producing JSON the verifier would reject.
        (OUTPUT / name).write_text(
            json.dumps(data, indent=2, allow_nan=False) + "\n"
        )

    best = summary["best"]
    print(
        json.dumps(
            {
                "seconds": round(time.perf_counter() - started, 3),
                "initial_restored_mask": best["restored"],
                "survey": best["survey"],
                "worst_risk": best["worst_risk"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
