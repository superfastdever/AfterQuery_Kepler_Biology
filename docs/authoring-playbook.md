# Humanization and Task-Authoring Playbook

Built from measured pass and fail results across three PDF-based authoring tasks
(NHANES bone density, NCHS fetal mortality, MMWR organ donor guideline) and the
revision history of AQ-04742. Every rule below is tied to an outcome that was
actually observed, and each one is labelled so a future reader can tell evidence
from inference.

---

## 0. The one-page version

1. **Structure first, words second.** Most failures were the shape of the text, not its
   vocabulary. Rewriting sentences inside a failing structure never worked.
2. **Three registers, not one.** A short first-person prompt, a long expository answer and
   a method write-up each pass in a different register. Using one register for all three
   fails.
3. **Plain beats polished, and polished beats ornate.** Adding literary flourishes to
   "humanize" a text measurably made it worse.
4. **Corrections are surgical.** Fix meaning, arithmetic, population, reference, units.
   Never touch phrasing that is merely different from your own.
5. **One lever per difficulty run.** Change one thing, re-run, read the per-try failures,
   then change the next thing.
6. **No em dashes, no decorative symbols, no markdown in fields.** See 2.5 for the full list.

---

## 1. What "AI-sounding" actually turned out to mean

### 1.1 The measured comparison

On one task the same content existed in two versions: an assistant draft and the user's
rewrite of that draft. Same facts, same order, so every difference is voice. The rewrite
passed; the draft did not.

| Feature | Assistant draft (failed) | Rewrite (passed) |
| --- | --- | --- |
| Mean sentence length | 19.8 words | 25.0 words |
| Sentences of 30+ words | 17% | 33% |
| Contractions per 1,000 words | 19.8 | 1.6 |
| Hedges per 1,000 words | 22.9 | 29.0 |
| Colons per 1,000 words | 16.4 | 10.3 |

**Reading:** the assistant instinct is short, crisp, tidy. The passing text is longer,
more subordinated, less tidy. Crispness is the tell.

### 1.2 The three things that failed, in order of severity

**A. Answer-shaped structure.** Numbered points, each opening with its conclusion, then
its evidence, one point per question asked. Five attempts inside that structure failed,
including one written by the user. Moving to prose that narrates the work in the order it
was done fixed it.

**B. Ornate register.** An attempt to raise "unpredictability" produced "apt to mislead",
"matters stand the other way round", "comes near to conceding", fronted objects and
inversions. This is the register of rewritten AI text and scored worse, not better.

**C. Decoration.** Rhetorical questions used as hooks, asides like "as far as I can see",
invented characters ("our coordinators keep asking"), and idioms for colour. Each addition
raised the score. Measured directly: a version with eight such additions scored higher
than the same text without them.

### 1.3 What passes

Plain, slightly heavy, mildly non-native professional prose:

- Long sentences joined with "and" and "but", fewer commas than an editor would use.
- The same word repeated rather than varied. "Criteria... criteria... criteria", not
  "criteria... measures... items".
- Ordinary vocabulary. "Went down to", "part company", "the other way round" are fine;
  "pared down in scope" and "apt to mislead" are not.
- Occasional loose grammar that does not change meaning: "the reason which the report
  gives", "it needs 14 days", "do not exist anymore".
- First person doing the work: "First I put...", "Then I added up...", "I used the
  sample...".
- Direct address where natural: "if you count from the table alone you get...".
- No contractions in long expository text; a few are fine in a short prompt.

---

## 2. Register by field

Each field has its own target. This is the single most useful table in this document.

| Field | Length | Register that passed |
| --- | --- | --- |
| Prompt | 200 to 350 words | First person, present situation, contractions fine, mixed statements and questions, one honest worry line |
| Golden solution | 600 to 1,300 words | Plain, no contractions, long joined sentences, work narrated in order, numbers inline |
| How you solved it | 230 to 300 words | Same as the gold but looser, decisions only, no findings repeated |
| Rubric rows | 13 to 70 words each | Latinate verbs, "as" and "whereas" for joins, acceptance ranges inside the sentence |

### 2.1 Prompt

**Shape that passed twice on the first attempt:**

> I'm putting together [deliverable] for [audience] using [source]. [Constraint that
> creates stake.]
>
> First I need to know [ask]. [Condition making it determinate.] [Reason it matters.]
>
> [One short worry line.] [Ask.] [Ask.] [Practical consequence.]
>
> [Ask.]
>
> Please set it out as [form] I can [use], one for each question, with [evidence] behind
> each one.

