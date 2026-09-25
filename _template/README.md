# Task template

Copy this directory to start a new task:

```bash
tools/new-task.sh <slug>     # creates tasks/<today>/<slug>/ from this template
```

Slugs are lowercase, at most three hyphen-separated words. The directory name,
`[task].name` (as `afterquery/<slug>`) and the name submitted on the platform
must all agree.

## What to fill in, in order

1. **Design the problem first.** Write down the specific agent failure mode you
   are targeting before you write any code. Check `docs/lessons-learned.md` that
   it differs from previous tasks — a re-skin of an earlier scaffold is
   rejected however much the surface changed.
2. `environment/Dockerfile` — the agent's world. Vendor input data in. Nothing
   from `tests/` or `solution/` may be referenced here.
3. `tests/test_outputs.py` + ground truth — the verifier. Write this *before*
   the reference solution: it forces you to define what correct means.
4. `solution/solve.sh` — the reference solution. Must score 1.
5. `authoring/` — generator, seeds, and your own cheat attempts. See `authoring/NOTES.md`.
6. `task.toml` — metadata and resources. Time the oracle, then set
   `[agent].timeout_sec` to several times that.
7. `instruction.md` — **written by the repo owner, not by AI.** See the comment
   block at the top of the file.

## Before submitting

```bash
tools/structure-check.py tasks/<date>/<slug>   # replicates Kepler's submit-time gates
tools/validate.sh tasks/<date>/<slug>          # oracle must be 1, nop must be 0
tools/package.sh <slug>                 # build/<slug>.zip
```

Files in this template that still contain `TODO`, `NotImplementedError`, or the
placeholder slug will fail the structure check — that is deliberate.
