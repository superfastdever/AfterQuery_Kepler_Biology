# Conventions for this repository

Read this before doing any work here. It encodes decisions already made, so they
do not need to be re-litigated each session.

## What this repo is

The home for every AfterQuery **Project Kepler** task authored by the repo
owner. Each task is a self-contained [harbor](https://harborframework.com/docs/tasks)
bundle — instruction, containerized environment, reference solution, sealed
verifier — designed so that frontier AI agents fail at it for legitimate
reasons. Tasks are submitted one zip at a time.

Three specs are vendored, in order of authority. **Do not edit any of them** —
they are kept verbatim so they stay trustworthy.

1. **`docs/kepler-science-task-template.md`** — the Kepler Science Task
   Template. The owner's work is **specific, not general**, so this is the
   template for every task here.
2. **The submit form's REQUIRED LAYOUT panel** (collapsed by default) — the
   gate that actually runs at submit.
3. **`docs/kepler-instructions.md`** — written for the *general* dataset.
   Least authoritative where the other two speak.

They are **not consistent**, and two of the disagreements would fail a
submission outright — the canary GUID and the `[task].name` prefix.
`docs/template-conflicts.md` records every one of them, which side the bundle
currently takes, and why. Read it before changing anything the specs touch, and
never resolve a conflict silently.

It defines the authoring workflow, the bundle structure and the validation
requirements. It does **not** define this repo's subject scope — that is set by
what the owner's account is approved for, in §1 below.

## Hard rules

### 1. Domain scope — Life Sciences only, and not every field

The owner's Kepler application was accepted for **Life Sciences**. The guidance
never repeats this restriction and lists example tasks across many domains;
that silence does **not** widen the scope, and those examples are *format*
references only.

`task.toml` carries the same `domain` and `field` **slugs** as the submit form,
plus a free-text `subfield`. The field is "the one the task's core
computational work belongs to".

| Field | Pool depth | Policy |
| --- | --- | --- |
| Ecology & Evolutionary Biology — phylogenetics, population genetics | Room for more | **Focus** |
| Neuroscience & Cognitive Science — neuroimaging, psychophysics, behavior | Room for more | **Focus** |
| Medicine & Health Sciences — clinical, epidemiology, public health | Balanced | Occasionally |
| Biology & Biotechnology — bioimaging, genomics, synthetic biology | Well stocked | **Never** |

The platform notes "every field is wanted; thin ones most", so the two focus
fields also carry the best acceptance odds. Excluding Biology & Biotechnology
is the **owner's policy, not a platform rule** —
`tools/structure-check.py` enforces it via `BANNED_FIELDS`, which is one line to
relax if that ever changes.

### 2. Authorship — `instruction.md` is written by the human, not by AI

From `docs/kepler-instructions.md`, "Authorship & originality":

> Write the instruction yourself, as a domain expert, in your own words. We run
> an AI check on every instruction file, and flagged submissions are rejected.
> AI assistance elsewhere (environment scaffolding, test data generation) is
> fine. The instruction is the part that must be yours.

| Component | May be AI-assisted |
| --- | --- |
| `instruction.md` | **No** — the repo owner writes and supplies it |
| `[metadata].relevant_experience` | **No** — a factual claim about the owner's career |
| `author_name` / `author_email` / `author_organization` / `author_profile` | **No** — the owner's identity |
| `[metadata].conflicts_of_interest` | **No** — a formal declaration, never generated or guessed |
| `environment/`, `tests/`, `solution/`, `authoring/`, data generation, `tools/` | **Yes** — explicitly permitted |

An AI assistant working in this repo **must not**:

- ghostwrite `instruction.md`, in whole or in part;
- restyle or "humanize" text so it reads as human-written to defeat the AI check;
- invent `relevant_experience`, or any other claim about the owner's background;
- edit or delete the vendored guidance to suppress a rule it finds inconvenient.

What it **may** do: supply a content checklist of what the instruction must
state, then review the owner's draft for *gaps* — an unnamed output path, a
missing constraint, a step-by-step tone the guidance warns against — and correct
outright typos. That is colleague review, not authorship.

The three `*_explanation` metadata fields are read by human reviewers to
calibrate the difficulty and verification claims, so they should reflect the
owner's real reasoning rather than generated filler.

### 3. Originality against the owner's own back catalogue

Each task must be a genuinely new problem, not a re-skin. Swapping domain nouns
around the same scaffold, reference solution and verifier shape is rejected
however thoroughly the surface changed. Before building, state **which specific
agent failure mode** the task targets, and check `docs/lessons-learned.md` that
it differs from the previous tasks.

## Confirm at submit time

The `domain` and `field` values in `task.toml` must match what the submit form
has selected. The form displays names ("Life Sciences", "Ecology & Evolutionary
Biology") while stating that `task.toml` carries **slugs**, so read the exact
string off the form when filling these in rather than inventing one.

`tools/structure-check.py` accepts either spelling — `"Ecology & Evolutionary
Biology"` or `"ecology-evolutionary-biology"` — so it cannot arbitrate this;
the form is the authority. The template ships `TODO-domain-slug` /
`TODO-field-slug` so an unfilled task cannot reach packaging unnoticed.

## Layout

```
task_list.md               generated index of every task — do not hand-edit
docs/                      platform guidance (verbatim), checklists, feedback
_template/                 the skeleton copied to start a new task
tasks/<date>/<slug>/       one self-contained bundle per task
tools/                     validation, scaffolding, packaging, indexing
build/                     generated zips (gitignored)
```

Tasks are grouped by **creation date**, `tasks/YYYY-MM-DD/<slug>/`, so the tree
stays readable as they accumulate. Slugs must be unique across every date
folder — the slug is the submitted task name — and `tools/new-task.sh` refuses
a duplicate.

Nothing in a task directory may depend on anything outside itself: the zip of
that directory's contents is the whole submission.

Inside a task, **nothing may sit at the bundle root** except `task.toml`,
`instruction.md`, `README.md`, and the `environment/`, `solution/`, `tests/`
and `authoring/` directories.

`authoring/` holds generators, seeds, cheat attempts and notes. It is **never
mounted into any container**, which makes it the right home for the script that
produced the data — keeping it out of `environment/`, where the agent could
read it.

### `task-meta.json` and `task_list.md`

Each task carries a `task-meta.json` holding the repo-side facts the platform
bundle has no field for: creation timestamp, status, completion date, a
one-line summary, and the agent failure mode it targets. **It never ships** —
`tools/package.sh` excludes it from the zip.

`task_list.md` at the repo root is the index: a table of every task ordered by
creation time, with per-task summaries below it. It is **generated** by
`tools/task-list.py` from the contents of `tasks/`, never written by hand, so
it cannot drift from reality. `new-task.sh` and `package.sh` refresh it
automatically; run it yourself after editing a `task-meta.json`, and
`tools/task-list.py --check` exits non-zero if it is stale.

Status moves in one direction only:
`building → validated → packaged → submitted → approved / rejected`.

## Workflow

```bash
tools/new-task.sh <slug> [YYYY-MM-DD]    # scaffold tasks/<date>/<slug>/
tools/structure-check.py tasks/<date>/<slug>
tools/validate.sh tasks/<date>/<slug>    # oracle must be 1, nop must be 0
tools/package.sh <slug>                  # build/<slug>.zip, ready to submit
tools/task-list.py                       # regenerate task_list.md
```

`package.sh` takes the bare slug and finds it under whichever date folder holds
it. The date argument to `new-task.sh` defaults to today and exists for
backdating.

Slugs are lowercase and at most three hyphen-separated words. The directory
name, `[task].name` (as `afterquery/<slug>`) and the submitted task name must
all agree.

Run `tools/structure-check.py` before every commit that touches a task, and
`tools/validate.sh` before any submission. A local failure is a guaranteed
pipeline failure, and the pipeline never starts on a bundle that fails the
structure check.

## Git

- Work on the branch the session designates; never push elsewhere without
  explicit permission. No pull request unless the owner asks for one.
- **Commit and push at every meaningful checkpoint.** Sessions may run in
  ephemeral cloud containers where unpushed work is lost when the container is
  reclaimed.

## Traps that cause most rejections

- Ground truth or test data reachable from `environment/` — anything in that
  image is visible to the agent. Grading logic lives only in `tests/`.
- A verifier that checks an exit code, a file's existence, or a string the agent
  can print, rather than the content of the result.
- Installing packages inside `test.sh`. Bake everything into `tests/Dockerfile`.
- Relative paths, or an output path the instruction never names.
- Nondeterministic grading: unseeded randomness, wall-clock dependence,
  float comparison without a tolerance.
- Timeouts left at template values. Time the oracle, then give the agent several
  times that.
- An environment depending on a live web resource. Vendor the data in, or pin an
  immutable source.
