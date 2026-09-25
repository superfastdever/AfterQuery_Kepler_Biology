# Pre-submission report — wetland-recovery-policy

Every check below was run, not inferred. Commands and actual outputs, followed
by the template's §9 checklist and an honest account of what could not be
tested here.

Environment: Linux x86-64, Docker 29.3.1, harbor 0.23.0, Python 3.12 images.
The reference was developed on macOS/ARM64.

---

## Results

### Repo gates

| Check | Result |
| --- | --- |
| `tools/selftest-structure-check.py` | 40 passed, 0 failed |
| `tools/structure-check.py --allow-placeholders _template` | 79 checks, 0 warnings |
| `tools/task-list.py --check` | up to date |
| `bash -n tools/*.sh` | clean |

### Bundle structure

`tools/structure-check.py tasks/2026-09-25/wetland-recovery-policy`

**158 checks passed, 10 failures — every one an owner-supplied value**
(author identity ×4, conflicts of interest, relevant experience, expert time
estimate ×2, the `field` slug, and the placeholder string that flags it). No
structural, leakage, pinning, network, layout or instruction failure.

With those ten filled on a validation copy: **166–170 checks pass, 0 failures.**

### Harbor, on the real harness

| Run | Result |
| --- | --- |
| Oracle | reward **1**, 5 independent runs |
| Nop | reward **0**, 5 independent runs |

**Determinism:** all five oracle runs produced byte-identical artifacts.

```
posterior=4272c7be42fd  policy=90fe10965d5d  audit=511b9f445fcb
5 oracle runs, 1 distinct artifact set -> DETERMINISTIC
```

**Cross-platform:** worst risk 0.9019740026356561 on Linux/x86-64 against
0.9019740026356562 from the macOS/ARM64 reference — about one ULP, ten orders
of magnitude inside the 1e-6 gate.

### Verifier

Built from `tests/` and run with `--network none` against real oracle
artifacts, matching the `no-network` declaration in `task.toml`:

- reward **1**
- CTRF report written to `/logs/verifier/ctrf.json`, 6 entries, 0 failed
- runtime 0.09 s

Note for reviewers: pytest reports **10** tests, CTRF reports **6**.
`pytest-json-ctrf==0.3.5` collapses each parametrized test into a single entry
(two parametrized tests × 3 cases + four plain tests). Not a discrepancy in the
suite.

### Mutation suite

**19/19**, re-run after `authoring/` was reorganised, including the two
acceptances (the reference artifacts, and a *different* feasible policy inside
the 1e-5 optimality tolerance) and the three wrong-model negative controls that
emit internally consistent artifacts.

### Ablation ladder

`run_ablations.py` re-run from scratch: output **byte-identical** to the
committed `ablation.json`, so the README's numbers are reproducible rather than
transcribed.

### Anti-cheat at the harness level

The mutation suite proves the *checker* rejects bad artifacts; the nop run
proves *missing* artifacts score 0. Neither proves a cheating **agent** fails.
Three cheating `solve.sh` variants were run as the agent through harbor:

| Attempt | What it does | Reward |
| --- | --- | --- |
| `cheat_constants.sh` | Schema-shaped JSON, invented probabilities, correct-looking headline risks | **0** |
| `cheat_degenerate.sh` | `{}`, `{}`, `{"roots": []}` — parseable but empty | **0** |
| `cheat_malformed.sh` | Truncated JSON, as an interrupted run would leave | **0** |

Sources in `authoring/evidence/cheat/`.

### Leak audit, on the built agent image

`/app` contains exactly:

```
/app/input/model.json  /app/input/archive.json
/app/input/output_schema.json  /app/input/protocol.md
```

Absent from the whole filesystem and from every layer: reference arrays,
`reference.json`, oracle artifacts, `generation_record.json`, the generator
scripts, `validation_report.md`, the checker, the mutation suite, `solve.sh`,
`run_oracle.py`, and the seed `20260925`.

One finding worth recording because it looked like a leak and was not: the
image carries **1,790 `.pyc` files, all inside `/usr/local/lib/python*`** —
python:3.12-slim's own stdlib. **Zero** outside the Python install, and none of
this task's modules compiled. Author bytecode has twice had to be cleaned from
`authoring/` after container runs that mount the tree, so this is checked
rather than assumed.

