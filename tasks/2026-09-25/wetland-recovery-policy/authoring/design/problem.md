# First problem: a recovery policy for a partially observed wetland network

Domain: Life Sciences. Field: Ecology & Evolutionary Biology. Subfield: metapopulation ecology and conservation decision analysis. Proposed task slug: `wetland-recovery-policy`.

The deliverable is an implementable six-year recovery policy for four wetland patches. The manager can restore one patch now and reserve a survey, then use the survey result to choose additional restoration in year 3. The objective is to minimize the worst forecast probability of two consecutive censuses with no breeding population anywhere in the network. All spending must be feasible on every observation branch.

The task is a synthetic scientific decision study. It does not represent a named reserve, species, or empirical monitoring program. The complete model is supplied so that scientific reasoning and implementation can be tested without access to undisclosed biological knowledge. The numerical instance is original to this package; that is not a claim that the platform's similarity check has been passed.

## The scientific problem

The archive contains six network histories, including the focal network, retained only after at least one early positive detection. Patch detections can be false positives or missed detections. Weather is shared across patches on a visit, while regional hydrology changes between years. An empty patch can be colonized by an occupied neighbor, but the neighbor must survive the intervening season before it can supply propagules. This makes destination occupancies dependent after the uncertain surviving source populations are integrated out.

Six ecological hypotheses disagree about survival, dispersal, initial occupancy, and detection. One hypothesis is shared across networks and remains fixed through time. The archive updates these hypotheses and the focal network's current state jointly. The selection experiment is fully specified; its likelihood correction is not left for the agent to guess.

Three forecasts describe early drought, late drought, and persistent stress, with different site-level survival responses. They are alternative futures rather than weighted Bayesian hypotheses. One scenario governs the entire future. The manager sees the year-3 survey but never the scenario, so there must be one table of follow-up actions that works across all three futures.

The requested outputs are a posterior, a policy, and an audit of counterfactual branch losses. They allow the sealed verifier to check the underlying scientific calculation and evaluate the actual submitted policy, rather than accept a claimed optimal objective value.

## Why this is a research-level candidate

The intended challenge is the integration of several distinct scientific requirements. A standard occupancy fit is not enough, because the sampling design changes the likelihood. A standard independent-patch forecast is not enough, because uncertain source survival couples colonization. A standard terminal extinction calculation is not enough, because the failure event depends on the path and can happen before a later recolonization. A policy optimized separately under each forecast is not enough, because that policy would require information the manager never receives.

The strongest expected failure is a superficially reasonable robust policy that takes a worst-case scenario separately within each survey branch, or uses a different action table for each hidden scenario. Those calculations change the scientific decision problem. Correct optimization must retain one scenario across the whole future and select one common deterministic action for each observable result.

The finite state space keeps the task computationally tractable. Small runtime after a correct implementation is desirable: the challenge is constructing the right scientific calculation, not making the agent wait. The target is specialist work beyond routine PhD coursework, but the actual expert time and frontier difficulty have not been measured. No claim of a guaranteed first-attempt model failure is justified before trials.

## What has been established locally

The author prototype constructs an exact 32-state ecological process under each hypothesis. It augments that process with a three-valued collapse record and integrates all future observations. A small integer program finds the best deterministic response table under each of the ten initial choices.

The selected initial choice restores Cedar and reserves the intensive survey. Its follow-up table uses three different restoration choices, depending on the recorded survey result. The best worst-scenario collapse probability is approximately 0.901974003. This is a high-risk population under the constrained interventions; the result is the best allowed policy, not a claim that restoration achieves a low collapse risk.

The calculated risks are approximately 0.901974003 for early drought, 0.901962790 for late drought, and 0.894448865 for persistent stress. The next-best initial choice is worse by about 0.000590691. The permitted objective gap is 0.00001, so the initial-choice distinction is larger than the grading tolerance.

Omitting the retention correction changes the posterior hypothesis weights by an L1 distance of about 0.454. Replacing sustained collapse with final-census emptiness changes the risk by up to about 0.181 for the selected policy. Letting the manager know the forecast produces an unattainable lower bound about 0.000250430 better than the valid minimax result. These are measured structural distinctions in the current instance, not predictions about how often an agent will fail.

## Files and visibility

The agent-facing brief is at `/Volumes/Work/Projects/AfterQuery/Kepler/Tasks/01-wetland-recovery/instruction.md`. The four files in `public/` become `/app/input/` inside the environment. They contain the model, observations, protocol, and output contract.

Everything in `author/` is for the author and Claude only. That includes generation code, latent generation states, the numerical reference, correct artifacts, mutation tests, and validation reports. None of it belongs in the agent image. The final verifier may contain trusted reference arrays, but those belong only in its sealed image.

Read `claude_handoff.md` for the implementation procedure and `validation_report.md` for the exact limits of the current validation.

## Authorship and release status

This problem package and instruction draft were produced with AI assistance. The instruction is an author-review draft and must not be represented as human-authored text. The supplied Kepler guidance explicitly reserves the submitted instruction for human authorship. The user should write the final wording from their own understanding of the problem, with technical review to preserve the contract.

The package is ready for Claude to implement and validate through Harbor. It is not a submission-ready bundle, and no frontier-model trial or platform acceptance check has been run.
