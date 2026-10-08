---
name: academic-summary
description: "Write the exam-ready summary of one lecture as its own 1–2 page file, compressed from the audited note: core ideas, must-know definitions, frameworks at a glance, key studies, commonly-confused distinctions, connections. Runs automatically after academic-notes or on request. Triggers on: exam summary, summarise this lecture for the exam, one-pager for, cheat sheet, lecture summary, /academic-summary."
---

# academic-summary

Toolchain and standards: `../academic-core/` (`standards/pdf-design.md`, `standards/filing.md`).

**Input:** the audited note from `academic-notes`. Never summarise from raw slides, and add nothing the note does
not support. The note is the source of truth; the summary compresses it. No audited note → run `academic-notes`.

## Shape (1–2 pages, fixed)
```
---
type: exam-summary
subject: <CODE>
lecture: <n>
source_note: "Lecture <n> — <Title>"
title: "Lecture <n> — <Title> · exam summary"
subtitle: "<CODE> — <Name>"
---
## core ideas              3–6 bullets: the lecture's argument in plain words
## must-know definitions   **term:** definition (exact wording where the examiner expects it)
## frameworks at a glance  table: framework · theorist/year · what it explains · when to use · limitation
## key studies             one line each: study — finding — why it matters
## commonly confused       table of the distinctions examiners test
## how it connects         earlier/later lectures and the subject spine
```
Rules: spelling and case per config · **no exam checklist** · no process narration · no new facts · reuse the
note's figures by reference only where a framework is clearer drawn than tabled · must fit two printed pages.

## Steps
1. Read the audited note in full (a partial read produces false gaps).
2. Compress to the shape above; every line must be traceable to the note.
3. Render: `python3 ../academic-core/scripts/pdf/md_to_pdf.py summary.md summary.pdf --doc-label "<CODE> · exam summary" --kicker "<CODE · NAME · LECTURE n>" --no-abstract --expect "<distinctive phrase>"`
   Check the page count (`pdftotext summary.pdf - | grep -c $'\f'` → ≤ 1 form feed means ≤ 2 pages); trim if over.
4. File per `standards/filing.md`, artifact `summaries`: `Lecture [X] — [Title] — Exam Summary.{md,pdf}`; confirm the
   path first; never overwrite without asking. Link it from the note's `## related` if the note is yours to edit.
5. Confirm: written to [paths] / skipped [why]; pages; anything not verified.
