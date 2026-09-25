# Pre-submission checklist

Work through this before submitting. It is ordered by the pipeline stage that
would catch each item, so a failure here is a failure there.

## 0. Before writing any code

- [ ] The specific **agent failure mode** is written down. Not "it's hard" —
      the invariant that gets broken, the race that is invisible, the rule that
      has to be inferred rather than read.
- [ ] That failure mode is **different from every earlier task** in
      `docs/lessons-learned.md`. A re-skin of an earlier scaffold is rejected
      however thoroughly the surface changed.
- [ ] The work is **real** — something a person would be paid to do.
- [ ] The solution is **not findable online**. The agent has full internet.
- [ ] Difficulty comes from the work, not from withheld context, trivia,
      obfuscation, or sheer volume of files to touch.

## 1. Structure check (instant, at submit)

Run `tools/structure-check.py tasks/<date>/<slug>`. It covers all of these:

- [ ] `instruction.md`, `task.toml`, `environment/Dockerfile`,
      `solution/solve.sh`, `tests/test.sh`, `tests/Dockerfile` all present.
- [ ] `[task].name` is `afterquery/<slug>`; slug is lowercase, ≤3 hyphenated
      words, and equals the directory name.
- [ ] `artifacts = [...]` sits above the first `[section]`.
- [ ] Python packages pinned with `==` in both Dockerfiles, `test.sh` and
      `solve.sh`. Verifier pins are exactly `pytest==9.1.1` and
      `pytest-json-ctrf==0.5.2`.
- [ ] apt packages never version-pinned; `apt-get update` before installing and
      `rm -rf /var/lib/apt/lists/*` after.
- [ ] `allow_internet` not set, with either value.
- [ ] `[agent].timeout_sec` between 9000 and 18000; `cpus` ∈ {1,2,4,8,16};
      `memory_mb` ∈ {1024,2048,4096,8192,16384}; `storage_mb` ≤ 40960.
- [ ] `[verifier].environment_mode = "separate"`.
- [ ] No `FROM --platform=` pins. No eval-set canary markers.
- [ ] `instruction.md` ends with a blank line, then the mandated sentence with
      N equal to `[agent].timeout_sec`, then at most one newline.
- [ ] If `environment/docker-compose.yaml` exists, it declares no volumes.

## 2. Reference verification

Run `tools/validate.sh tasks/<date>/<slug>`, several times.

- [ ] Oracle scores **exactly 1**, every run.
- [ ] Nop scores **exactly 0**, every run.
- [ ] The verifier is deterministic: no unseeded randomness, no wall-clock
      dependence, no float comparison without a tolerance.
- [ ] `[agent].timeout_sec` is several times the measured oracle runtime.
- [ ] `[verifier].timeout_sec` comfortably exceeds the test suite's runtime.

## 3. Quality review (agentic, 35 criteria)

- [ ] The instruction states the **goal and the deliverable**, not a numbered
      recipe of steps.
- [ ] Every output path is **absolute** and named explicitly, and matches
      `artifacts` exactly.
- [ ] Output format fully specified: schema, keys, types, units, precision,
      ordering. Anything the verifier demands, the instruction states.
- [ ] The verifier checks **content**, never an exit code, a file's existence,
      or a string the agent can print.
- [ ] Ground truth lives only in `tests/`. Nothing in `environment/` reveals it.
- [ ] `tests/Dockerfile` pre-installs everything; `test.sh` installs nothing.
- [ ] `test.sh` writes `/logs/verifier/reward.txt` on **every** code path,
      including crashes, and emits a CTRF report.
- [ ] `tests/Dockerfile` does `mkdir -p` on every declared artifact's parent.
- [ ] No dependency on a live web resource that can change or vanish.

## 4. Anti-cheat probe

- [ ] You wrote the laziest passing attempt you could think of into `cheat/`
      and confirmed it scores **0**.
- [ ] Hardcoding plausible constants fails.
- [ ] Echoing an input back as the output fails.
- [ ] A degenerate result (zeros, empty list) fails.
- [ ] Nothing readable in the environment image shortcuts the work.

## 5. Difficulty probe

- [ ] Honest expectation that a frontier agent solves it **sometimes but not
      usually** — the band is ≥1 and ≤7 out of 8.
- [ ] An expert would need hours, not minutes.

## 6. Metadata and human review

- [ ] `difficulty_explanation`, `solution_explanation` and
      `verification_explanation` are specific. Reviewers read these first and
      generic text fails.
- [ ] `relevant_experience` describes genuine professional background, written
      by the repo owner.
- [ ] `expert_time_estimate_hours` is honest.
- [ ] `domain` and `field` carry the real **slugs** (not display names, not
      `TODO-*`), and match what is selected on the submit form.
- [ ] `field` is one of the in-scope Life Sciences fields — Ecology &
      Evolutionary Biology, Neuroscience & Cognitive Science, or Medicine &
      Health Sciences. **Never** Biology & Biotechnology.
- [ ] `subfield` is free text and specific (e.g. "population genetics", not
      "biology").
- [ ] `instruction.md` was **written by the repo owner**, in their own words.

## 7. Package

```bash
tools/package.sh <slug>
```

- [ ] The zip has `instruction.md` at its top level, not nested under a folder.
- [ ] No `__pycache__`, `.DS_Store`, or stray build output inside.