**Rules:**

- Open with what you are making and why accuracy matters.
- State conditions that make the answer determinate: which rows, which age bands, which
  population, what is unavailable.
- Never name the method, the denominator, the table numbers or the figure numbers. Those
  are the answer.
- Keep one short personal line, used once. "The spine worries me more."
- Ask for a compact form. It prevents the truncation that silently fails late criteria.
- Avoid: one question per paragraph, coined hyphen phrases, invented characters, hooks.

### 2.2 Golden solution

- Tell the work in the order it was done. Open with the first step or a one-line verdict,
  never a preview of all findings.
- Put the working on its own lines: `13,106 minus 1,470 = 11,636`.
- Cite inconsistently the way people do: "(PDF page 9)" once, then "page 8", "on pages 6
  and 12", sometimes just the table name.
- Close on a practical consequence, not a recap.
- It must satisfy every rubric row, or Rubric gradability fails later.

### 2.3 How you solved it

- Decisions, not answers. Which base, which rows, what was checked against what.
- Name at most three or four numbers. The gold already carries the rest.
- Never describe a check that was not performed. Personal reactions are fine; invented
  verification is not.

### 2.4 Rubric rows

- Begin "The response should" or "The response should not".
- One requirement per row. Split any "and" that joins two independently checkable things.
- Self-contained. No "this age group", no "that conclusion", no "those two causes".
- Never pair a conclusion with its evidence in one row. Two rows, each standing alone.
- Closed lists of the same kind of value are one requirement and may stay together.
- Put acceptance ranges inside the sentence: "with half a percentage point either way
  acceptable", not "Accept 9% to 11.5%." as a trailing fragment.
- Vary length deliberately: some rows at 18 words or under, some at 35 or over.
- Vary the opening verb: identify, state, show, derive, give, explain, attribute,
  conclude, note, place, recalculate.

### 2.5 Micro-rules: symbols, typography and formatting

These are small and they are the first thing a reader or a checker notices. Every field
in the editor is a plain text box, so anything decorative either fails to render or reads
as machine output.

**Never use**

| Symbol | Why | Use instead |
| --- | --- | --- |
| Em dash | The single loudest AI tell in this work | Comma, full stop, "because", "since", or brackets |
| En dash in ranges | Same family, and it breaks some plain-text fields | Hyphen: `2016-2020`, `4-6 weeks`, or the word "to" |
| Curly quotes and apostrophes | Paste artifacts, inconsistent across fields | Straight `'` and `"` |
| Arrows, bullets, emoji, ellipsis characters | Decorative, never appear in professional prose | Write the words |
| Markdown in editor fields | Fields are plain text; asterisks and hashes show up literally | Nothing. No bold, no headings, no `#` |
| ALL CAPS section headings in a gold | Reads as generated scaffolding | Plain sentences, or nothing |
| Numbered labels like "1. What was dropped." | The answer-shaped structure that failed repeatedly | Start the point with content |
| Trailing fragments like "Accept 9% to 11.5%." | Mechanical, and it made rubric rows read as templated | Fold it in: "with half a point either way acceptable" |

**Numbers and units**

- Thousands separators always: `13,106`, not `13106`.
- Keep the source's own precision, and say where you rounded.
- Distinguish percent from percentage points every time. A rate rises by points, not by
  percent.
- Write ranges as people say them: "2 to 4 weeks", "from 2008 to 2018".
- Working goes on its own line, in words and symbols mixed: `13,106 minus 1,470 = 11,636`.
- Put the unit with the first number of a list, not after each one.

**Citations inside a field**

- Use one form and vary it naturally: "(PDF page 9)" once, then "page 8", "on pages 6 and
  12", sometimes just the table name. A bracketed page after every single claim reads as
  machine precision.
- Say "PDF page" or "page" consistently within a task, and state the viewer-to-printed
  offset in your own notes so citations stay right.

**Spelling and consistency**

- Pick British or American and stay with it inside one field. Mixed spelling inside a
  paragraph is the one inconsistency worth fixing in someone else's text, and even then
  only if they ask.
- Repeat the same term rather than varying it. Synonym variation is a stronger tell than
  repetition.

**Delivery mechanics**

- Never hand text to the user inside a fenced code block. Fences hard-wrap lines, and the
  breaks land inside sentences when pasted into the editor. Give plain paragraphs, or a
  file to copy from.
- Paste into an empty field, then click outside the box before running a check.
- Keep paragraph breaks as blank lines. Single line breaks inside a paragraph survive the
  paste and look like damage.
