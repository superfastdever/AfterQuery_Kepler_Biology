# Authoring workspace

Generators, seeds, cheat attempts and working notes. **Never mounted into any
container**, so nothing here is visible to the agent or to the verifier — this
is the sanctioned home for the things that must not leak.

The submit form's required layout allows `authoring/` at the bundle root and
**nothing else** beyond `task.toml`, `instruction.md`, `environment/`,
`solution/`, `tests/` and `README.md`.

## What belongs here

- **Generators.** The script that produced the task's data. Keeping it here
  rather than in `environment/` is what stops the agent from reading the
  process that made the answer.
- **Seeds and parameters.** Everything needed to regenerate the data
  byte-for-byte, so the task can be rebuilt or tuned later.
- **Cheat attempts.** See below.
- **Notes.** Calibration runs, tuning decisions, dead ends.

## The cheat attempt

Before finalising the verifier, ask: *what is the cheapest thing that passes?*
Write it here, run it against the verifier, and confirm it scores **0**.

Typical lazy attempts:

- hardcoding constants that satisfy a loose schema check
- echoing an input back as the output
- emitting a degenerate result (all zeros, an empty list, everything flagged,
  nothing flagged) that a weak assertion accepts
- writing the file and exiting 0, in case the verifier checks the exit code
- reading a value the environment image accidentally exposes

If any scores 1, the verifier is wrong, not the cheat. Tighten
`tests/test_outputs.py` and repeat.

Kepler runs a dedicated adversarial probe that attempts exactly this: an agent
is explicitly invited to pass the verifier without doing the work. If it
succeeds, the task fails.

## Record

| # | What it does | Why the verifier rejects it |
| --- | --- | --- |
|   |              |                             |
