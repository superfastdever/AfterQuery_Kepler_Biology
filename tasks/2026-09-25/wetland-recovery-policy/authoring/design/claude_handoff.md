# Claude implementation handoff

Build the Harbor task for `wetland-recovery-policy` from this package. Read `/Volumes/Work/Projects/AfterQuery/Kepler/AGENTS.md` first. This is Life Sciences, specifically Ecology & Evolutionary Biology. Do not reclassify it as Biology & Biotechnology or as a generic software task.

The scientific design has already been developed and tested locally. Implement that design faithfully before making changes. Do not substitute a simpler process, omit the archive selection, redraw ecological hypotheses across years, optimize forecast-specific policies, or replace the sustained-collapse event with terminal emptiness. Report any genuine defect and its evidence. Do not silently alter the specification to make an implementation pass.

## Read in this order

Read `problem.md`, the agent brief at `/Volumes/Work/Projects/AfterQuery/Kepler/Tasks/01-wetland-recovery/instruction.md`, and all four files in `public/`. Then inspect `author/reference.py`, `author/validate.py`, `author/check_outputs.py`, and `author/test_verifier.py`. The public protocol is the authoritative scientific definition. The Python reference is an implementation to check against it, not a substitute for reading the protocol.

Keep the prose plain, professional, and consistent with the brief. Use the same terms for the same quantities. Avoid invented personal experience, rhetorical flourishes, and deliberate rough grammar. Consult the humanization playbook only where it applies to Kepler. Do not rewrite the brief merely to imitate a detector-passing style. The instruction draft is AI-assisted and requires the user's substantive human authorship before submission; do not relabel it as human-written.

## Scientific implementation

For hypothesis m, the ecological state has 32 possibilities: hydrology h in {0,1} and a four-bit occupancy mask x. Use the specified conditional initial distribution, not a stationary approximation. A transition first samples h', then the surviving source subset, then external immigration and arrivals from those survivors. Sum over survivor subsets before treating the next-census vector as a marginal distribution. It is generally wrong to multiply four marginal destination occupancy probabilities.

For observations, integrate the shared visit weather outside the product of the four patch observation likelihoods. Independent visits get independent weather mixtures. The water report appears once per year. Missing entries integrate to one. A positive record is not known occupancy.

Let z_m(s) be the probability of no positive patch records in either of the two visits in a year given state s. With initial row distribution mu_m and historical transition T_m, the selection probability is

    q_m = 1 - mu_m diag(z_m) T_m z_m.

For each retained network record k, calculate the ordinary forward likelihood L_mk under the historical model. Its contribution is L_mk / q_m. Calculate posterior weights proportional to prior_m times the product of those six conditional likelihoods, using log scaling. Given m and the complete focal observations, ordinary normalized filtering gives the focal final state distribution: its retention event is already implied by those observations. Combine it with the posterior model weights to obtain the full joint posterior. Do not apply the selection normalizer a second time to that conditional state vector.

For future risk, retain the ecological state and track whether the last census was empty or sustained collapse has already occurred. In the reference implementation r=0 means the last census is nonempty without prior collapse, r=1 means one empty census without prior collapse, and r=2 means collapse has occurred. At t=0, set r from current occupancy with no prior failure. A second consecutive empty census switches to r=2. That flag is absorbing, but the ecological state still evolves and observations are still generated. This matters for branch probabilities on already-failed paths.

For initial restoration R and survey u, enumerate every legal added mask a. The allowed additions are disjoint from R, contain at most two patches, and meet the pathwise total budget after including the initial projects and survey. The empty addition must remain in the audit even if it is dominated.

For scenario k, observation code o, and feasible addition a, calculate C[k,o,a], the joint probability of receiving observation o and having collapsed by t=6 if that addition is used on branch o. Weight by the joint historical posterior over m and current state. Use three transitions with the first hydrology matrix and R, the observation emission, then three transitions with the second matrix and R union a. M stays fixed throughout. The scenario survival shift applies during both phases. Also calculate P[k,o], the observation branch mass. C is not a conditional probability; do not divide it by P for the robust optimization.

For each initial choice, solve the deterministic policy problem with binary x[o,a]:

    minimize z
    sum_a x[o,a] = 1 for each o
    sum_o,a C[k,o,a] x[o,a] <= z for each scenario k.

Compare the ten initial choices. The reference uses SciPy's HiGHS-backed `milp`. Multiplying the loss coefficients and objective variable by 1e6 makes numerical feasibility tolerances small on the probability scale. Independently evaluate the selected binary table from C, check its feasibility, and compare its objective against the solver's dual bound. Do not rely on solver status alone. Other certified methods are acceptable.

