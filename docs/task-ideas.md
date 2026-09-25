# Task idea pipeline

Candidate tasks, with the agent failure mode each one targets. An idea earns a
build only once that failure mode is written down and differs from everything
in `docs/lessons-learned.md`.

Scope is Life Sciences: **Ecology & Evolutionary Biology** and **Neuroscience &
Cognitive Science** primarily, Medicine & Health Sciences occasionally, never
Biology & Biotechnology.

Status: `idea` → `vetted` (difficulty and verifiability argued) → `building` →
`submitted`.

---

## Difficulty hardening

Reusable levers, ordered by how much they actually move the solve rate. Applies
to every task here, not just the ones below.

**1. Make the obvious remediation fail too.** The highest-value lever by some
distance. Frontier agents usually manage the naive approach and will often try
one standard fix on top of it. If both the naive route and the obvious fix land
somewhere wrong, the solve rate drops sharply and the task stays fair — nothing
is hidden, the data simply have to be discriminated.

**2. Three independent hard points, from the start.** From
`docs/authoring-playbook.md` §5.3.2: a task resting on one hard point
"collapses to an easier tier the moment you soften it". The independence test
is §5.3.5 — two things that pass or fail together are one thing. Build three
that can fail separately, and the task degrades gracefully instead of falling
off a cliff when one is weakened.

**3. Require a quantity only the correct route produces.** A per-item
classification, or a structural placement that a summary pipeline cannot emit
at all. It cannot be guessed, and it keeps the binary reward honest: there is
no way to be half-right and still pass.

**4. A negative control inside the deliverable.** A statistic whose correct
value only exists if a control was genuinely run. Cheap to verify, expensive to
fake.

**5. Size against brute force, gently.** Enough data that exhaustive search
does not fit the budget while the targeted diagnostic is cheap. Used hard this
becomes a speed contest, which is not difficulty.

**Band target: 2–3 solves out of 8.** The platform's band is ≥1 and ≤7.
Adapting the playbook's §5.3.6 ("aim for one solve in five, not three"), aim
for margin above the floor rather than a seat near the ceiling. Note that a
task solved **zero** times fails just as surely as one solved every time, and
that "almost nothing solved it" is read by the platform as a specification
problem, not as evidence of difficulty (§5.4).

**Rejected sources of difficulty** — these fail the run audit or the
"fair with the internet open" rule: withholding context an expert would
obviously have; misleading or false documentation in the environment;
obfuscation and tokenizer tricks; difficulty by volume; requiring a tool the
agent could not know about.

---

## A. Species tree under hidden single-copy paralogy

**Field:** Ecology & Evolutionary Biology · *subfield: phylogenetics*
**Status:** idea — recommended for the first build

### The problem

The agent gets a few hundred gene alignments across ~12 taxa. Every orthogroup
holds **exactly one sequence per taxon**, which is the conventional signal that
a gene family is safely orthologous. A fraction of them are not: an ancient
duplication followed by differential loss in different lineages leaves one copy
per taxon while the copies are *paralogous*, so those gene trees record the
duplication history rather than the species history.

Deliverable: the species tree topology, plus the set of orthogroups whose
history is not the species history.

### Hardened design: two mechanisms, three hard points

As first sketched this task had a single hard point — notice the discordance is
not all ILS — which is exactly the fragile shape the playbook warns about. The
hardened version seeds **two** independent causes of gene-tree discordance that
require **opposite** treatments:

| Set | Cause | Correct treatment |
| --- | --- | --- |
| P | ancient duplication + differential loss | **remove** — their history is not the species history |
| R | among-lineage rate heterogeneity (long-branch attraction) | **keep and re-model** — removing them discards real signal and biases the result |

Tuned so three distinct topologies result:

- use everything → `T_naive`
- drop every discordant gene → `T_blunt`
- remove P, re-model R → `T_true`

Only correct discrimination reaches `T_true`. This punishes "drop the
outliers", which is the move a capable agent is most likely to make once it
notices discordance at all — lever 1 above.

The three hard points, each able to fail on its own:

| # | Hard point | Why it fails independently |
| --- | --- | --- |
| 1 | Detect that discordance is not coalescent; separate P from R | Needs the quartet-symmetry test; an agent can miss it entirely |
| 2 | Re-model R rather than dropping it | An agent can pass 1 and still blunt-drop everything discordant |
| 3 | Place the duplication on the species tree | Needs reconciliation; passing 1 and 2 does not yield it |

Point 3 also serves lever 3: a tree-only pipeline cannot emit it at all.