- Check the pasted text for stray breaks before running the check, particularly after
  copying from a chat window.

---

---

## 3. Correcting someone else's text

When the user rewrites, the assistant checks and corrects. Paraphrasing damages meaning in
a predictable order: **reference, then attachment, then quantity.**

**Always fix:**

1. **Dangling reference.** "The latter is the clinical requirement" pointing at the wrong
   item.
2. **Detached qualifier.** One denominator attached to three percentages when one belongs
   to a different base.
3. **Missing object.** "I summed the six pair tables and put up against the total."
4. **Dropped quantifier.** "compared each pair's loss against its two single losses" where
   the operation is against *the sum of* them.
5. **Wrong operation verb.** "I included each row... thus covering 38 donors" where the
   operation was addition and the 38 is unrelated to the sum.
6. **Unsupported intensifier.** "None of these comes close" when the gap is 4%.
7. **Scrambled word order** that obscures meaning.
8. **Wrong collective noun.** "That adds up to 4.0%, 3.5%, 4.8% and 6.7%" for four separate
   values.
9. **Terminology that points elsewhere.** "the final rule" when the document contains a
   different thing called a final rule.

**Never touch:** sentence order, phrasing, contractions, transitions, formality level,
number formatting, paragraph length, British or American spelling, or a loose construction
that carries no ambiguity.

**Report back:** the corrected text plus a short list separating what was wrong from what
was merely ambiguous, so the user can reject the second group.

---

## 4. Editor mechanics

### 4.1 Field order

Classification and capability tags, prompt, golden solution, write-up, affected pages,
rubric, final checks, difficulty check. Run each field's checks as you go; a failure then
points at one block of text.

### 4.2 Gates and advisories

- **Gate:** prompt quality, human-authored (on prompt, gold and write-up), domain match,
  scenario realism, uniqueness, criteria count, criterion quality, rubric/PDF, prompt/rubric.
- **Advisory:** declared shape, prompt complexity, rubric authorship, rubric gradability,
  deliverable suggestions.

Run **uniqueness first**. It is cheap and it can invalidate the whole concept before you
build a gold and a rubric on it.

### 4.3 Traps in the interface itself

- **"cached" badges.** If every badge reads cached and the message still names the old
  setting, the checker never saw your edit. Clear the field, paste, click outside the box,
  then run. Confirm the badges lose the cached tag.
- **"Could not verify ... a transient error occurred."** Not a verdict. Retry. If it
  persists, report the issue, then override with a reason that says the check never ran,
  the others pass on the same text, and it passed on a near-identical earlier version.
- **Any edit resets the difficulty result.** Make the final edit, then run the check, then
  submit.
- **Affected pages can silently clear.** Re-check the count before submitting.

### 4.4 Declared shape

The checker matches the prompt's own wording against the shape definition, not what the
task needs underneath.

- "work out what its count must be" reads as **Calculation chain**.
- "check whether Table 1 agrees with the text" reads as **Cross-reference**.
- "would 30 days be sufficient to get below one in a million" reads as **Evaluate / judge**,
  because it names a benchmark.

If it flags, change the selection rather than the prompt. Prompt edits reset Human-authored.

### 4.5 Deliverable suggestions

"This deliverable shape is well represented" reads what the prompt asks the reader to walk
away with, not the dropdown. Changing the answer-form selection alone will not clear it.
Change what the prompt asks for: a short list of points, a table of figures, a replacement
paragraph.

---

## 5. Difficulty design

### 5.1 The tiers

Tier 1 an easier model solves it; Tier 2 the standard model solves it sometimes; Tier 3 a
stronger model solves it sometimes and the standard model cannot; Tier 4 harder still. The
target is "solved sometimes but not reliably", roughly one or two tries in five. A task
nothing solves is rejected, not promoted.

### 5.2 Where difficulty must come from

- Numbers the report never prints but that follow exactly from what it does print.
- Figures the report states wrongly, where its own table contradicts it.
- Conclusions with no number attached, which require a direction to be argued.
- Rank orders or margins that rest on one or two units.
- Reading rules that differ between two parts of the same document.

Not from: hidden targets, fussy tolerances, formatting traps, or a method the prompt never
asked for.

### 5.3 The rules that were learned the hard way

1. **Every rubric row must map to something the prompt explicitly asks.** Rows that grade
   your own working method fail across the board and the platform calls them
   under-specified.
2. **Build at least three independent hard points from the start.** "This task's difficulty
   rests on a single point" is a standing warning, and a task with one hard row collapses
   to an easier tier the moment you soften it.
