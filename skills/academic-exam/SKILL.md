---
name: academic-exam
description: "Exam preparation across MCQ and SAQ together: printable exam-simulation practice sets (two independent sets A/B, fillable, solutions in a separate PDF, mirrored to the real exam's format), and topic-level consolidation across lectures (integration recall, topic questions, gap audit). Triggers on: practice exam, mock exam, exam-style questions, practice test, printable practice questions, consolidate this topic, finished all lectures in, topic review, /academic-exam."
---

# academic-exam

Toolchain and standards: `../academic-core/` (`standards/mcq-construction.md`, `standards/pdf-design.md`,
`standards/visuals.md`, `standards/filing.md`). Pick ONE mode.

| Mode | Use when |
|---|---|
| **practice** | the student wants something close to sitting the real exam: printable, two independent sets, separate solutions |
| **consolidate** | all lectures in a topic are done and the student needs integration across them |

Quick drills in chat are `academic-mcq` / `academic-saq` — don't reach for the heavier PDF pipeline unprompted.

## Mode: practice

**Gather first**
- Subject, lectures/topics in scope, and the audited notes for each (`academic-notes` first if missing).
- **The real assessment's format** (subject outline or a past paper). It sets the MCQ:SAQ mix: an all-short-answer
  exam gets all short answer, **no MCQ section** — mirror the real exam, don't pad it. Format unknown → ask; if the
  student defers, default to short-answer-only until it is known (adding a format the exam won't have is worse than
  omitting one it will).
- If a past paper or tutorial sheet was supplied: extract its skill coverage and difficulty, but write **original**
  scenarios for both sets — never near-verbatim copies.

**Structure**
- **Two sets (A and B):** same outcome coverage and mark distribution, different scenarios and numbers; never the
  same question twice.
- **MCQ section (if the real exam has one):** built to `standards/mcq-construction.md`; run
  `scripts/mcq/check_answer_pattern.py` and `scripts/mcq/audit_mcq_set.py` per set to `PASS`, then the four reading
  checks.
- **Short-answer section:** structured multi-part (a/b/c) questions with explicit marks, matching the real
  assessment's style — computational or table-based where content is quantitative, prose where conceptual.
- **Fillable:** ruled lines sized to marks (`wblocks.lines(marks=N)`), `fillin_table()` for frequency tables,
  `mcq_item()` with an empty mark-box before each option letter.
- **Solutions in a physically separate PDF:** `mcq_solution()` (letter, justification, why the strongest distractor
  fails), `saq_solution()` (worked answer + one-line mark scheme), `solutions_banner()` ("do not read until attempted").
- **Compute every quantitative question's numbers in a scratch calculation first**; write the question around them.

**Build:** `scripts/worksheet/build_example.py` is a complete worked assembly (question set → both PDFs, verified) —
copy its shape. Use `wblocks.py` builders, never hand-written HTML; render through `render_pdf.py in.html out.pdf
--expect "<marker>" …` with a distinctive marker from each set and from the solutions.
Files: `[Subject] [Topic] — Practice Questions.pdf` and `— Practice Solutions.pdf`.

**Steps:** gather → read notes → compute numbers → write Set A → write Set B (no repeats) → MCQ audit → build the two
PDFs → verify markers → file via `standards/filing.md` (artifact `practice`; confirm the path first) → confirm: sets,
counts, audit result (or "no MCQ section — real exam is all short-answer"), destinations written / skipped (reason).

## Mode: consolidate
1. Read every lecture note in the topic in full.
2. **Cross-lecture active recall:** integration questions that span lectures; same difficulty rule; flag siloed
   thinking (answers that stay inside one lecture).
3. **Topic MCQ:** the per-lecture standard plus cross-lecture items, built to `standards/mcq-construction.md` and
   passing the audit. Cross-lecture items are where length and convergence cueing creep in, because distractors come
   from a wider pool — check those two flaws explicitly. A student who revised only one lecture must not score full.
4. **Topic SAQ:** per-lecture short answers plus **one extended 250–350-word cross-lecture argument question**, each
   with a model answer.
5. **Gap audit across all lectures:** list every concept, theorist, study or distinction that is thin or missing,
   with the lecture it belongs to; flag high-risk gaps. Update the student's spaced-review list if they keep one.
6. Where a printable topic exam is wanted, switch to **practice** mode with all the topic's lectures in scope.
7. File via `standards/filing.md` (artifact `consolidate`): `Topic MCQ.md`, `Topic SAQ.md`, `Gap Audit.md`; confirm
   the path first. Confirm: counts, audit result, destinations written / skipped (reason).
