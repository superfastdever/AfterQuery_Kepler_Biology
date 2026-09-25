# wetland-recovery-policy

Six-year restoration and survey policy for a four-patch wetland network, chosen
from a monitoring archive that retained only networks passing an early
detection screen.

Life Sciences / Ecology & Evolutionary Biology. Subfield: metapopulation
ecology and conservation decision analysis.

---

## Difficulty

> The protocol originally named all seven traps the verifier catches, five as
> explicit "do not do X" instructions — the template's first rejection symptom.
> Five hand-holds were removed while the generative model was left complete.
> See `authoring/evidence/difficulty-analysis.md`; the answer, verifier and
> gates are provably unchanged.

Four scientific requirements hold simultaneously, and each has a shortcut that
a careful generalist would take without noticing. What makes the task hard is
not any one of them; it is that all four must be got right together, and three
of the four shortcuts produce an answer that looks *better* than the truth.

**The archive is not a random sample.** Networks entered it only by passing an
early detection screen, so each retained record's likelihood needs dividing by
that hypothesis's retention probability. An agent that fits occupancy the
standard way gets posterior hypothesis weights wrong by L1 0.454 — and its
*policy* can still be right, so nothing downstream reveals the error.

**Colonization couples the patches.** A source population must survive the
intervening season before it can supply propagules, so destination occupancies
are dependent once the surviving set is integrated out. Multiplying four
marginal occupancy probabilities is the natural move and is wrong.

**The failure event is path-dependent.** Two consecutive empty censuses
anywhere in years 0–6, not emptiness at the end. A later recolonization does
not undo an earlier collapse. Scoring the final census instead makes the
network look far healthier than it is.

**The manager never learns the scenario.** One observation-to-action table must
serve all three futures. Optimizing per scenario, or taking the worst case
separately inside each survey branch, both yield policies that require
information the manager does not have.

### The plausible wrong routes, and what they produce

| Route | What the agent sees | Why it is wrong |
| --- | --- | --- |
| Worst case inside each survey branch | A confident "robust" policy, risk 0.902248 | Minimises a per-branch worst case, which no single scenario realises |
| Scenario-specific optimization | Risk 0.901724, *better* than the true optimum | Needs the scenario disclosed; not implementable |
| Terminal emptiness | Risk 0.799525, dramatically better | Scores the wrong event |
| Factorized destination occupancy | Risk 0.859104, better | Discards dependence induced by uncertain survival |
| Standard occupancy fit | Correct-looking policy | Posterior wrong by L1 0.454 |

Three of these look like *good news*. That is the trap: the agent has no
internal signal that it has gone wrong.

---

## Reference solution

Choices, not steps. Other valid strategies exist and the verifier requires none
of them.

The reference builds the exact finite process rather than approximating: 32
ecological states per hypothesis, hydrology crossed with a four-bit occupancy
mask. It integrates the shared per-visit weather **outside** the product over
patches, and marginalizes the surviving-source subset **before** treating the
next census as a distribution — the two places where an independence assumption
would be tempting and wrong.

For the archive it computes each hypothesis's retention probability and divides
each retained record's likelihood by it, then forms the joint posterior over
hypothesis and current state.

For the forecast it augments the ecological state with a three-valued record of
whether the last census was empty and whether collapse has already happened.
That flag is absorbing, but the ecological state keeps evolving underneath it,
which matters for branch probabilities on already-failed paths.

It then enumerates the feasible second-stage additions under the budget for
each of the ten initial choices, computes the joint probability of each
observation branch together with collapse by year six, and solves a small
binary minimax program: one addition per observation code, worst scenario risk
minimized, the same table under all three futures. Loss coefficients are scaled
by 1e6 so the solver's feasibility tolerance is small on the probability scale,
and the selected table is re-evaluated independently and compared against the
solver's own dual bound rather than trusting a success status.

Result: restore Cedar (mask 4), reserve the intensive survey, three distinct
follow-up actions, worst-scenario collapse probability **0.9019740026**. This
is a high-risk population under constrained interventions — the best allowed
policy, not a claim that restoration makes the network safe.

---

## Verification

Gates are those in `tests/checker.py`, which is byte-identical (SHA-256
verified) to the author's validated `check_outputs.py`.

| Gate | Threshold | Reference worst case | Independent implementation worst case | Nearest wrong route | Why the threshold sits there |
| --- | --- | --- | --- | --- | --- |
| Posterior / retention agreement | abs 1e-6 | 0.0 | 6.66e-16 | factorized occupancy, 3.22e-02 (32,164× the gate) | Double-precision contraction noise is ~1e-15; 1e-6 is nine orders above it and five below the nearest error |
| Audit branch and joint-loss agreement | abs 1e-6 | 0.0 | 6.66e-16 | terminal emptiness, 9.22e-02 (92,246× the gate) | Same basis; the audit is the gate that catches optimistic wrong models |
| Policy risk vs independent evaluation | abs 1e-6 | 0.0 | 6.66e-16 | — | Recomputed from sealed arrays, so agent-reported risk is never trusted |
| Worst risk above optimum | abs 1e-5 | 0.0 | — | worst-case-per-branch, 2.74e-04 (27.4× the gate) | Wide enough to admit alternative optima, 27× below the nearest wrong route |

**Margin.** The template's rule is that a correct route within 1.5× of a gate
sits inside method noise. The nearest *correct* result to any gate is the
independent implementation at 6.66e-16 against 1e-6 — about **1.5 × 10⁹ times
inside**. The nearest *wrong* route is 27.4× outside. No gate is inside method
noise on either side.

