# Difficulty analysis

Difficulty is the gate this task is most likely to fail, and it is the one that
cannot be measured here. What *can* be measured is how much of the method the
agent is handed, because that is a property of the input files, not of any
agent run.

## The finding

Every trap the mutation suite tests for was named explicitly in
`environment/data/protocol.md`, five of them as direct instructions not to make
the mistake.

| Trap the verifier catches | How the protocol named it, before this change |
| --- | --- |
| Treating the archive as a random sample | "the likelihood of a retained record is its ordinary observation likelihood **divided by P(A \| M)**" |
| Factorizing destination occupancies | "Integrating out S **does not, in general, leave destination occupancies independent**" |
| Scoring terminal emptiness | "a sustained-absence objective, **not the probability of emptiness at t=6**" |
| One action table per scenario | "A different table for each scenario **is not an admissible policy**" |
| Conditional in place of joint losses | "**Do not divide** joint losses by branch probabilities" |
| Per-patch survey weather | "shared by all four patches on that visit" |
| Water report per visit | "one factor per year, **not one per visit**" |

Seven of seven. An agent that read the protocol carefully and implemented
exactly what it said could not make any of the errors the task was built to
catch — not because it reasoned well, but because it was told.

This is the template's first listed rejection symptom: *"6-7 of 8 passes in
under 30 minutes. Usually means: method handed over, or single-insight task."*

## Why this happened, and why it was not unreasonable

The design package is explicit that this was deliberate. `problem.md`: "The
complete model is supplied so that scientific reasoning and implementation can
be tested without access to undisclosed biological knowledge", and "The
selection experiment is fully specified; its likelihood correction is not left
for the agent to guess."

That is a coherent theory of difficulty: the work is hard because four coupled
requirements must all be executed correctly over a long chain of dependent
steps, not because any one of them is hard to discover. "Long-horizon work with
many dependent steps" is one of the guidance's own proven sources of
difficulty.

The risk is that it collapses into an implementation exercise, and
implementation is what current agents are best at. The four requirements are
individually simple once stated; the protocol stated them all.

## The change

The principle applied: **the protocol must specify the generative model
completely, because that is what makes the task fair. It does not have to name
which inferences are wrong.**

Removing a warning removes no information the agent needs — the correct answer
is still derivable from the model specification — it removes only the
signposting. Five hand-holds were removed:

1. **The retention formula.** The sampling experiment is still described in
   full: draw a history under M, keep it only if it meets the retention rule,
   discard earlier attempts. That is textbook rejection sampling and fully
   determines the correction. The explicit division by P(A|M), and the warning
   not to double-correct the prior, are gone. The agent must now recognise that
   the selection changes the likelihood and work out how.
2. **The dependence warning.** The exact conditional colonization formula and
   the statement that destinations are conditionally independent *given S*
   remain. That marginalizing over S destroys independence is a mathematical
   consequence the agent derives.
3. **The terminal-emptiness contrast.** The collapse event is still defined
   precisely: at least one adjacent pair of censuses with all four patches
   empty, absorbing once it occurs. It is no longer contrasted with the wrong
   alternative.
4. **The admissibility restatement.** "A single initial choice and a single
   observation-to-action table" remains; the redundant sentence naming the
   inadmissible form is gone.
5. **The joint-vs-conditional instruction.** "P(o and collapse | …)" is already
   unambiguous about being a joint probability.

Deliberately **kept**, because removing them would create unfairness rather
than difficulty — each specifies the model rather than warning about an
inference:

- survey weather is shared across patches within a visit,
- one water report per year,
- the initial distribution is not stationary (an agent could otherwise
  reasonably assume it is),
- the scenario survival vector is distinct from the scalar hypothesis shift
  (the two share a name in the data, so this is a naming clash, not a trap).

## Proof the change is safe

`protocol.md` is documentation. The reference computes from `model.json` and
`archive.json` only, so editing the protocol cannot move the answer. Verified
rather than assumed:

- `model.json` and `archive.json` hashes are **unchanged from the original
  package** (`32f89422…`, `3f49c882…`). Only the two documentation files were
  rehashed in `manifest.json`.
- Six harbor oracle runs across the change produce **one distinct artifact
  set**: `posterior=4272c7be42fd policy=90fe10965d5d audit=511b9f445fcb`.
- Mutation suite: **19/19**, unchanged.
- Ablation ladder: re-run, **byte-identical** to the committed JSON.
- Structure check: 174 pass, oracle 1, nop 0.

The task's answer, verifier, gates and evidence are all exactly as before. Only
what the agent is told has changed.

## What this is not

This is an argument about difficulty, not a measurement. No frontier agent has
attempted the task, here or anywhere. Specifically unresolved:

- **Whether the remaining difficulty is sufficient.** Four coupled requirements
  over a long chain, now without signposting, is a reasonable design. It could
  still be solved 7 or 8 times out of 8 by a careful agent, in which case the
  next lever is structural rather than editorial — a second dependent decision,
  or a requirement that cannot be satisfied by implementing the protocol
  literally.
- **Whether it is now too hard.** Removing signposting risks the opposite
  failure: 0 or 1 solves, with correct science in the failing trials. The
  guidance's own reading of that outcome is that something is missing or
  unclear, not that the task is hard. The generative model is still complete,
  which is the safeguard, but only a real probe settles it.
- The guidance **contradicts itself** on whether zero solves is acceptable
  (line 137 "at least 0", line 159 "at least once… Both fail"). Designed for
  ≥1, which satisfies both readings.

If the probe comes back at 7–8 solves, the next step is a structural change,
not more removal. If it comes back at 0, the first thing to check is whether
the failures are scientific or conventional — the diagnostic table in
`docs/authoring-playbook.md` §5.4 applies directly.
