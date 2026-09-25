# Validation report: wetland recovery policy

Status: local scientific prototype and artifact checker passed. Harbor execution, platform review, and frontier difficulty are untested.

The local environment was macOS on ARM64 with Python 3.12.14, NumPy 2.2.6, and SciPy 1.15.3. The pinned libraries were installed in the project-local `.venv-kepler` environment. Docker and Harbor were not available on the current PATH. No remote model was called to solve this task, and no task was submitted.

## Scientific checks

All 31 numerical checks in `author/validate.py` passed. These include normalized ecological and observation kernels, 786 transition rows compared with a separately written scalar calculation, shared-weather and missing-observation handling, an exact three-year likelihood comparison across 32,768 latent state paths, and a retention probability comparison across 1,024 state pairs. An independent small optimization fixture was solved both by exhaustive enumeration and by the policy optimizer.

The full chosen policy was evaluated twice: once by the reference's backward augmented-state calculation and once by a forward distribution over ecological state, previous empty census, and whether collapse had already occurred. Their scenario risks agree to floating-point precision. All ten initial-choice optimizations were checked against their solver lower bounds. The largest recorded residual among the 31 checks was below 1e-14. This is evidence of local numerical agreement, not a proof that every implementation defect is impossible.

The probability model remained well defined for all hypotheses and restoration masks. Already-collapsed paths stayed failed while their ecological states could still recover. Both survey packages had properly normalized complete observation distributions.

## Artifact checker checks

All 19 checks in `author/test_verifier.py` passed. Two are positive cases: the reference artifacts and a different feasible policy within the advertised optimality tolerance. The other 17 reject invalid submissions.

Rejected cases include an empty output directory; empty JSON objects; strings or booleans substituted for probabilities; NaN; duplicate JSON keys; missing or duplicate observation branches; infeasible restoration; fabricated optimal risks for a no-additional-restoration policy; incomplete counterfactual audits; incorrect joint loss values; omitted archive selection; and conditional probabilities supplied in place of joint losses.

Three complete alternative calculations were also rejected: one integrates survey weather separately for each patch, one discards dependence between destination occupancies while preserving their marginal probabilities, and one optimizes final-census emptiness instead of the specified sustained-collapse event. These are meaningful scientific negative controls, not just malformed-file tests.

The checker uses sealed reference coefficients to evaluate the submitted decisions. It does not trust submitted risk claims, execute submitted code, or grade the exact reference policy string.

## Numerical result and sensitivity to mistakes

| Quantity | Local reference result |
| --- | --- |
| Initial restoration | Cedar, mask 4 |
| Reserved survey | Intensive |
| Worst scenario collapse probability | 0.9019740026356562 |
| Early drought collapse probability | 0.9019740026356562 |
| Late drought collapse probability | 0.9019627898546361 |
| Persistent stress collapse probability | 0.8944488652475052 |
| Distinct follow-up actions in reference policy | 3 |
| Gap to next-best initial choice | About 0.0005906911 |
| Unattainable scenario-aware lower bound | About 0.9017235727 |
| Gap caused by requiring one implementable policy | About 0.0002504299 |
| Posterior L1 change without retention correction | About 0.4537731282 |

Under the same chosen policy, final-census emptiness probabilities are approximately 0.7210523280, 0.8089232532, and 0.7422510888. Those are not the requested collapse probabilities. The distinction is large enough to test substantive ecological reasoning rather than rounding.

The final numerical reference run took approximately 0.38 seconds after imports on this machine. This measures the implemented finite calculation. It excludes image building, startup, derivation, coding, and debugging, and cannot be used as an estimate of expert-solving time.

## Development findings

Local validation caught a solver feasibility-tolerance issue: a nominally successful unscaled solve had a probability discrepancy of approximately 3.64e-7 against independently evaluated decisions. The reference now scales the loss constraints by 1e6 and checks the evaluated objective against the lower bound. The public acceptance tolerances did not need to be weakened.

The original local NumPy BLAS path emitted floating-status warnings despite finite normalized results. The reference now uses explicit NumPy contractions for its small matrices. Independent scalar comparisons validate the resulting probabilities. These are local implementation refinements before any frontier trial; this package has not undergone model-driven task tuning.

The final climate coefficients were chosen during design to make the intended conflict between scenario-specific choices substantive. The final manifest fixes those inputs for subsequent trials.

## What remains for Claude

Build the isolated environment, real executable oracle, and separate pytest/CTRF verifier. Verify package availability, image contents, artifact copying, timeout behavior, and a fail-closed reward file. Run the actual Harbor oracle, nop, and quality checks. Check Linux numerical results against the disclosed tolerances. Test artifact failures through the real harness.

Then run the frontier difficulty probe without changing the instance between its attempts. Inspect the trajectories. Genuine scientific difficulty, underspecification, infrastructure failure, and verifier exploitation must be distinguished. The supplied guide's contradictory wording about zero solves remains unresolved; no local test establishes that policy.

The final instruction also needs the user's substantive authorship under the supplied project rules. Domain and field machine slugs and truthful author metadata must be resolved for submission. There is no missing separate scientific-computing contract.

## Reproduce the local evidence

From the project root, use the project virtual environment to run these scripts in order:

1. `.venv-kepler/bin/python Tasks/01-wetland-recovery/author/reference.py`
2. `.venv-kepler/bin/python Tasks/01-wetland-recovery/author/validate.py`
3. `.venv-kepler/bin/python Tasks/01-wetland-recovery/author/test_verifier.py`

The existing public data is frozen. Do not regenerate it as part of an agent attempt. The generator is retained for author provenance only.

Machine-readable results are `author/results/validation.json`, `author/results/verifier_validation.json`, `author/results/reference.json`, and `author/results/reference_arrays.npz`. Correct artifacts are in `author/oracle_artifacts/`. Keep every one of these files out of the agent image.
