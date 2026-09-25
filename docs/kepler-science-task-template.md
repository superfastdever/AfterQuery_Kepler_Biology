## Task Template

Updated Sep 16

**Kepler SCIENCE TASK TEMPLATE**

A fill-in guide for building a task. Replace every <...>. Delete the guidance notes (lines starting with NOTE:) before submitting.

**0\. ONE-PARAGRAPH PITCH (write this first)**

-   Workflow: <What a practitioner in this field actually does, in one sentence. "Reduce X into Y, correcting for Z, and decide W.">
    
-   Who does this: <Role and setting. "A core-facility analyst after an instrument service.">
    
-   The hard part: <The one or two judgment calls that separate an expert from a careful generalist.>
    
-   What a wrong answer looks like: <The plausible-but-wrong route an agent will take, and why it fails.>
    

NOTE: If you cannot name a real judgment call here, the task will grade as implementation. Stop and redesign.

NOTE: If the hard part is a convention only you know, it is not a judgment call. Either make it discoverable from the data or state it.

**1\. DIRECTORY LAYOUT**

tasks/<domain>/<field>/<task-name>/

task.toml

[instruction.md](http://instruction.md)

[README.md](http://README.md)

environment/

Dockerfile

data/ (agent-visible inputs only)

solution/

[solve.sh](http://solve.sh) (oracle entry point)

<solver files>

tests/

Dockerfile

[test.sh](http://test.sh)

test\_<name>.py

<held-out inputs and truth; never copied into environment/>

authoring/

provenance/ (generators, source URLs, checksums, dev truth)

evidence/ (calibration runs, independent implementation, ablation ladder)

**2\. TASK.TOML**

schema\_version = "1.4"

artifacts = \["<absolute path of every file the verifier reads>"\]

\[task\]

-   name = "terminal-bench-science/<task-name>"
    
-   description = "<one sentence, same as the pitch workflow line>"
    
-   authors = \[{ name = "<you>", email = "<email>" }\]
    
-   keywords = \["<field term>", "<method term>", "<data type>"\]
    

\[metadata\]

-   author\_name = "<you>"
    
-   author\_email = "<email>"
    
-   author\_organization = "<org or Independent Researcher>"
    
-   domain = "<life-sciences | physical-sciences | earth-sciences | mathematical-sciences | engineering-sciences>"
    
-   field = "<field>"
    
-   subfield = "<specific subfield>"
    
-   expert\_time\_estimate\_hours = <honest number>
    
-   relevant\_experience = "<what you have personally done that qualifies you to author this>"
    
-   conflicts\_of\_interest = "None"
    

\[verifier\]

-   timeout\_sec = <seconds>
    
-   environment\_mode = "separate"
    

\[verifier.environment\]

-   network\_mode = "no-network"
    

\[agent\]

-   timeout\_sec = <seconds; size to the real work, not padded>
    

\[environment\]

-   cpus = <n>
    
-   memory\_mb = <n>
    
-   storage\_mb = <n>
    
-   gpus = 0
    
-   network\_mode = "public"
    

NOTE: expert\_time\_estimate\_hours is checked against observed agent solve time. A 20-hour claim on a task agents finish in 20 minutes is flagged every time.

**3\.** [**INSTRUCTION.MD**](http://INSTRUCTION.MD)

Keep it under about 400 words. Every sentence should be one an agent needs.

<!-- harbor-canary GUID <guid> -->

Context

<2-4 sentences: the setting, what was collected, what went wrong or what is unknown. Written as a colleague would brief you, not as a spec.>

Inputs

<Absolute path of each input, one line each, with what it contains. Point to any data README for formats and conventions.>

Deliverable

<Absolute path of each output file, its exact format (columns, keys, units, precision), and what each field means.>

What is graded

<Name the metrics that gate the result and what they measure. Do NOT give thresholds, verifier formulas, or the scoring algorithm.>

Notes

<Any non-conventional choice the agent cannot infer: units, sign convention, tie-break rule, reference frame, coordinate origin, rounding precision. If a choice affects grading and is not derivable from the data, it goes here.>

You have <agent.timeout\_sec> seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.

NOTE: Test: hand the instruction and the data to a peer in your field with no other context. If they ask a question you have to answer verbally, that answer belongs in the instruction or a data README.

NOTE: Do not describe the method. Describe the outcome. If you find yourself writing the fitting procedure, you are handing over the task.

**4\. ENVIRONMENT/**

Dockerfile:

FROM ubuntu:24.04

ENV DEBIAN\_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y <packages> && rm -rf /var/lib/apt/lists/\*

RUN pip install <pinned==versions>

COPY data /root/data

data/:

\- Agent-visible inputs only. Never truth, never held-out cases, never verifier helpers.

\- Include a short README.txt or <instrument>.md documenting formats, units, and any convention the agent must know. This is the right place for "the logger records X in local time" or "column Y is a half-chord."

\- If the task is a repair, the starter code lives here and must run (and fail) as shipped.

NOTE: Anti-leak check: grep environment/ for every number in tests/. Any hit is a leak.

**5\.** [**README.MD**](http://README.MD)

Reviewers read this before anything else. Four sections, all required.

_Difficulty_

<What makes this hard for an expert, in terms of decisions rather than steps. Name the plausible wrong route(s) and what an agent that takes them will produce.>

_Reference solution_

<How the oracle solves it, at the level of choices made. State plainly that other valid strategies exist and the verifier does not require this one.>

Verification

<For each gate, list on one line: gate name, threshold, reference worst case, independent implementation worst case, nearest wrong route, and one line on why the threshold sits there.>

<State how many seeds or instances the calibration used.>

Ablation ladder

<For each intended step, what happens to the graded numbers if it is skipped. List each route on one line: route name, value of each gate, passes yes/no. Include full reference, each skipped step, and a naive baseline.>

NOTE: If you cannot fill in the independent implementation, write one. A second solver by a different route is the single strongest piece of evidence a task can carry.

NOTE: If any correct route sits within 1.5x of a gate, the gate is inside method noise. Widen it or change what you grade.

**6\. SOLUTION/**

[solve.sh](http://solve.sh):

#!/bin/bash

set -euo pipefail

cd /root

python3 /solution/[solve.py](http://solve.py)

\- Must score 1.0 on every run. Fix seeds, avoid wall-clock dependence.

\- Should be the solution you would actually write, not one tuned to the verifier. If the oracle only passes because it starts near truth or freezes a parameter, the gate is too tight.

**7\. TESTS/**

Dockerfile:

FROM python:3.11-slim

RUN pip install --no-cache-dir pytest==8.4.1 pytest-json-ctrf==0.3.5 <other pinned deps>

RUN mkdir -p /root/results /logs/verifier

COPY . /tests/

[test.sh](http://test.sh):

#!/bin/bash

set -euo pipefail

pytest --ctrf /logs/verifier/ctrf.json /tests/test\_<name>.py -rA

test\_<name>.py should:

\- Read only declared artifacts.

\- Gate on the core scientific claims. Report everything else as diagnostics to a separate metrics.json.

\- Compare floats at a tolerance the science supports. Never at machine epsilon. Never on a rounded-vs-unrounded consistency check the instruction did not state.

\- Parse defensively: normalize keys, accept 100 and 100.0, strip whitespace. A correct answer in the wrong spelling is your bug, not the agent's.

\- Write exactly 0 or 1 to /logs/verifier/reward.txt.

\- Re-run the agent's code on held-out instances where possible, so a hardcoded answer to the visible case scores 0.

NOTE: Prefer "fraction of held-out cases within tolerance at least X" over "every one of N exact fields." All-or-nothing over many fields means one convention slip zeros a correct solution.

**8\. AUTHORING/**

provenance/: generator script, seed, source data URLs and checksums, dev-set truth. Enough for a maintainer to regenerate.

evidence/: calibration run outputs, the independent implementation, ablation ladder outputs, anti-cheat notes. Everything the README cites.

**9\. PRE-SUBMISSION CHECKLIST**

Run these yourself and paste the results into the PR.

\- Oracle 3/3 at reward 1. Nop 3/3 at reward 0.

\- Reference passes on at least 30 regenerated seeds (or all held-out instances) with margin. If it fails any, recalibrate before submitting.

\- Independent implementation passes the same set.

\- Each ablation rung fails as the ladder says.

\- No number in tests/ appears in environment/.

\- Every grading-relevant convention is either derivable from the data or written in the instruction or a data README.

\- Instruction gives no method, only outcome.

\- harbor check -r rubrics/task-implementation.toml is clean.

\- At least 3 agent trials run; harbor analyze findings read and pasted.

\- For every failed trial: what decided the failure? If the answer is a format, a rounding, a sign, a key name, or a threshold inside method noise, fix the task, not the note.

\- Expert-hours estimate is defensible against the observed solve times.

  

**10\. COMMON REJECTION REASONS (from review)**

---

Symptom: 6-7 of 8 passes in under 30 minutes.

Usually means: method handed over, or single-insight task.

Fix: withhold the modeling choice; add a second dependent decision.

---

Symptom: 0-1 of 8 passes with correct science in the failing trials.

Usually means: convention, format, or gate artifact.

Fix: state the convention; widen the gate to method spread.

---

Symptom: reference fails its own reseeds.

Usually means: gate calibrated to one draw.

Fix: multi-seed calibration; gate at several sigma.

---

Symptom: agents recover generator parameters exactly.

Usually means: noise-free synthetic plant.

Fix: add realistic noise, missing metadata, an unmodelled effect.

---

Symptom: failures all trace to one binary choice.

Usually means: task is a coin flip on that choice.

Fix: make it identifiable from data, or grade it with partial weight.

---

Symptom: long instruction full of I/O rules.

Usually means: spec-conformance task.

Fix: cut to outcome; move formats to a data README; tolerate variants.

---

Symptom: author has no stated experience in the field.

Usually means: invented apparatus or textbook exercise.

Fix: start from a workflow you have personally run.