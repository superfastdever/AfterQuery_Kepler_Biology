# Scientific and technical evidence ledger

This ledger separates published motivation from the original benchmark definition. The public input numbers, sampling experiment, intervention costs, and objective were authored for this synthetic task. They are not reported measurements or fitted parameters from the papers below. No copyrighted dataset or article text is required to solve the task.

| Source | Supported point | Limits of its use here |
| --- | --- | --- |
| [MacKenzie et al. (2003), Estimating site occupancy, colonization, and local extinction when a species is detected imperfectly](https://pubs.usgs.gov/publication/5224260), DOI 10.1890/02-3090 | Imperfect detection matters for dynamic occupancy, colonization, and extinction inference. | Does not establish this task's false-positive model, selection rule, or numerical parameters. |
| [Bertassello et al. (2021), Dynamic spatio-temporal patterns of metapopulation occupancy in patchy habitats](https://doi.org/10.1098/rsos.201309) | Wetland habitat dynamics, hydroclimatic forcing, and connectivity can be represented in stochastic patch occupancy models. | The four-patch transition process here is an original simplified definition, not a reproduction of their model or data. |
| [Williams and Brown (2022), Partial observability and management of ecological systems](https://www.usgs.gov/publications/partial-observability-and-management-ecological-systems), DOI 10.1002/ece3.9197 | Management can require decisions based on belief states and future observations rather than directly observed ecological states. | Does not validate the particular budget, restoration effects, or robust objective in this package. |
| [Williams (2011), Resolving structural uncertainty in natural resources management using POMDP approaches](https://pubs.usgs.gov/publication/70036993), DOI 10.1016/j.ecolmodel.2010.12.015 | Structural model uncertainty is a substantive resource-management problem. | This task's finite six-hypothesis prior is a benchmark definition, not an empirical posterior. |
| [SciPy official documentation, scipy.optimize.milp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html) | Mixed-integer linear optimization, integrality constraints, and available dual-bound and MIP-gap results. | The local implementation uses pinned SciPy 1.15.3; actual local execution establishes compatibility, not the current online documentation version alone. |

The source pages were consulted during design. Exact task behavior is defined by the vendored public inputs, so the agent does not need live access to these websites. Source dates or current website versions do not alter the mathematical instance.

## Original mathematical definitions

The archive prior is explicitly defined by drawing a shared model and then rejection-sampling each network record. Under that experiment, conditioning each history on retention gives L(record | M) / P(retention | M). This is a consequence of conditional probability, not a universal rule that every selected ecological dataset should be adjusted in the same way. If the prior or sampling experiment were different, the correction could also be different.

The robust scenario objective has no scenario prior. The scenario is fixed across the entire future, and each observable survey result gets one common deterministic action. Consequently, scenario probabilities are not Bayesian model weights, and a maximum cannot be distributed independently over observation branches without changing the problem.

The collapse event is the occurrence of an adjacent all-empty census pair within t=0 through t=6. It is a management objective for sustained absence. Because external immigration remains possible, calling it permanent biological extinction would be incorrect.

## Provenance and numerical evidence

The author generator uses a fixed seed, retained in `author/generation_record.json` with the latent states. These are withheld from the agent. Published sources do not supply the answer. The selected observation histories remain fixed; no current frontier model was used to select among candidate datasets.

During local design, forecast parameters were adjusted to ensure that the intended cross-scenario decision conflict actually exists. This was a scientific instance-design check, not a frontier-model search. The final instance is identified by `manifest.json`; it should remain unchanged within a difficulty trial set.

The exact local numeric checks and their errors are stored in `author/results/validation.json`. Artifact-verifier checks are in `author/results/verifier_validation.json`. Neither report establishes benchmark-wide originality, human authorship, Docker compatibility, or frontier-model failure.
