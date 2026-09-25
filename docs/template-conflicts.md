# Where the science template and the general guidance disagree

Three specs are now in play. They are not consistent, and two of the conflicts
would fail a submission outright.

| Source | File | Scope |
| --- | --- | --- |
| **Kepler Science Task Template** (updated Sep 16) | `docs/kepler-science-task-template.md` | The owner states this is the right template for all tasks here, and that the work is specific rather than general. Treat it as authoritative. |
| Submit form REQUIRED LAYOUT panel | screenshots | The gate that actually runs at submit. |
| General authoring guidance | `docs/kepler-instructions.md` | Written for the *general* dataset. Least authoritative where the others speak. |

Nothing below has been silently resolved. Where a conflict is unresolved the
bundle keeps the safer option and the gap is recorded.

---

## Hard conflicts — resolve before submitting

### 1. The canary GUID: required, or instantly rejected?

**Science template, §3**, first line of `instruction.md`:

```
<!-- harbor-canary GUID <guid> -->
```

**General guidance, line 135:**

> Do not include eval-set canary markers (the `harbor-canary` GUID lines some
> public tasks carry)… **the structure check rejects a bundle that contains
> one.**

These cannot both hold. One says put it in the instruction; the other says its
presence fails the gate.

**Current state:** omitted, and `tools/structure-check.py` actively rejects it
(`check_forbidden`). Rationale for the safer side: if the template is right and
the canary is merely missing, that is a quality note; if the general guidance
is right and a canary is present, the bundle is rejected before the pipeline
starts. An absent canary also cannot be mistaken for a real one.

**Needs:** the owner to confirm from the platform which applies to the science
dataset. If the template wins, `BANNED`-style canary rejection must come out of
`check_forbidden` and the GUID goes at the top of `instruction.md`.

### 2. The `[task].name` prefix

| Source | Value |
| --- | --- |
| Science template §2 | `terminal-bench-science/<task-name>` |
| Submit form + general guidance | `afterquery/<task-name>` |

**Current state:** `afterquery/wetland-recovery-policy`, because the submit form
states the name must equal what is typed into the form's own task-name field,
and the form is the gate.

**Needs:** confirmation. A wrong prefix is a structure-check failure at submit.

---

## Conflicts that change the instruction, and so change the rewrite

### 3. Thresholds in the instruction

**Science template §3, "What is graded":**

> Name the metrics that gate the result and what they measure. **Do NOT give
> thresholds, verifier formulas, or the scoring algorithm.**

The current draft gives both: risks within **1e-6** of independent evaluation,
worst risk within **1e-5** of the optimum.

This is genuinely two-sided. The general guidance says the opposite — anything
the verifier demands, the instruction must state — and `protocol.md` line 60
already states both tolerances to the agent anyway, so removing them from the
instruction does not hide them.

**Suggested resolution:** name what is graded without repeating the numbers,
and let `protocol.md` carry them. That satisfies the template without hiding a
grading rule, because the protocol is an agent-visible input.

### 4. Instruction structure and length

Template §3 wants five headings — **Context, Inputs, Deliverable, What is
graded, Notes** — and under about 400 words.

The draft uses none of those headings and is **396 words**, so length is fine
but the shape is not. The "Notes" section is for conventions the agent cannot
infer: units, sign conventions, tie-breaks, rounding. The strict-JSON
requirement flagged in `instruction-review.md` §2.1 belongs there.

### 5. `category` / `subcategory`

The submit form requires `category = "Science"` plus a `subcategory`. The
science template's `[metadata]` block has neither — it carries only
`domain` / `field` / `subfield`.

**Current state:** both kept, since the form demands them and an unexpected
extra key is far likelier to be ignored than a missing required one is.

---

## Resolved by the template

### `domain` is no longer a guess

Template §2 enumerates the allowed values:

> `domain = "<life-sciences | physical-sciences | earth-sciences | mathematical-sciences | engineering-sciences>"`

So **`domain = "life-sciences"`**, taken from the spec rather than invented.

`field` is still written as a free placeholder in the template and is not
enumerated, so it stays unresolved. Given `domain` is a hyphenated lowercase
slug, `ecology-evolutionary-biology` is the obvious parallel, but that is an
inference and the form remains the authority.

### Verifier pins confirmed

Template §7: `pytest==8.4.1 pytest-json-ctrf==0.3.5` — matching the submit form
and confirming the choice already made against the general guidance's 9.1.1 /
0.5.2.

### `conflicts_of_interest`

Template §2 shows `"None"` as the value, so a plain declaration of none is the
expected form rather than something elaborate. It is still the owner's to make.

### `schema_version`

Template §2 requires `schema_version = "1.4"`, which the bundle was missing.

---

## Requirements the template adds that the bundle does not yet meet

These are not conflicts, just work.

- **`[task].authors` and `[task].keywords`** are required and absent.
- **`README.md` must have four named sections**: Difficulty, Reference
  solution, Verification, Ablation ladder. The last two are specific: a
  per-gate line giving threshold, reference worst case, independent
  implementation worst case and nearest wrong route; and a ladder showing what
  each graded number becomes when a step is skipped. The design package's
  `validation_report.md` already has the ablation numbers.
- **`authoring/` wants `provenance/` and `evidence/` subdirectories.** The
  bundle currently uses `source/`, `results/`, `oracle_artifacts/`, `design/`.
- **Oracle 3/3 and nop 3/3.** Two of each have been run, not three.
- **An independent implementation** is called "the single strongest piece of
  evidence a task can carry". The design package has one inside
  `validate.py` — a forward path-risk calculation cross-checking the backward
  recursion — but it is not packaged as `authoring/evidence/`.
- **Held-out instances.** Template §7 wants the agent's result checked against
  held-out cases so a hardcoded answer scores 0. This task grades a single
  frozen instance; the anti-cheat rests on the answer being unguessable rather
  than on re-running. Worth a deliberate decision.
- **`harbor check -r rubrics/task-implementation.toml`** and at least three
  agent trials with `harbor analyze` output. Neither is runnable here: the
  rubric file is not in the package, and agent trials need model credentials
  this container does not have.

---

## The repo layout question

Template §1 gives `tasks/<domain>/<field>/<task-name>/`. This repo uses
`tasks/<YYYY-MM-DD>/<slug>/` at the owner's explicit instruction, with a
generated `task_list.md` index.

These need not conflict: the submission is a zip of the *task directory
contents*, so neither the date folder nor a domain/field folder appears inside
it. The template's layout is a repository convention, not a bundle
requirement. Kept as-is pending the owner's preference.
