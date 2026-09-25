# Reviewing a task spec

Run this when the repo owner delivers a problem specification and its
`instruction.md`. Findings are **reported**, not applied: `instruction.md` is
the owner's to write and to change (CLAUDE.md §2).

Two parts — what to check, and how to correct text without damaging it.

---

## Part 1 — What to check

### 1. Scope

- [ ] Field is Ecology & Evolutionary Biology, Neuroscience & Cognitive
      Science, or Medicine & Health Sciences. **Never** Biology &
      Biotechnology.
- [ ] `subfield` is free text and specific ("population genetics", not
      "biology").
- [ ] `domain` and `field` match what the submit form has selected. The form is
      the authority on the exact slug string.

### 2. Instruction mechanics

- [ ] Ends with a blank line, then the mandated sentence verbatim with N equal
      to `[agent].timeout_sec` as an integer, then at most one newline.
- [ ] Every artifact in `task.toml` is named in the instruction, with an
      **absolute** path.
- [ ] Output format fully specified: keys, types, units, precision, ordering.
      Anything the verifier demands, the instruction states. Ambiguity resolved
      in the verifier but not here is unfair and fails the run audit.
- [ ] States the goal and the deliverable, not a numbered recipe of steps.
- [ ] Conditions that make the answer determinate are stated: which data, which
      subset, what is unavailable.
- [ ] **No leak.** The instruction must not name the method, the diagnostic,
      the expected distribution or the tool that cracks it. Those are the
      answer. (Playbook §2.1.)
- [ ] Context a domain expert would obviously have is present. Withholding it
      is an artificial handicap, not difficulty.
- [ ] No eval-set canary line.

`tools/structure-check.py` covers the mechanical half of this automatically.
The judgement half — leak, recipe tone, determinacy — is a read.

### 3. Verifiability

- [ ] The deliverable is machine-checkable to exactly 0 or 1. No partial
      credit.
- [ ] Exact equality wherever possible. Any tolerance is justified by what the
      science supports, not chosen to make the oracle pass.
- [ ] Deterministic: no unseeded randomness, no wall-clock dependence, no bare
      float comparison.
- [ ] The verifier reads **content**, never an exit code, a file's existence,
      or a string the agent can print at will.
- [ ] Re-running the verifier on the same oracle output gives the same reward
      every time.

### 4. Anti-cheat

Name the laziest attempt that would pass, then confirm it does not. At minimum:

- [ ] Hardcoded plausible constants fail.
- [ ] Echoing an input back as the output fails.
- [ ] A degenerate answer (all zeros, empty list, everything flagged, nothing
      flagged) fails.
- [ ] Writing the file and exiting 0 fails.
- [ ] Nothing readable in the environment image shortcuts the work.

Keep the attempt in `cheat/`. Kepler runs an adversarial probe that tries the
same thing.

### 5. Leakage

- [ ] Nothing in `environment/` reveals ground truth: no seeds, no generator
      script, no parameter files, no expected output, no reference to `tests/`
      or `solution/`.
- [ ] Anything in the environment image is visible to the agent. Treat it that
      way.

### 6. Difficulty

- [ ] The targeted agent failure mode is written down and **specific** — the
      invariant broken, the race unseen, the rule that must be inferred rather
      than read.
- [ ] The **obvious remediation also fails.** An agent that notices the problem
      and applies the standard fix should still land wrong. This is the single
      highest-value property.
- [ ] **At least three independent hard points.** Two things that pass or fail
      together are one thing. A task resting on one point collapses to an
      easier tier the moment anything is softened. (Playbook §5.3.2, §5.3.5.)
- [ ] The solution is not findable online. The *method* being public is fine —
      that is expertise. The *answer* must not be.
- [ ] Difficulty is not volume, not a speed contest, not trivia, not
      obfuscation.

### 7. Band risk

Argue both directions explicitly:

- [ ] Why it will be solved **at least once** in 8. Never solved is treated as
      unsolvable as specified and fails.
- [ ] Why it will be solved **at most seven** times.
- [ ] Target 2–3 of 8, not 6–7 — margin above the floor, not near the ceiling.
      (Playbook §5.3.6, adapted from "one solve in five".)

This cannot be measured locally: `harbor run -a oracle` and `-a nop` work
without model credentials, a frontier-agent probe does not. Any pre-submission
claim about the band is an argument, and `difficulty_explanation` should read
as one.

### 8. Resources

- [ ] Fits `cpus`, `memory_mb`, `storage_mb`.
- [ ] Oracle timed; `[agent].timeout_sec` is several times its runtime, not the
      template default.
- [ ] `[verifier].timeout_sec` comfortably exceeds the test suite.
- [ ] No dependency on a live web resource. Data vendored, or the source pinned
      and immutable.

### 9. Originality

- [ ] The failure mode differs from every row in `docs/lessons-learned.md`.
      Not just new subject matter — a new way of breaking the model.

---

## Part 2 — Correcting the owner's text

Method from `docs/authoring-playbook.md` §3, which is the repo's standing
approach to reviewing prose written by someone else. It fits CLAUDE.md §2
exactly: correct meaning, never author.

Paraphrase damages meaning in a predictable order: **reference, then
attachment, then quantity.**

### Always fix

1. **Dangling reference** — "the latter" pointing at the wrong item.
2. **Detached qualifier** — one denominator attached to values that have
   different bases.
3. **Missing object** — "I summed the tables and put up against the total".
4. **Dropped quantifier** — "against its two losses" where the operation is
   against *the sum of* them.
5. **Wrong operation verb** — "included" where the operation was addition.
6. **Unsupported intensifier** — "nothing comes close" when the gap is small.
7. **Scrambled word order** that obscures meaning.
8. **Wrong collective noun** — "that adds up to" followed by separate values.
9. **Terminology that points elsewhere** — a term the source uses for something
   different.

Plus, for this project specifically:

10. **Unnamed or relative output path**, where the verifier needs an absolute
    one.
11. **A constraint the verifier enforces that the instruction never states.**
12. **A method or diagnostic named in the instruction** that gives the answer
    away.

### Never touch

Sentence order, phrasing, contractions, transitions, formality, number
formatting, paragraph length, British or American spelling, or any loose
construction that carries no ambiguity. Different from your own phrasing is not
a defect.

### Report back

The corrected text, plus a list separating **what was wrong** from **what was
merely ambiguous**, so the owner can reject the second group. Their call, not
the reviewer's.

---

## What this repo does not do

The playbook also carries voice-calibration guidance — target sentence lengths,
contraction and hedge rates, register advice for sounding less machine-written.
That material was measured against a different platform's authorship checker,
on a different text genre, so it is not evidence for Kepler in any case. More
to the point, applying it to `instruction.md` would be styling text to pass an
authorship check, which CLAUDE.md §2 and the Kepler guidance both rule out.

The owner writes `instruction.md` in their own voice. Reviewing it for the
defects listed above is colleague review. Restyling it is not, and is not done
here.
