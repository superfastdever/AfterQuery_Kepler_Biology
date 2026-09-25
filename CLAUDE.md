# Conventions for this repository

Read this before doing any work here. It encodes decisions already made, so they
do not need to be re-litigated each session.

## What this repo is

The home for every AfterQuery **Project Kepler** task authored by the repo
owner. Each task is a self-contained [harbor](https://harborframework.com/docs/tasks)
bundle — instruction, containerized environment, reference solution, sealed
verifier — designed so that frontier AI agents fail at it for legitimate
reasons. Tasks are submitted one zip at a time.

Platform guidance is vendored verbatim at
`docs/kepler-instructions-general.md`. **Do not edit that file.** It is kept
unaltered so it stays trustworthy as a reference.

⚠ It is the **General** dataset's guide. This repo submits under **Scientific
computing**, whose contract is stricter and is not yet vendored. See
"Open: bundle contract" below before packaging anything.

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

From `docs/kepler-instructions-general.md`, "Authorship & originality":

> Write the instruction yourself, as a domain expert, in your own words. We run
> an AI check on every instruction file, and flagged submissions are rejected.
> AI assistance elsewhere (environment scaffolding, test data generation) is
> fine. The instruction is the part that must be yours.

| Component | May be AI-assisted |
| --- | --- |
| `instruction.md` | **No** — the repo owner writes and supplies it |
| `[metadata].relevant_experience` | **No** — a factual claim about the owner's career |
| `environment/`, `tests/`, `solution/`, data generation, `tools/` | **Yes** — explicitly permitted |

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

## Open: bundle contract

**Do not package or submit a task until this is closed.**

The submit form's dataset picker is set to **Scientific computing**, described
on the platform as:

> Real research workflows in the natural, mathematical and engineering
> sciences. **A stricter, science-specific bundle contract** — read the science
> section of the instructions before building.

Only the **General** dataset's guide has been vendored. Every rule in
`tools/structure-check.py` is transcribed from that laxer variant, so the
checker passing means less than it appears to. `tools/package.sh` refuses to
build a zip until `docs/kepler-instructions-scientific-computing.md` exists
(override deliberately with `KEPLER_ALLOW_UNKNOWN_CONTRACT=1`).

Three things are still unknown and **must not be guessed**:

1. **The Scientific computing bundle contract** — its science section, and
   whatever it adds beyond the General rules.
2. **The exact `domain` and `field` slug strings.** The submit form shows
   display names ("Life Sciences", "Ecology & Evolutionary Biology");
   `task.toml` needs slugs. The template carries `TODO-domain-slug` /
   `TODO-field-slug` so an unfilled task cannot reach packaging.
3. **The full REQUIRED LAYOUT list.** The submit form truncates it behind a
   collapse chevron: `task.toml · instruction.md · environment/Dockerfile ·
   solution/solve.sh · tests/test.sh · tests/Dockerfile · a…` — at least one
   required item has never been read.

When the contract arrives: vendor it as
`docs/kepler-instructions-scientific-computing.md`, re-check every rule in
`tools/structure-check.py` against it, extend
`tools/selftest-structure-check.py` to cover whatever it adds, and record what
differed in `docs/lessons-learned.md`.

## Layout

```
docs/          platform guidance (verbatim), checklists, accumulated feedback
_template/     the skeleton copied to start a new task — keep it valid
tasks/<slug>/  one self-contained bundle per task; zips independently
tools/         validation, scaffolding and packaging, shared by all tasks
build/         generated zips (gitignored)
```

Nothing in `tasks/<slug>/` may depend on anything outside itself — the zip of
that directory's contents is the whole submission.

## Workflow

```bash
tools/new-task.sh <slug>              # scaffold tasks/<slug>/ from _template
tools/structure-check.py tasks/<slug> # replicate Kepler's submit-time gates
tools/validate.sh tasks/<slug>        # oracle must score 1, nop must score 0
tools/package.sh <slug>               # build/<slug>.zip, ready to submit
```

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