**Cross-platform.** The reference was developed on macOS/ARM64. Re-running the
oracle on Linux/x86-64 under harbor reproduces the worst risk to about one ULP
(0.9019740026356561 vs 0.9019740026356562), which is ten orders of magnitude
inside the 1e-6 gate.

**Calibration set.** One frozen instance, not multiple seeds — see *Missing
evidence*.

**Harness runs.** Harbor oracle 3/3 at reward 1 and nop 3/3 at reward 0, with
the three artifacts byte-identical across runs.

**Independent implementation.** `authoring/source/validate.py` re-derives the
result by a different route: a forward distribution over ecological state,
previous-empty flag and collapse flag, against the reference's backward
augmented-state recursion. Agreement 6.66e-16. It also checks 786 ecological
rows against a scalar expansion (3.33e-16), a three-year likelihood against all
32,768 explicit state paths (5.64e-18), and the robust program against brute
force over all 16 policies on an independent fixture (exactly 0.0).

---

## Ablation ladder

Produced by `authoring/evidence/run_ablations.py`, which builds each route's
complete artifact set and runs the real sealed checker over it. Raw output in
`authoring/evidence/ablation.json`.

Optimum 0.9019740026. Gates: numeric 1e-6, optimality 1e-5.

| Route | Worst risk | Gap to optimum | Posterior err | Audit err | Gates failed | Passes |
| --- | ---: | ---: | ---: | ---: | --- | :-: |
| **Full reference** | 0.901974003 | 0.00e+00 | 0.00e+00 | 0.00e+00 | none | **yes** |
| Skip retention correction | 0.901974003 | 0.00e+00 | 1.75e-01 | 0.00e+00 | posterior | no |
| Per-patch survey weather | 0.904113893 | +2.14e-03 | 1.88e-02 | 2.20e-03 | posterior, audit, optimality | no |
| Factorized destination occupancy | 0.859104210 | −4.29e-02 | 3.22e-02 | 3.70e-02 | posterior, audit | no |
| Terminal emptiness | 0.799525386 | −1.02e-01 | 1.78e-15 | 9.22e-02 | audit | no |
| Worst case within each branch | 0.902247973 | +2.74e-04 | 0.00e+00 | 0.00e+00 | optimality | no |
| Scenario-specific (clairvoyant) | 0.901723573 | −2.50e-04 | n/a | n/a | not submittable | no |
| Naive: survey then do nothing | 0.914286589 | +1.23e-02 | 0.00e+00 | 0.00e+00 | optimality | no |

Three things this table is meant to show.

**Negative gaps are the point.** Factorized occupancy, terminal emptiness and
the clairvoyant bound all report risks *better* than the true optimum. An agent
on those routes believes it has done well. None is caught by the optimality
gate — they are caught by the posterior and audit gates, which is precisely why
those artifacts are required rather than just the policy.

**Skipping the retention correction fails on exactly one gate.** Its policy is
the correct one and its audit is exact; only the posterior moves, by 175,170×
the gate. The posterior artifact exists to catch this and nothing else does.

**The non-anticipativity constraint is worth 2.50e-04**, twenty-five times the
optimality tolerance. Requiring one action table across undisclosed scenarios
is a real constraint, not a formality.

---

## Missing evidence

Stated plainly rather than implied.

- **No frontier-agent trials.** The template asks for at least three, with
  `harbor analyze` findings. Running an agent needs model credentials this
  container does not have. **The solve band is argued, not measured** — treat
  any claim about it as a design argument until the platform probe runs.
- **`harbor check -r rubrics/task-implementation.toml` not run.** The rubric
  file is not in the supplied package.
- **No multi-seed calibration.** The template asks for the reference to pass on
  ~30 regenerated seeds. This task grades **one frozen instance**: the archive
  was generated once under seed 20260925, its hash is pinned in
  `authoring/design/manifest.json`, and regenerating it would change the
  answer. The design chose a fixed instance over a seed family. What substitutes
  for multi-seed evidence here is the independent implementation and the
  exhaustive cross-checks (32,768 explicit paths, 1,024 state pairs, 786
  transition rows, brute force over all 16 policies on a fixture). That is a
  deliberate difference from the template and a reviewer may disagree with it.
- **No held-out instances.** Template §7 prefers re-running the agent's work on
  held-out cases so a hardcoded answer scores 0. With one instance, the
  anti-cheat rests instead on the answer being unguessable: an exact 32-entry
  policy table plus ten audit roots of branch masses and joint losses, all
  checked against sealed arrays.
- **`expert_time_estimate_hours` not set.** The template warns it is checked
  against observed agent solve time, and no solve time has been observed.
- **`instruction.md` authorship.** The current file is the AI-assisted draft
  with three targeted technical corrections applied; 5 of 7 paragraphs remain
  byte-identical to the draft (93.5% word-level similarity). The owner has
  accepted it in this state. Recorded here because Kepler screens this file.

---

## Reproducing

```bash
tools/structure-check.py tasks/2026-09-25/wetland-recovery-policy
tools/validate.sh tasks/2026-09-25/wetland-recovery-policy    # oracle 1, nop 0
tools/package.sh wetland-recovery-policy
```

Ablation ladder, inside an image with numpy and scipy:

```bash
python3 authoring/evidence/run_ablations.py <author_dir> <public_dir> out.json
```

`<author_dir>` must contain the `.py` files from `authoring/provenance/` with a
`results/` directory beside them holding `reference.json` and
`reference_arrays.npz`, which is how `check_outputs.py` resolves its ground
truth.
