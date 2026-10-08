---
name: academic-saq
description: "Write top-band short-answer questions for a lecture from the audited note, each with a model answer (key terms, named theorists and studies, causal explanation, evaluation) and a mark scheme, then mark the student's attempt before revealing it. Triggers on: SAQs for this lecture, short answer questions, practice questions, exam-style written questions, mark my answer, /academic-saq."
---

# academic-saq

Toolchain and standards: `../academic-core/` (`standards/filing.md`, `standards/pdf-design.md`, `standards/visuals.md`).

## Ground truth
Read the audited lecture note in full before writing any question. Every question and model answer must be
traceable to it (the lecture is the primary source; add outside knowledge only if the note cannot fully answer an
outcome, and name it). No note → run `academic-notes`. Test lecture content, never the lecturer.

## Set design
- **Distribution:** about 30% recall-and-explain, 40% application/mechanism, 30% evaluation.
- **Size:** ≥ 1 per outcome; floor 3 per lecture, dense lectures ≥ 5. Each answerable in 100–200 words at the top band.
- **Model answer per question:** key terms · named theorists and studies (year) · causal explanation of the
  mechanism · evaluation and nuance (limits, counter-position, where the weight of evidence sits) · a one-line mark
  scheme: "what a full-mark answer needs".
- Quantitative questions: **compute the numbers in a scratch calculation first**, then write the question around
  them. Never write plausible numbers and solve afterwards.
- Visuals: where a question turns on a table or figure, supply that stimulus (`standards/visuals.md`).

## Steps
1. Read the note; map outcomes to questions; draft questions, then model answers.
2. Source markdown: frontmatter `title`/`subtitle`/`subject`; questions numbered consecutively; if answers are
   grouped, start them with `## model answers` after a `---` and keep them out of the question pages.
3. Render: `python3 ../academic-core/scripts/pdf/md_to_pdf.py saq.md saq.pdf --no-abstract --doc-label "[CODE]" --kicker "[CODE · SAQ · LECTURE n]" --expect "<distinctive phrase>"`
4. **Fillable worksheet mode** (only when asked for something to print and write on): use
   `../academic-core/scripts/worksheet/` — `wblocks.saq_item()` with ruled `lines(marks=…)`, `student_fields()`,
   rendered through `render_pdf.py`. For a full two-set mock exam use `academic-exam`.
5. File via `standards/filing.md` (artifact `saq`): `Lecture [X] — SAQ Worksheet.{md,pdf}`; confirm the path first.
6. **Marking:** when the student answers, mark their attempt against the model answer **before** revealing it,
   criterion by criterion, then give the estimated percentage against the configured `target_grade`, and the single
   highest-value fix.
7. Confirm: counts, destinations written / skipped (reason), anything unverified.
