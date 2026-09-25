# Deliberate cheating attempt

This directory holds the laziest attempt you can think of that a weak verifier
would let through. **It is never executed** by harbor or by the pipeline — it is
kept as evidence that you tried to break your own task, and reviewers read it.

Kepler runs a dedicated adversarial probe that attempts the same thing: an agent
is explicitly invited to pass your verifier without doing the work. If it
succeeds, the task fails.

## How to use this folder

1. Before finalising the verifier, ask: *what is the cheapest thing that passes?*
   Typical answers — hardcoding constants that happen to satisfy a loose schema
   check; echoing an input back as the output; emitting a degenerate result
   (all zeros, an empty list) that a weak assertion accepts; writing the file
   and exiting 0 so an exit-code check passes; reading a value the environment
   image accidentally exposes.
2. Write that attempt here, as `cheat.sh` or similar.
3. Run it against your verifier. **It must score 0.**
4. If it scores 1, the verifier is wrong, not the cheat. Tighten
   `tests/test_outputs.py` and repeat.

Record below what you tried and why each attempt now fails.

## Attempts

| # | What it does | Why the verifier rejects it |
| --- | --- | --- |
|   |              |                             |
