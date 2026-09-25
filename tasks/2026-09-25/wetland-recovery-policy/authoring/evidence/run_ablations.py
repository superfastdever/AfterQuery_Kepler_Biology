"""Quantitative ablation ladder.

For each route -- the full reference, each individually skipped step, the
plausible-but-wrong robust policies, and a naive baseline -- this produces the
complete artifact set that route would submit, runs the *real* sealed checker
over it, and records what each grading gate actually does.

The point is to replace "this route fails" with numbers: how far outside
tolerance, on which gate, and by how much. A route that fails only just is a
gate sitting inside method noise and has to be widened or regraded.

Run inside an image carrying numpy and scipy, with the author tree mounted:

    python3 run_ablations.py <author_dir> <public_dir> <out.json>

<author_dir> holds reference.py, check_outputs.py, export_outputs.py and
results/{reference.json,reference_arrays.npz}.
"""

import json
import sys
import tempfile
from pathlib import Path

import numpy as np

AUTHOR = Path(sys.argv[1]).resolve()
PUBLIC = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
sys.path.insert(0, str(AUTHOR))

from reference import Model, run, dot, BITS          # noqa: E402
from export_outputs import format_outputs            # noqa: E402
from check_outputs import evaluate                   # noqa: E402

SCEN = ["early", "late", "persistent"]
TRUTH = AUTHOR / "results"

gold = json.loads((TRUTH / "reference.json").read_text())
arrays = dict(np.load(TRUTH / "reference_arrays.npz", allow_pickle=False))
best = gold["best"]
BEST_KEY = best["id"]
OPTIMUM = best["worst_risk"]

config = json.loads((PUBLIC / "model.json").read_text())
archive = json.loads((PUBLIC / "archive.json").read_text())
base_model = Model(config)

# Gate tolerances, taken from check_outputs.py rather than restated by hand.
G_NUMERIC = 1e-6     # posterior / branch / loss agreement
G_OPT = 1e-5         # worst risk above the optimum


def gates(outputs):
    """Run the real checker, plus the numeric distances behind each gate."""
    post = outputs["posterior.json"]
    pol = outputs["policy.json"]
    aud = outputs["audit.json"]

    g_post = max(
        np.max(np.abs(np.array(post["hypothesis_weights"]) - gold["hypothesis_weights"])),
        np.max(np.abs(np.array(post["selection_probability"]) - gold["selection_probability"])),
        np.max(np.abs(np.array(post["focal_joint"]) - arrays["focal_joint"])),
    )

    g_audit = 0.0
    for root in aud["roots"]:
        k = f"{root['initial_restored_mask']}-{root['survey']}"
        for i, s in enumerate(SCEN):
            sc = root["scenarios"][s]
            g_audit = max(
                g_audit,
                np.max(np.abs(np.array(sc["branch_probability"]) - arrays[k + "-mass"][i])),
                np.max(np.abs(np.array(sc["joint_collapse"]) - arrays[k + "-loss"][i])),
            )

    worst = float(pol["worst_risk"])

    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for name, data in outputs.items():
            (d / name).write_text(json.dumps(data, allow_nan=False))
        try:
            evaluate(d, TRUTH)
            verdict, reason = "ACCEPT", ""
        except Exception as exc:                        # noqa: BLE001
            verdict, reason = "REJECT", f"{type(exc).__name__}: {exc}"

    return {
        "posterior_max_abs": float(g_post),
        "audit_max_abs": float(g_audit),
        "worst_risk": worst,
        "optimality_gap": float(worst - OPTIMUM),
        "gate_posterior": "pass" if g_post <= G_NUMERIC else "FAIL",
        "gate_audit": "pass" if g_audit <= G_NUMERIC else "FAIL",
        "gate_optimality": "pass" if worst - OPTIMUM <= G_OPT else "FAIL",
        "verdict": verdict,
        "reason": reason,
    }


def policy_from_indices(indices):
    """Correct model and audit, but a different second-stage table."""
    outputs = format_outputs(gold, arrays)
    losses = arrays[BEST_KEY + "-loss"]
    risk = losses[:, np.arange(32), indices].sum(axis=1)
    outputs["policy.json"]["second_stage"] = [
        {"observation_code": o, "added_mask": best["additions"][int(indices[o])]}
        for o in range(32)
    ]
    outputs["policy.json"]["scenario_risk"] = dict(zip(SCEN, risk.tolist()))
    outputs["policy.json"]["worst_risk"] = float(risk.max())
    return outputs


routes = {}

