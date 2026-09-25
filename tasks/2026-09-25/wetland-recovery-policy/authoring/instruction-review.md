# Review of the draft instruction

The current `instruction.md` is the AI-assisted draft from your design package,
with the mandated closing sentence appended. This is a colleague review of it:
what it must keep, what is missing, and what it must not start saying. The
words are yours to write.

Reviewed against what the verifier actually enforces (`tests/checker.py`),
against `environment/data/protocol.md` and `output_schema.json`, and against
`docs/spec-review.md`.

---

## 1. The single most important thing to preserve

**`/app/output/` appears nowhere except `instruction.md`.**

| File | mentions of `/app/output` |
| --- | --- |
| `protocol.md` | 0 |
| `output_schema.json` | 0 |
| `instruction.md` | all three paths, paragraph 4 |

Nothing else in the agent's world says where to write. If a rewrite drops,
renames, or relativises one of these, the agent writes somewhere harbor does
not collect from, the verifier finds nothing, and **every attempt scores 0** —
which the run audit reads as an underspecified task, not as difficulty.

Keep all three, absolute, spelled exactly:

- `/app/output/posterior.json`
- `/app/output/policy.json`
- `/app/output/audit.json`

The four input paths are safer — `protocol.md` and `output_schema.json` are
also reachable by name — but keep them absolute too:
`/app/input/model.json`, `/app/input/archive.json`, `/app/input/protocol.md`,
`/app/input/output_schema.json`.

---

## 2. Gaps worth fixing

### 2.1 Strict JSON is enforced but never stated anywhere

`checker.strict_load` rejects **duplicate JSON keys** and the literals **NaN
and Infinity**. Neither `instruction.md`, `protocol.md` nor
`output_schema.json` mentions this. A solver that emits `NaN` from an underflow
is rejected without ever having been warned, which is the kind of thing the run
audit treats as an unfair specification rather than difficulty.

One clause fixes it. Something to the effect that outputs must be plain JSON
with finite numbers and no repeated keys.

### 2.2 The tool sentence reads as a restriction

> The environment supplies Python 3.12, NumPy 2.2.6, and SciPy 1.15.3.

True, but an agent can read it as *only* those. The internet is open and the
agent keeps full capabilities; a constraint that is not real is an artificial
handicap. Consider making it clear these are provided rather than imposed.

### 2.3 One quantity has three names

| Where | Term |
| --- | --- |
| `protocol.md` | joint losses |
| `output_schema.json` | `joint_collapse` (the JSON key) |
| `instruction.md` | joint collapse probabilities |

The key is fixed, so the prose should move toward it. Using one term
throughout is also the safer style choice: synonym variation reads worse than
repetition.

---

## 3. What the draft already gets right

Do not lose these in a rewrite.

- States the **goal and the deliverable**, not a numbered recipe. The guidance
  rejects checklist-shaped instructions.
- Names the objective precisely: minimise the **worst scenario** probability of
  **two consecutive completely empty network censuses**, years 0 to 6, with
  year 0 the final historical census.
- Says **a later recolonisation does not undo an earlier collapse** — this is
  the definition of the scored event, not a hint. Without it the task is
  ambiguous.
- Says the same observation-to-action table must hold **under all three
  scenarios**, and that the scenario is **fixed for the whole future and never
  disclosed**. Also definitional.
- Says the **budget holds on every branch**.
- Gives both acceptance tolerances: risks within **1e-6** of independent
  evaluation, worst risk within **1e-5** of the optimum, and states that **any
  admissible policy meeting the bound is acceptable**.
- Says only the three artifacts survive ("Do not rely on other files being
  retained"), which is true and load-bearing.
- Says the four inputs are the complete specification and no outside biology is
  needed. This prevents an agent inventing ecological assumptions.

---

## 4. What must not be added

The draft is clean on this and should stay clean.

- **No method.** Do not name the quartet or symmetry diagnostic, the
  augmented-state construction, the retention divisor, the integer program, or
  HiGHS. Those are the answer.
- **No numbers from the answer.** Not the worst risk, not the chosen mask, not
  the survey, not the number of distinct follow-up actions.
- **No step list.** State what must be true when the work is done.
- **No canary line.**

One judgement call, yours not mine: paragraph 1 says treating the archive as an
ordinary random sample "would change the evidence". That is more than pointing
at the protocol — it tells the agent the naive route is wrong. Your
`problem.md` says the selection experiment is deliberately fully specified and
"its likelihood correction is not left for the agent to guess", so this looks
intended rather than accidental. Keep it if that was the intent; it is
defensible either way, but it should be a decision rather than an inheritance.

---

## 5. The mandated closing sentence

The file must end with a blank line, then exactly this, then at most one
newline:

`You have 18000 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.`

18000 must equal `[agent].timeout_sec` in `task.toml`. If you change one,
change both. `tools/structure-check.py` verifies this at byte level.

---

## 6. On authorship

Kepler screens this file and only this file for AI-generated text, and your own
`claude_handoff.md` says it needs your substantive authorship and must not be
relabelled as human-written. So this is a rewrite in your words, not an edit
pass over the draft.

Two things worth knowing, because they cut against the instinct to polish:

- The check screens for **machine-generated text**, not for imperfect English.
  Plain, slightly heavy, domain-specific prose from someone who actually knows
  the problem is the easiest thing to pass. Even, tidy, evenly-cadenced writing
  is what trips it.
- Your own playbook's finding, measured: adding literary flourishes to sound
  human made results **worse**, not better. So does deliberately rough grammar.

When you hand the rewrite back, I will check it against sections 1 to 5 above —
paths, tolerances, the closing sentence, terminology against the protocol, and
anything that leaked — and report what is wrong separately from what is merely
different from the draft, so you can reject the second group.
