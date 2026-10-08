---
name: academic-notes
description: "Write top-band lecture notes from slides, transcripts and learning outcomes: one H2 per outcome in a fixed spine, mechanisms and studies explained, every source visual rendered, validated, and exported as a clean PDF. Triggers on: notes for this lecture, make study notes, turn these slides into notes, lecture notes, HD notes, high distinction notes, exam revision notes, /academic-notes."
---

# academic-notes

Toolchain and standards: sibling skill `../academic-core/`. **Read `standards/note-format.md` first** — it holds the
fixed note shape, the voice rules, the depth floor, and the canonical notes prompt (§7) you will apply.
Config (spelling, heading case, exclude_admin, wikilinks): `standards/filing.md`.

## Inputs
Subject code · subject name · lecture number and title · the lecture material (PDF/PPTX/transcript/readings) · the
learning outcomes if any. Missing one you cannot derive → ask. No outcomes supplied → derive them from the
material's own structure (they become the headings; say nothing about it in the note — tell the student in chat).

## Steps
1. **Slide-by-slide audit (mandatory).** Look at every slide, not just its text. If you have a shell, render the
   PDF to images (`pdftoppm -r 110 -png slides.pdf out/s`; convert PPTX/Keynote to PDF first) and view each. In
   chat, view the attached pages. Write a **slide inventory** in scratch space — never in the note: every theory,
   framework, model, process, diagram, chart, table, figure, worked example and plotted value. Every item must end
   up in the note as the right artifact, or be judged non-examinable (admin only).
2. **Write the note** with the notes prompt in `standards/note-format.md` §7, grounded in the material. Lecture is
   the primary source; add outside knowledge only where an outcome cannot otherwise be answered, and name it.
   Apply visuals per `standards/visuals.md`: comparison matrices and data tables are mandatory where the trigger
   test fires; reproduce every visual the lecture showed as a rendered figure (house primitives, or a Mermaid
   fence in chat), recovering values only from the source — never estimate.
3. **Validate (deterministic gate — do not eyeball it).**
   `python3 ../academic-core/scripts/validate_note.py note.md [--outcomes lo.txt] [--heading-case lower|sentence|any]`
   Exit 0 required. Any FAIL blocks filing: fix and re-run. Warnings are judgement calls (a "no table" warning
   usually means the visuals trigger test was skipped). Supply `--outcomes` (one outcome per line) whenever an
   outcomes document exists. No shell → run the same checks by reading: spine, `## related` closer, no preamble,
   no banned sections, no process narration.
4. **Content audit against the source.** Every outcome present, in order, split where multi-part; per outcome the
   depth floor satisfied; nothing examinable omitted; nothing fabricated; no admin content (unless
   `exclude_admin: false`); grep the draft for `the deck`, `the slide`, `not reproduced here`, `derived`,
   `backfilled` — each hit is rewritten as direct subject matter or deleted. Fill every gap from the source.
5. **Link (only if `wikilinks: true`).** Wrap every defined term, named theorist/study, model, test or key
   terminology in `[[double brackets]]`, first occurrence, over-linking rather than under-linking; `**[[term]]:**`
   for definition entries; add `tags:` to the frontmatter.
6. **Frontmatter:** `title`, `subtitle` (code — name), `subject`, `lecture`, `type: notes`, `source`, `date`,
   `status: complete`, `tags`.
7. **Export the PDF** (PDF is delivered, never a flat markdown print):
   `python3 ../academic-core/scripts/pdf/md_to_pdf.py note.md note.pdf --doc-label "CODE — Name" --kicker "CODE · NAME · WEEK n" --lang <en-AU|en-GB|en-US> --base-url <note folder> --expect "<distinctive phrase>"`
   Then the **figure gate**: for each embedded figure, `pdftotext note.pdf - | grep -c "<caption words>"` must be > 0
   (zero = the image was dropped). Look at page 1 and at every new figure at real size.
8. **File** via `standards/filing.md`: resolve → show the path → wait for a yes the first time per subject →
   write `Lecture [X] — [Title].md` and `.pdf` (and to configured mirrors). Never overwrite without asking.
   Chat-only: deliver the markdown and say where to save it.
9. **Hand-off:** run `academic-summary` for this lecture (the exam summary is a separate file), then offer
   flashcards, MCQ, SAQ and recall.

## Confirm (honestly)
"Note written and validated (exit 0), N figures rendered and verified in the PDF, filed to: [paths] / skipped:
[destination — reason]. Dropped from content: [any admin-only outcome and why]. Unresolved: [anything unreadable
or unverified]." Name anything not actually done.

## Standing rules (full text in `standards/note-format.md`)
Content only, never process narration · begins with the first LO, ends with exactly `## related` · no summary, no
checklist inside the note · never transcribe slides — explain · never fabricate a citation or value.
