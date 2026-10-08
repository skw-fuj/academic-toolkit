---
name: academic-mcq
description: "Write a hard, exam-standard multiple-choice worksheet for a lecture from the audited note, built to the NBME/Haladyna item-writing standard, with no guessable answer pattern (checked by script), a one-line justification per answer, and a clean PDF. Triggers on: MCQs for this lecture, make multiple choice questions, quiz questions, exam-style MCQ, test me with multiple choice, /academic-mcq."
---

# academic-mcq

Toolchain and standards: `../academic-core/`. **Read `standards/mcq-construction.md`** (the named testwiseness-flaw
table, structural conventions, 9-point audit) before writing a single item.

## Ground truth
Read the audited lecture note in full. Every outcome gets coverage and every item must be checkable against it. No
note → run `academic-notes`. **Test lecture content, never the lecturer:** no item about who teaches, their bio or
contact details (assessment facts are fair game only if the note covers them and `exclude_admin` is false).

## Writing the set
- **Count:** ≥ 3 per outcome; floor 15 per lecture, dense lectures ≥ 20. Mix about 40% recall, 35%
  application/mechanism, 25% evaluation/contested.
- **Format:** one-best-answer; a closed lead-in stem answerable with the options covered; 4 options (3 is allowed
  when only two distractors are genuinely plausible); homogeneous in length, grammar, specificity; logical order
  where one exists; one testing point per item; prefer a short applied vignette over bare recall.
- **Distractors encode real misconceptions** drawn from the note's confusable concepts, adjacent terms and common
  student errors — never filler. No "all/none of the above", no absolutes or hedges as a tell, no vague frequency
  words, no negative stems unless bolded and rare.
- **Stimulus:** where an item turns on reading a table or figure, generate that stimulus (`standards/visuals.md`).
- Final read: cover the stems and read only the options — no option should be identifiable as correct in isolation.

## The answer-sequence gate (mandatory — run it, don't eyeball it)
Hand-balancing letters by eye fails: one real worksheet had 14 of 22 answers on "B", and a hand-fix that fixed the
frequency still repeated the bigram "CD" four times.
1. List the correct letters in order, e.g. `C,D,C,A,D,A,C,D,A,B,C,B,D,B,D,B,A,C,B,C,A,B`.
2. `python3 ../academic-core/scripts/mcq/check_answer_pattern.py "<sequence>"`
3. On `FAIL`, reorder the flagged items' options (correct text moves; distractors keep their relative order) and
   re-run until `PASS`. The final worksheet's letters must equal the sequence that passed.

## The mechanical audit
Write the set as JSON `[{"stem": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "answer": "C"}]`
and run `python3 ../academic-core/scripts/mcq/audit_mcq_set.py set.json` — length cueing, absolute/hedge words,
all/none, numeric-range overlap, and the position check. Then do checks 3, 7, 8, 9 (grammar fit, distractor
plausibility, cover-the-options, cross-item independence) **by reading**. Present the set only after all nine pass.

## Layout (markdown source → PDF)
- Frontmatter `title`, `subtitle` (code — lecture), `subject`.
- Meta line `*N questions · answer key on final page*`; an **Instructions** line ("Select the single best answer
  for each question") and an italic line naming the outcomes covered.
- Questions numbered consecutively; bold number; options as consecutive lines `A. text` / `B. text` — the bridge
  renders them as one hanging-indent block (never a run-on paragraph).
- One `---` rule is not a page break; the answer section starts with `## answer key and explanations`, then per
  question `**Q[N]. Correct answer: [X]**` and one tight paragraph: why it is right and why the strongest
  distractor is wrong.
- Render: `python3 ../academic-core/scripts/pdf/md_to_pdf.py mcq.md mcq.pdf --no-abstract --doc-label "[CODE]" --kicker "[CODE · MCQ · LECTURE n]" --expect "Correct answer"`
  then `pdftotext` and confirm each option A–D appears on its own line.

## File and mark
File via `standards/filing.md` (artifact `mcq`): `Lecture [X] — MCQ Worksheet.{md,pdf}`; confirm the path first.
If the student answers in chat: **mark before revealing the key**, then give the estimated percentage against the
configured `target_grade`. Confirm: counts, audit result, destinations written / skipped (reason).