## Bundle layout and dependencies

Create a new bundle under `Tasks/01-wetland-recovery/bundle/`, rather than mixing author files into the environment build context. Its root instruction is a copy of the reviewed canonical brief. The environment should use Python 3.12 with `numpy==2.2.6` and `scipy==1.15.3`, copy only the four public input files to `/app/input/`, and create `/app/output/`. No test code, latent state, correct artifact, generation seed, reference number, or author document may be copied into that image or left in its layers.

Build `solution/solve.sh` and helpers from the actual numerical analysis. The oracle must recompute the results from public inputs inside the environment; copying `author/oracle_artifacts` is not an acceptable demonstration of solvability. It must write these top-level artifacts:

- `/app/output/posterior.json`
- `/app/output/policy.json`
- `/app/output/audit.json`

Build a separate verifier image with the trusted checker, reference results, NumPy, and the exact testing package pins required by the supplied project guide: `pytest==9.1.1` and `pytest-json-ctrf==0.5.2`. Confirm that these pins resolve before claiming the image builds; report a guide/package incompatibility rather than silently changing it. Bake the verifier files with `COPY . /tests/`. Pre-create `/app/output/` and every other required artifact parent. Do not install anything during verification.

Adapt `author/check_outputs.py` into pytest tests and a `tests/test.sh` entry point that writes a CTRF report and `/logs/verifier/reward.txt` containing exactly 0 or 1. Initialize reward to 0 before running tests and change it to 1 only on verified success. Handle ordinary command failures through a fail-closed exit path. A container killed before any script runs is an infrastructure failure, not something a shell trap can guarantee to repair. Treat uploaded artifacts as untrusted data. Never import, execute, unpickle, or follow executable instructions from them. The trusted NPZ file is verifier-owned and loaded with `allow_pickle=False`.

The checker must use sealed reference arrays to evaluate the actual submitted policy. Agent-reported risks and agent-reported audit coefficients cannot be the grader's source of truth. Enforce types, array shapes, finite probabilities, complete unique observation codes, feasible added masks, all ten audit roots, posterior normalization, and the disclosed numerical tolerances. Permit alternative valid policies. Do not grade prose style or a particular implementation.

Use a CPU-only environment. A provisional allocation is 4 CPUs, 4,096 MB memory, and 10,240 MB storage, with an agent timeout of 18,000 seconds. Match the exact timeout sentence in the instruction. Choose build and verifier timeouts after measuring actual image builds and checks. The local reference calculation is fast, but its measured subsecond numerical runtime excludes Python startup and is not an estimate of authoring or agent-solving time. Do not add an `allow_internet` field, platform-pinned `FROM`, apt version pins, or compose volumes.

For `task.toml`, preserve the user's Life Sciences domain and Ecology & Evolutionary Biology field. The supplied general template and the user's Life Sciences submission screen use different taxonomies. Do not invent a machine-readable domain or field slug or silently use generic `Science`/`Biology`; resolve the actual accepted values when preparing the form and metadata. This does not prevent building the scientific bundle. Author name, email, and professional experience must come from the user. Do not fabricate credentials or certify an unmeasured expert time estimate.

## Validation and release

Reproduce the author checks first, then run the actual Harbor oracle and nop trials in the built images. Run the harness quality review and inspect the emitted CTRF report and reward file. Repeat the oracle to verify deterministic acceptance. A successful local Python run is not a successful Harbor run.

The local mutation suite rejects empty artifacts, malformed probabilities, duplicate JSON keys and observation codes, missing branches, infeasible spending, fabricated risk values, incomplete audits, and several complete solutions from scientifically incorrect models. Preserve those cases when porting the checker. It also accepts a different policy within the stated optimum tolerance; preserve that freedom.

Inspect the agent image for answer leakage and ensure the oracle reads only public scientific inputs. Test missing and malformed files through the real harness, not just the Python checker. Freeze the public input hashes before difficulty trials. Do not change the task between attempts within a difficulty probe. Run frontier-agent trials and inspect whether failures arise from scientific errors, implementation defects, ambiguity, resource limits, or reward hacking. Do not declare success merely because one attempt fails.

The supplied guide contradicts itself about zero successful attempts out of eight. Preserve that uncertainty when interpreting platform results. No separate "Scientific computing contract" is missing or required. Do not wait for one.

Return a concise implementation report with the bundle location, actual commands run, oracle/nop rewards, quality-review results, failure reasons, resource measurements, and anything still unverified. Do not submit or publish the bundle without explicit user authorization.