### Why a frontier agent fails

The standard pipeline — align, infer gene trees, summarise with ASTRAL, or
concatenate and infer — assumes single-copy implies orthologous. That
assumption is invisible in the data and is exactly what the task violates. An
agent that runs the standard pipeline gets a confidently wrong tree.

The rule that must be **inferred rather than read**: under incomplete lineage
sorting alone, the two discordant quartet topologies are expected in *equal*
frequency. A significant asymmetry means the discordance is not coalescent —
it is duplication, introgression, or systematic error. An expert checks this.
The naive pipeline never asks.

This is not trivia: the principle is textbook (it underlies the D-statistic).
The difficulty is knowing to apply it, then acting on it — partition the genes,
identify the offending set, re-infer from the clean set. That is an iterative
diagnose-and-revise loop, not a read-and-solve.

ASTRAL-Pro and similar paralogy-aware methods do not rescue this: they key on
*multi-copy* gene families, and every orthogroup here is single-copy.

### Verification

- **Species tree:** unrooted Robinson–Foulds distance to the true topology
  must be 0. Discrete, deterministic, and unguessable — there are ~13 billion
  unrooted topologies for 12 taxa.
- **Flagged set:** exact match against the simulated duplicated orthogroups.
  Designed so an expert reaches 100%, with the ambiguous middle cases excluded
  from the ground truth rather than graded loosely.

Both are exact equality, so no tolerance tuning and no float comparison.

### Anti-cheat

- Guessing the topology is hopeless at that tree count.
- Returning *all* orthogroups as flagged, or none, fails the set check.
- The true tree must not be recoverable from anything in `environment/`:
  simulation seeds, parameter files and the generator stay in `tests/`, and
  only the alignments are vendored into the image.
- The naive-pipeline answer is a specific wrong topology, so a test asserting
  the submission differs from it catches the lazy attempt directly.

### Risks to settle before building

1. **Band calibration.** The paralog fraction and duplication depth set how
   often the naive pipeline fails. Needs tuning against the ≥1-of-8 / ≤7-of-8
   band, which means actually running attempts.
2. **Paralogy vs introgression.** Both produce quartet asymmetry. Either design
   the generative process so the flagged set is unambiguous, or frame the
   deliverable as "genes whose history is not the species history", which is
   what the verifier can actually check.
3. **Tooling in the image.** IQ-TREE and ASTRAL should be baked in from pinned
   releases, not fetched at run time.
4. **Runtime.** A few hundred gene trees on 1–2 CPUs is minutes, not hours —
   fine, but the oracle must be timed before setting `[agent].timeout_sec`.

---

## B. Demographic inference confounded by linked selection

**Field:** Ecology & Evolutionary Biology · *subfield: population genetics*
**Status:** idea

Simulated genomes under a known demographic history, with background selection
in some genomic regions. Site-frequency-spectrum inference over all sites
recovers a spurious bottleneck, because linked selection distorts the SFS in a
way that mimics one. The agent must recover the true history, which requires
recognising the confound and masking or modelling it.

**Failure mode:** treating the SFS as a pure demographic signal — a different
error from A (A is about which data to trust, B is about what a summary
statistic actually measures).

**Verification concern:** parameter recovery within tolerance is softer than
A's exact topology, and tolerance tuning is where nondeterminism creeps in.
Viable if the naive and correct answers are far apart, but A is the safer
first build.

---

## C. Spike sorting through electrode drift

**Field:** Neuroscience & Cognitive Science · *subfield: electrophysiology*
**Status:** idea

Simulated extracellular recording with slow electrode drift and bursting units
whose spike amplitude declines within a burst. Both break template matching:
drift splits one unit into several, bursting drops the later spikes of a burst.
Ground truth spike times and unit identities come from the simulation.

**Failure mode:** accepting a sorter's default output without checking for
drift-induced oversplitting — a perception/signal-processing failure, distinct
from A and B.

**Concerns:** GPU is unavailable (`gpus = 0` outside ML tasks), so
CPU sorters only, which raises runtime. Scoring is threshold-based rather than
exact, so the pass mark needs justifying. Heavier and flakier than A.

---

## Deliberately not pursued

- Anything in **Biology & Biotechnology** (bioimaging, genomics tooling,
  synthetic biology) — out of scope by repo policy.
- "Find the bug in this analysis script" framings. Real in practice, but they
  drift toward software engineering and away from the approved domain.
- Tasks whose difficulty is volume: 400 files to touch is long, not hard.
