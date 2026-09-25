# Wetland recovery protocol

This is a synthetic decision study for a cryptic, wetland-dependent animal. The numbers define the study; they are not estimates for a named species or advice for an actual reserve. There are four patches in the order Alder, Birch, Cedar, Dogwood. All probabilities and costs needed for the calculation are in `model.json`, and the retained survey records are in `archive.json`. No parameter fitting beyond the finite hypothesis update described here is needed.

## Ecological state and annual order

At a census, X is a vector of four binary occupancy indicators. H is a regional hydrologic state, with 0 meaning wet and 1 meaning dry. Occupancy denotes a breeding population, not an individual count. A patch mask is the sum of X[i] times 2**i, so Alder is the least significant bit. A state index is 16*H + mask. Arrays indexed by patch follow the order above. All logarithms are natural.

The initial H distribution is `initial_hydrology`. Conditional on H and hypothesis m, initial patch occupancies are independent Bernoulli variables with probability logistic(logit(initial_occupancy[H][i]) + initial_shift[m]). This initial distribution applies separately to the beginning of each archived network record, before year 0 observations. It is not a stationary distribution.

One hypothesis M is shared across every archived network and the focal network and stays fixed through all historical and planning years. Its six possible values, prior weights, and parameter shifts appear in `hypotheses`. Independent network histories are independent conditional on M; their hydrologic states are not shared. All archived networks were unmanaged: the restored mask is zero and every historical transition uses historical_hydrology. The dispersal scale multiplies probabilities, whereas the survival, detection, and initial shifts are additive on the log-odds scale.

