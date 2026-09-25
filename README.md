# AfterQuery — Project Kepler (Life Sciences)

Tasks authored for [Project Kepler](https://experts.afterquery.com/projects/kepler),
a benchmark of hard, real computer work that current AI agents cannot do yet.

Each task is a self-contained [harbor](https://harborframework.com/docs/tasks)
bundle: a written brief, a containerized environment, a reference solution, and
a sealed verifier that scores an attempt 0 or 1. Tasks are filed under the
**Life Sciences** domain, with a `field` and a free-text `subfield`.

Read `CLAUDE.md` before contributing — it carries the rules that govern this
repo, including who writes `instruction.md` and which fields are in scope.

## Layout

| Path | Purpose |
| --- | --- |
| `docs/kepler-instructions.md` | Platform guidance, vendored verbatim. Defines workflow, bundle structure and validation — not subject scope. **Do not edit.** |
| `docs/authoring-checklist.md` | Gate-by-gate checklist to work through before submitting. |
| `docs/local-validation.md` | Running the gates locally, and sandbox quirks that get in the way. |
| `docs/lessons-learned.md` | Failure modes already used, and feedback from past reviews. |
| `task_list.md` | **Index of every task**, ordered by creation time. Generated — do not hand-edit. |
| `_template/` | The skeleton copied for each new task. |
| `tasks/<date>/<slug>/` | One self-contained bundle per task, grouped by creation date. Zips independently. |
| `tools/` | Scaffolding, local gates, packaging, indexing. |
| `build/` | Generated zips and harbor job output. Gitignored. |

## Authoring a task

```bash
tools/new-task.sh <slug>                      # scaffold tasks/<today>/<slug>/
tools/structure-check.py tasks/<date>/<slug>  # Kepler's submit-time gates, locally
tools/validate.sh tasks/<date>/<slug>         # oracle scores 1, nop scores 0
tools/package.sh <slug>                       # build/<slug>.zip, ready to submit
```

Slugs are lowercase and at most three hyphen-separated words, unique across all
date folders. The directory name, `[task].name` and the name submitted on the
platform must all agree.

Tasks are grouped by creation date under `tasks/YYYY-MM-DD/`. The index at
[`task_list.md`](task_list.md) is regenerated from that tree by
`tools/task-list.py`, so it always matches what is on disk.

Build in this order — it is not arbitrary:

1. **Decide the failure mode first.** Write down what specifically the agent
   will get wrong: an invariant it will not preserve, a race it cannot see, a
   rule it has to infer rather than read. Check `docs/lessons-learned.md` that
   it differs from earlier tasks. A task earns its place by breaking models in
   a way the rest of the set does not.
2. **Environment**, with input data vendored into the image.
3. **Verifier, before the solution.** Writing the tests first forces you to
   define what correct means, rather than defining it as whatever your solution
   happened to produce.
4. **Reference solution**, until the oracle scores 1.
5. **Try to cheat it.** See `_template/authoring/NOTES.md`. If the laziest attempt
   passes, the verifier is wrong.
6. **Metadata**, then `instruction.md`.

## The two gates that decide acceptance

**Structure.** Checked the instant you submit; the pipeline never starts if it
fails. `tools/structure-check.py` replicates these locally — required files,
slug rules, dependency pinning, apt hygiene, resource sizes, verifier
isolation, the mandated instruction suffix, ground-truth leakage, canary and
platform-pin bans. Its own negative tests live in
`tools/selftest-structure-check.py`.

**Difficulty.** Eight independent frontier-agent attempts at the full time
budget. The task must be solved **at least once and at most seven times**.
Never solved counts as unsolvable as specified and fails just as surely as
solved every time.

## Non-negotiables

- **Life Sciences only**, and not every field within it. Ecology & Evolutionary
  Biology and Neuroscience & Cognitive Science are the focus; Medicine & Health
  Sciences occasionally; Biology & Biotechnology never. See `CLAUDE.md`.
- **`instruction.md` is written by the repo owner**, not generated. Kepler runs
  an AI check on it and rejects flagged submissions. See `CLAUDE.md`.
- **The internet stays open.** Obscurity is not difficulty, and a solution
  findable online will be found.
- **Ground truth never enters `environment/`.** Anything in that image is
  visible to the agent.
