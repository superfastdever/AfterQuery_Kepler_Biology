# wetland-recovery-policy

Six-year restoration and survey policy for a four-patch wetland network,
chosen from a monitoring archive that retained only networks passing an early
detection screen. The agent must produce a posterior over six ecological
hypotheses and the current network state, a policy mapping every year-3 survey
result to a second-stage restoration, and an audit of counterfactual branch
losses across all ten initial choices.

Life Sciences / Ecology & Evolutionary Biology, subfield metapopulation ecology
and conservation decision analysis.

## Why it is hard

Four requirements hold at once, and each has a plausible shortcut that silently
changes the answer:

| Shortcut | Effect if taken |
| --- | --- |
| Treat the archive as a random sample | posterior weights shift by L1 ≈ 0.454 |
| Multiply marginal destination occupancies | ignores dependence induced by uncertain surviving sources |
| Score emptiness at the final census | risk moves by up to ≈ 0.181 |
| Optimize per scenario | unattainable bound ≈ 0.00025 better, against a 1e-5 tolerance |

Each produces a complete, internally consistent, confidently wrong answer.

## Data

The four files in `environment/data/` are copied to `/app/input/` and are the
whole study specification. They are frozen; `authoring/design/manifest.json`
pins their SHA-256, verified on import.

The generator, its seed, the true hypothesis and every precomputed result live
in `authoring/`, which is never mounted into a container.

## Verification

`tests/checker.py` is a byte-identical copy of the author's validated
`check_outputs.py`, so the graded contract cannot drift from what the mutation
suite was run against. `tests/test_outputs.py` wraps it in pytest; the lighter
tests around it only make the CTRF report say which part of the contract broke.

Grading recomputes the submitted policy's risk from sealed reference arrays in
`tests/results/`, so agent-reported risks and audit coefficients are never the
source of truth. Any policy within 1e-5 of the optimum passes — the reference
answer is not privileged.

## Validated here

- Structure check: 156 checks pass, with owner-supplied metadata filled in.
- Harbor oracle = 1, nop = 0, twice, on the real harness.
- Artifacts byte-identical across both oracle runs.
- Linux/x86-64 reproduces the macOS/ARM64 reference to about 1 ULP: worst risk
  0.9019740026356561 against 0.9019740026356562, far inside the 1e-6 tolerance.
- All 19 author mutation cases still rejected/accepted correctly by the ported
  checker, including the three wrong-model negative controls.
- Agent image audited: `/app` holds only the four public inputs; no reference
  arrays, oracle artifacts, generator, seed or author document anywhere on its
  filesystem or in a discarded layer.
- Verifier: 0.14 s pytest, under 1 s container.

## Outstanding

- `instruction.md` needs the repo owner's substantive authorship and is
  currently missing the mandated closing sentence.
- Owner-supplied metadata in `task.toml` is empty by design.
- The `domain` and `field` slugs must be read off the submit form.
- No frontier-agent difficulty trial has been run; the solve band is argued,
  not measured.

## Rebuilding

```bash
tools/structure-check.py tasks/2026-09-25/wetland-recovery-policy
tools/validate.sh tasks/2026-09-25/wetland-recovery-policy
tools/package.sh wetland-recovery-policy
```
