# Fields only the repo owner can supply

Everything else in this bundle is built and validated. These ten structure-check
failures are all that stand between it and a packageable submission, and every
one of them is a fact about you or a value that has to be read off the submit
form.

Your own `claude_handoff.md` is why they were left empty rather than filled in:

> Author name, email, and professional experience must come from the user. Do
> not fabricate credentials or certify an unmeasured expert time estimate.
> (line 57)

> Do not invent a machine-readable domain or field slug.
> (line 57)

## 1. Paste into `task.toml`, replacing the empty strings

```toml
author_name = ""
author_email = ""
author_organization = ""          # your institution, or "independent"
author_profile = ""               # ORCID, lab page, or profile URL
conflicts_of_interest = ""        # a real declaration; "none" if there are none

expert_time_estimate_hours = 0    # your honest best case for a domain expert
relevant_experience = ""          # your actual background in this area
```

`relevant_experience` is read first by reviewers and generic text fails review.
The three `*_explanation` fields above it are already filled from your design
package; read them and change anything that does not match your own reasoning,
since reviewers use them to calibrate the difficulty and verification claims.

On `expert_time_estimate_hours`: the reference calculation runs in under a
second once written, which says nothing about how long deriving it takes. Your
`validation_report.md` makes the same point.

## 2. Read off the submit form

Both currently hold their placeholder value in `task.toml`:

- `domain` — displayed on the form as **Life Sciences**
- `field` — displayed on the form as **Ecology & Evolutionary Biology**

The form shows display names while stating that `task.toml` carries **slugs**.
A guess here would be worse than the current failure: it would turn a loud
local error into a silent rejection at submit, which is exactly what
`tools/structure-check.py` exists to prevent. `subfield` is already set to
`metapopulation ecology and conservation decision analysis`.

## 3. `instruction.md`

The file is complete and structurally correct — the mandated closing sentence
is now present and verified at byte level. The prose is still the AI-assisted
draft from your package, and your handoff says it needs your substantive
authorship before submission and must not be relabelled as human-written.

What it has to keep saying, whatever words you use:

- the four input paths under `/app/input/`, by absolute path
- the three output paths under `/app/output/`, by absolute path
- the objective: minimize the worst-scenario probability of two consecutive
  empty censuses across years 0 to 6
- one observation-to-action table across all three futures; the scenario is
  never disclosed
- the budget holds on every branch
- the acceptance tolerances: risks within 1e-6 of independent evaluation, and
  worst risk within 1e-5 of the optimum
- the mandated closing sentence, unchanged

What it must not start saying: the diagnostic, the method, or anything that
points at the intended solution.

## Then

```bash
tools/structure-check.py tasks/2026-09-25/wetland-recovery-policy   # expect 0 failures
tools/validate.sh tasks/2026-09-25/wetland-recovery-policy          # oracle 1, nop 0
tools/package.sh wetland-recovery-policy                            # build/wetland-recovery-policy.zip
```

Submit with **Life Sciences** and **Ecology & Evolutionary Biology** selected,
matching what you put in `task.toml`.