For every annual transition, first draw H' from the applicable hydrology matrix, whose rows are the current H and columns the next H. Then draw the surviving source population indicator S[i] independently for each currently occupied patch. It is zero for an empty patch. Its probability when X[i]=1 is

    logistic(logit(survival[H'][i]) + survival_shift[m]
             + forecast_survival_shift[i]
             + restored[i] * restoration_logodds[H'][i]).

The forecast shift is zero for historical years and is the vector named `survival_shift` in the selected future scenario during all six planning transitions. Do not confuse that vector with the scalar hypothesis shift. Restoration is persistent and modifies only this survival probability. It does not change the initial occupancy, dispersal, immigration, or survey process, and it does not directly populate an empty patch.

After survival, each surviving patch j sends a successful colonizing propagule to destination i independently with probability dispersal[j][i] * dispersal_scale[m]. Rows are sources and columns are destinations. The donor breeding population is not removed. Independently, destination i receives successful external immigration with probability external_colonization[H'][i]. Thus a destination without a surviving population is occupied at the next census if at least one of these arrivals succeeds. Equivalently, conditional on the complete surviving source vector S, its colonization probability is

    1 - (1 - external_colonization[H'][i])
        * product_j(1 - S[j] * dispersal[j][i] * dispersal_scale[m]).

Destinations are conditionally independent given S and H'. A surviving patch is occupied with probability one. A patch that lost its population can be recolonized in the same transition. Newly colonized patches do not send propagules until a later transition. External immigration remains possible after all four patches have become empty.

## Survey observations

There is no ecological transition between visits within a census year. Each visit has its own unobserved survey weather W, shared by all four patches on that visit. W=0 is good survey weather, with probability weather_good_probability[H], and W=1 is poor survey weather. Visits have independent W values conditional on H. Survey weather is distinct from H.

Conditional on X, H, M, and W, recorded patch detections are independent. For an occupied patch the positive-record probability is logistic(logit(detection[W][i]) + detection_shift[m]); for an empty patch it is false_positive[W]. Historical visits and the future basic survey use these parameters. The future intensive survey substitutes intensive_detection and intensive_false_positive, with the same hypothesis detection shift and weather distribution. A positive record is not certain occupancy.

Each year also has one regional water report, independently of all patch records conditional on H. The probability of report 1 is water_report_dry_probability[H]. Report 0 is its complement. There is one water-report likelihood factor per year, not one per visit. A JSON null is an unobserved result, and its likelihood contribution is one. Missingness after year 1 is independent of M, state, and observation outcomes; the missingness pattern carries no additional information. Both visits and the water report are complete in years 0 and 1.

## How the archive was selected

The prior weights in model.json belong to the following sampling experiment. Draw M once from those weights. For each of the six network records, independently draw a full history under M until it meets the retention rule, then keep that history and discard all earlier attempts. The number of rejected attempts is not supplied and is not an observation. The focal network is designated in advance, not chosen by its final-year outcome.

The retention event A is at least one recorded positive patch result among the eight patch results in year 0 and the eight in year 1. A water report does not qualify a record for retention. False positive patch records do qualify. Every supplied record meets A. Every supplied record is one of these retained draws, the focal record included. The raw initial distributions above apply inside the retention experiment exactly as they do elsewhere.

Condition the focal network's final historical state jointly with M on the entire archive. The final historical census is planning census t=0. Other networks inform M but do not become additional patches in the recovery plan.

## Management and uncertainty

The decision horizon is six annual transitions, giving censuses t=0 through t=6. At t=0 select either no restoration or one patch to restore, and reserve either a basic or an intensive survey at t=3. Initial restoration is effective for transitions 0 to 1, 1 to 2, and 2 to 3 and stays effective thereafter. Reserving a survey immediately incurs its cost. There are no new observations at t=1 or t=2.

At t=3, after the third ecological transition, receive exactly one patch-survey visit and one water report. Both are complete. Observation code o is patch_detection_mask + 16*water_report, from 0 through 31. Choose zero, one, or two previously unrestored patches in response to that code. Those projects are effective for transitions 3 to 4, 4 to 5, and 5 to 6. There are no further management decisions or observations. A policy must give one deterministic second-stage choice for every possible code. No randomization is allowed.

For every observation code, the sum of initial restoration cost, survey cost, and second-stage restoration cost must be at most 7 budget units. Project costs are incurred once, regardless of occupancy, and unused budget has no terminal value. A patch cannot be restored twice. These are constraints on every branch, not on expected spending.

The three named scenarios specify alternative future hydrology and site-specific survival responses. Use the `first` hydrology matrix for the first three transitions and `second` for the last three. Each scenario's survival shift applies throughout. They do not alter the historical likelihood. One scenario governs the entire future, and it is not revealed. There is no prior over scenarios. In each scenario, average over the joint posterior of M and the current state and over all future ecological and observation randomness. M itself remains fixed. Minimize the largest of the three resulting collapse probabilities using a single initial choice and a single observation-to-action table. Neither the scenario nor M can be chosen anew after an observation.

Collapse means that at least one adjacent pair of censuses in t=0,...,6 has all four patches empty at both censuses. An empty t=0 counts as the first census of a possible pair, but no pre-t=0 census counts. Once this event has occurred it remains a failure even if immigration later recolonizes the network. The event need not be observable to managers. Future observations are still generated and actions still follow the same table on paths where collapse has already happened. This is a sustained-absence objective, not a claim that regional biological extinction is irreversible.

## Numerical and output requirements

Write the three files specified in instruction.md, with the structures in output_schema.json. The posterior array uses hypothesis order M0,...,M5 and state index 16*H+mask. Include zero-probability states rather than dropping them. Every numeric output must be finite. Probabilities must lie between zero and one, allowing only 1e-12 of floating-point boundary error. Required distributions must sum to one within 1e-8. Extra explanatory fields are allowed but do not replace required fields.

For any admissible policy, the largest of its three scenario risks is at least the average of those risks under any weighting of the scenarios, and that average is in turn at least

    sum over observation codes o of min over feasible additions a of sum over scenarios k of w[k] * P(o and collapse | initial choice, addition a at o, scenario k)

for weights w on the three scenarios. Report in `scenario_weights` a weighting that makes this bound as large as it can be made. The reported weights are checked by evaluating that bound from sealed coefficients; a weighting short of the best available one is rejected. Weights concentrated on a single scenario do not attain it.

The policy table has all 32 observation codes exactly once. A second-stage action is an added patch mask, not the cumulative restored mask. The result's three scenario risks must agree with an independent evaluation of the submitted policy within absolute error 1e-6. Its worst risk must be no greater than the independently established optimum plus 1e-5. Multiple policies can satisfy this tolerance; no particular policy text, solver, or tie-breaking convention is required.

The audit file records all ten possible initial choices and their feasible additions. For each it gives branch probabilities P(o | archive, initial choice, scenario) and joint losses P(o and collapse | archive, initial choice, specified addition at o, scenario). The latter include paths that collapsed before the survey. Supply every legal addition, including the empty one and dominated choices; the audit is intended to make the calculation inspectable. The numerical checks compare posterior, retention, branch probabilities, and joint losses to independent reference values with absolute tolerance 1e-6. They also check the probability identities just described.

The policy is the outcome to optimize. Audit quantities must reflect the stated scientific model, not quantities from a surrogate model. Any numerical method may be used if its results meet these accuracy requirements. The task has a finite state space and finite observation and action sets; stochastic estimation is not required. The sealed grading process evaluates the JSON artifacts and does not execute submitted code.