# --- 1. the full reference ---------------------------------------------------
routes["full reference"] = gates(format_outputs(gold, arrays))

# --- 2. wrong models: every artifact internally consistent, science wrong ----
class IndependentWeather(Model):
    """Integrates the shared per-visit weather separately for each patch."""
    def emission(self, m, visits, water=None, intensive=False):
        out = super().emission(m, [], water, intensive)
        for visit in visits:
            for i, y in enumerate(visit):
                one = [None] * 4
                one[i] = y
                out *= super().emission(m, [one], None, intensive)
        return out


class IndependentDestinations(Model):
    """Keeps the marginal occupancies but drops their dependence."""
    def ecological(self, m, restored, h, forecast_shift=(0., 0., 0., 0.)):
        original = super().ecological(m, restored, h, forecast_shift)
        marg = dot(original, BITS)
        return np.prod(
            np.where(BITS[None, :, :], marg[:, None, :], 1 - marg[:, None, :]), axis=2
        )


class FinalCensusOnly(Model):
    """Scores emptiness at the final census instead of sustained collapse."""
    def coefficients(self, weights, beliefs, restored, survey, terminal_only=False):
        return super().coefficients(weights, beliefs, restored, survey, terminal_only=True)


for label, cls in [
    ("per-patch survey weather", IndependentWeather),
    ("factorized destination occupancy", IndependentDestinations),
    ("terminal emptiness, not sustained collapse", FinalCensusOnly),
]:
    summary, wrong = run(cls(config), archive)
    routes[label] = gates(format_outputs(summary, wrong))

# --- 3. skipped step: no retention correction --------------------------------
w, beliefs, _, q = base_model.posterior(archive, adjust_selection=False)
no_ret = format_outputs(gold, arrays)
no_ret["posterior.json"]["hypothesis_weights"] = w.tolist()
no_ret["posterior.json"]["selection_probability"] = q.tolist()
no_ret["posterior.json"]["focal_joint"] = (w[:, None] * beliefs).tolist()
routes["no archive retention correction"] = gates(no_ret)
routes["no archive retention correction"]["posterior_L1"] = float(
    np.abs(w - np.array(gold["hypothesis_weights"])).sum()
)

# --- 4. wrong robust policies, correct model ---------------------------------
losses = arrays[BEST_KEY + "-loss"]

# Worst case taken separately inside each survey branch.
branchwise = losses.max(axis=0).argmin(axis=1)
routes["worst case within each branch"] = gates(policy_from_indices(branchwise))

# One action table per scenario: not implementable, so a lower bound only.
clair = [float(losses[k].min(axis=1).sum()) for k in range(3)]
routes["scenario-specific (clairvoyant)"] = {
    "worst_risk": max(clair),
    "optimality_gap": max(clair) - OPTIMUM,
    "gate_posterior": "n/a",
    "gate_audit": "n/a",
    "gate_optimality": "n/a",
    "verdict": "NOT SUBMITTABLE",
    "reason": "requires one action table per scenario; the manager never learns the scenario",
    "per_scenario_risk": clair,
}

# --- 4b. correct policy, solver trusted, no certificate derived --------------
for label, mix in [("solver answer, no certificate", None),
                   ("certificate guessed as one scenario", [1.0, 0.0, 0.0]),
                   ("certificate guessed as uniform", [1/3, 1/3, 1/3])]:
    outputs = format_outputs(gold, arrays)
    if mix is None:
        outputs["policy.json"].pop("scenario_weights", None)
    else:
        outputs["policy.json"]["scenario_weights"] = mix
    routes[label] = gates(outputs)

# --- 5. naive baseline: survey, then do nothing ------------------------------
zero = np.full(32, best["additions"].index(0))
routes["naive: no second-stage restoration"] = gates(policy_from_indices(zero))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(
    {
        "optimum": OPTIMUM,
        "best_initial_choice": BEST_KEY,
        "gate_tolerances": {"numeric_abs": G_NUMERIC, "optimality_abs": G_OPT},
        "routes": routes,
    },
    indent=2,
) + "\n")

width = max(len(k) for k in routes)
print(f"{'route':<{width}}  {'worst risk':>12}  {'gap':>11}  {'post':>9}  {'audit':>9}  verdict")
for name, r in routes.items():
    print(f"{name:<{width}}  {r['worst_risk']:>12.9f}  {r['optimality_gap']:>11.2e}  "
          f"{r.get('posterior_max_abs', float('nan')):>9.2e}  "
          f"{r.get('audit_max_abs', float('nan')):>9.2e}  {r['verdict']}")