3. **A row that always passes is padding.** It costs a must-pass hurdle and adds nothing.
4. **A row that always fails is broken.** Check whether the fact is findable at all before
   assuming the task is hard.
5. **Two rows that pass or fail together are one row.**
6. **Aim for one solve in five, not three.** Three is the top of the range and leaves no
   margin when the standard model is retried.
7. **Length limits fail criteria silently.** If answers truncate, late rows fail for a
   reason that has nothing to do with difficulty. Ask for a compact deliverable.

### 5.4 Reading a difficulty result

Tally which rows failed on which tries. The pattern names the fault:

- **One row failing on nearly every try:** that row is broken or unrequested. Fix or
  loosen it alone.
- **Different rows failing each try:** the difficulty is real and spread. Leave it.
- **Rows failing late in the answer only:** truncation, not difficulty.
- **"Almost nothing solved it":** the platform's own reading is that something is missing
  or unclear, not that the task is hard.

### 5.5 Changing it

One lever per run. Keep harder rows in reserve at the bottom of the rubric and add them one
at a time. Never fix a failing hard row by deleting it if its cause can be removed instead:
the deletion takes the difficulty with it.

### 5.6 Criterion strength

Separate from tier. The card reports discriminating must-pass criteria against a floor of
two. Rows that vary but are tagged soft do not count. If the floor is not met and two soft
rows are the only ones whose outcome varies, promote those two to Certain dealbreaker; do
not reword them.

---

## 6. Pre-flight checklist

**Before writing anything**

- [ ] Read the source end to end. Note which pages hold the narrative, the tables, the
      figures, the technical notes.
- [ ] Establish the viewer-page to printed-page offset and write it down.
- [ ] Check whether landscape or rotated tables mangle the text layer. If they do, read
      those pages as images.
- [ ] Verify every number you intend to use, and build an evidence ledger: value, page,
      locator, how derived, tolerance.
- [ ] Find the internal cross-checks: totals that reconcile, percentages that reproduce,
      statements the tables contradict.

**Before running checks**

- [ ] Every rubric row maps to an explicit prompt ask.
- [ ] The gold satisfies every row.
- [ ] No row bundles two checks, leans on another row, or pairs a conclusion with evidence.
- [ ] Traps name the concrete wrong value.
- [ ] Row lengths vary; opening verbs vary.
- [ ] No em dashes, en dashes, curly quotes, arrows, emoji or markdown anywhere in a field.
- [ ] Percent and percentage points used correctly throughout.
- [ ] Thousands separators present; spelling consistent within each field.
- [ ] Text pasted from a file, not from a fenced block, and checked for stray line breaks.
- [ ] Affected pages cover everything the answer depends on and nothing it does not.

**Before submitting**

- [ ] All gates green and not cached.
- [ ] Difficulty check run after the final edit.
- [ ] Criterion strength at or above the floor.
- [ ] No override left in place that a rerun could have cleared.

---

## 7. Worked examples of the correction pass

**Ambiguous reference**

> Before: not even the best option of L1 with L2 (498 people).
> After: not even the best option of L1 with L2, which still leaves out 498 people.
> Reason: the bracket reads as the number covered, not the number lost.

**Wrong base attached**

> Before: the 11%, 2% and 4% are each of those who were scanned (13,106).
> After: ... (13,106 for the spine, 13,193 for the femur).
> Reason: the 4% belongs to the femur scans.

**Operation misstated**

> Before: I included each of the rows of Table 1 thus covering 38 donors.
> After: I added up each of the rows of Table 1 across HIV, HBV and HCV; the table covers
> 38 donors.
> Reason: the rows sum to 74 entries; the 38 is the donor count, not the sum.

**Overstatement**

> Before: None of these comes close to 12,865.
> After: None of these reaches 12,865.
> Reason: the best is 498 short, about 4%, which is close.

---

## 8. Things that did not work, so nobody repeats them

- Rewriting a failing text from scratch in a new style. Twenty-plus attempts on one field,
  scores from 43 to 99, no pass.
- Treating the detector score as a dial that responds to small edits.
- Adding deliberate errors or rough edges to sound human.
- Running technical prose through a paraphraser without checking: it damages populations,
  denominators and sign directions while reading perfectly.
- Fixing an advisory flag by editing a gated field.
- Making two changes before re-running a check, which makes the result unattributable.
- Cutting several rubric rows at once after a "too hard" verdict. It overshoots to an
  easier tier in one step.