The string `M4` does appear in `/app/input/model.json`. It is a hypothesis
label in the public model, not the answer; which hypothesis generated the
archive is only in `authoring/provenance/generation_record.json`.

### Packaging dry run

Archive built with `package.sh`'s exclusion list from a validation copy:

- **264 KB**, against the 250 MB limit
- 53 files; all six required files at the **top level**, not nested
- `task-meta.json`, `__pycache__`, `.DS_Store`, `.pyc` all absent
- top level exactly: `task.toml`, `instruction.md`, `README.md`,
  `environment/`, `solution/`, `tests/`, `authoring/`

The zip was deleted afterwards. **No real zip exists yet** — `package.sh` gates
on the structure check, which fails on the ten owner-supplied values.

---

## Template §9 checklist

| Item | Status |
| --- | --- |
| Oracle 3/3 reward 1, nop 3/3 reward 0 | **pass** — 5/5 and 5/5 |
| Reference passes ≥30 regenerated seeds | **not applicable by design** — single frozen, hash-pinned instance; see below |
| Independent implementation passes the same set | **pass** — forward path-risk vs backward recursion, agreement 6.66e-16 |
| Each ablation rung fails as the ladder says | **pass** — 7 routes, each failing the predicted gate |
| No number in `tests/` appears in `environment/` | **pass** — leak audit above |
| Every grading-relevant convention derivable or stated | **pass** — `protocol.md` and `output_schema.json` are agent-visible; strict-JSON added to the instruction |
| Instruction gives no method, only outcome | **pass** — scanned for solver, method and answer terms |
| `harbor check -r rubrics/task-implementation.toml` clean | **cannot run** — rubric file not in the package |
| ≥3 agent trials, `harbor analyze` read | **cannot run** — needs model credentials absent here |
| Every failed trial diagnosed | **cannot run** — follows from the above |
| Expert-hours estimate defensible | **blocked** — owner-supplied and unset |

---

## Blocking submission

**1. Ten owner-supplied values.** `package.sh` refuses to write a zip while the
structure check fails. The eight fields are listed in
`authoring/owner-fields.md`. This is mechanical, not editorial: no zip can
exist until they are filled.

**2. Two unresolved spec conflicts** (`docs/template-conflicts.md`). Neither is
testable; both would fail the submission if decided wrongly.

- **Canary GUID** — the science template puts one in `instruction.md`; the
  general guidance says the structure check rejects a bundle containing one.
  The bundle omits it.
- **`[task].name` prefix** — template says `terminal-bench-science/`, the
  submit form says `afterquery/`. The bundle uses `afterquery/`.

---

## Difficulty

The protocol was found to name all seven traps the verifier catches, five of
them as explicit instructions not to make the mistake — the template's first
rejection symptom. Five hand-holds were removed and the generative model left
complete. The answer is provably unmoved: six oracle runs across the change
produce one artifact set, the mutation suite still returns 19/19, and the
ablation ladder is byte-identical. See `difficulty-analysis.md`.

## Stated limits

- **The solve band is argued, not measured.** No frontier-agent trial has run.
  Nothing here establishes that the task lands in the required band, and the
  supplied guidance contradicts itself on whether zero solves is acceptable
  (line 137 says "at least 0", line 159 says "at least once… Both fail"). The
  bundle is designed for ≥1, which satisfies both readings.
- **Single instance, not a seed family.** The archive was generated once under
  seed 20260925 and its hash is pinned. Regenerating changes the answer, so the
  template's multi-seed calibration does not apply. What stands in for it:
  786 transition rows against a scalar expansion, a three-year likelihood
  against all 32,768 explicit state paths, retention across 1,024 state pairs,
  the robust program against brute force over all 16 policies on an independent
  fixture, and the independent forward implementation. This is a deliberate
  departure from the template and a reviewer may disagree with it.
- **No held-out instances.** With one instance, anti-cheat rests on the answer
  being unguessable — a 32-entry policy table plus ten audit roots of branch
  masses and joint losses, all graded against sealed arrays — rather than on
  re-running the agent's work elsewhere.
- **`instruction.md` authorship.** The file is the AI-assisted draft with three
  technical corrections applied; 5 of 7 paragraphs are byte-identical to that
  draft (93.5% word-level similarity). The owner has accepted it in this state.
  Recorded because Kepler screens this file and rejects flagged submissions.
