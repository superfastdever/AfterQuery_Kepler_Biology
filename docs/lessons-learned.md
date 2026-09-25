# Lessons learned

Two purposes: keep each task a genuinely new problem, and stop repeating
mistakes that have already cost a submission.

## Failure modes already used

Kepler rejects a task that re-skins an earlier one — same scaffold, same
solution shape, same verifier shape, different nouns. It also wants each task
to break models in a way the rest of the set does not. **Add a row before
building, not after.** If the new idea's failure mode is already in this table,
change the idea.

| Task | Field | Failure mode targeted | Source of difficulty | Verifier shape | Outcome |
| --- | --- | --- | --- | --- | --- |
| _(none yet)_ | | | | | |

The **Field** column keeps coverage visible: the two thin fields (Ecology &
Evolutionary Biology, Neuroscience & Cognitive Science) are where tasks are
most wanted, so a run of entries in one field is a signal to move.

"Source of difficulty" should name one of: long-horizon dependent steps; a rich
environment that must be explored; a dynamic environment; cross-domain
expertise; iterative trial and error. "Ten tasks that all reduce to
reconstructing the exact numbers a missing tool would have produced are worth
about as much as one."

## Review feedback received

Record every rejection reason and every advisory note, so the next bundle does
not repeat it.

| Date | Task | Stage | Verdict | What to do differently |
| --- | --- | --- | --- | --- |
| | | | | |

Stages: structure · AI check · similarity · reference verification · quality
review · anti-cheat · difficulty probe · run audit · human review.

## Notes to self

Things learned building these, beyond what the platform guidance says.

- Harbor's own `harbor init` scaffold does **not** satisfy Kepler's rules: it
  installs pytest inside `test.sh` at verify time, pins `pytest==8.4.1` rather
  than the mandated `9.1.1`, and ships no `tests/Dockerfile`. Use
  `tools/new-task.sh`, not `harbor init`.
- `[metadata]` is free-form in harbor's schema, so Kepler's custom fields
  (`difficulty_explanation`, `relevant_experience`, …) validate fine locally.
  Local acceptance says nothing about whether reviewers will accept their
  content.
- Harbor collects artifacts before the verifier runs, so a trial that errors in
  the verifier still leaves `artifacts/` behind in the job directory. When a
  verifier claims a file is missing, look there first to see what the agent
  actually produced.
- **The difficulty probe cannot be run locally.** `harbor run -a oracle` and
  `-a nop` need no model credentials; running a frontier agent against the task
  does. So the solve band (≥1 and ≤7 of 8) is never measured before
  submission — it is argued. Write `difficulty_explanation` as an argument, and
  treat the platform's probe as the first real measurement.
- In a cloud dev container, `dockerd` may simply not be running. Starting it is
  often all that stands between "validation is impossible here" and a working
  local gate. Check before concluding validation has to happen elsewhere.
