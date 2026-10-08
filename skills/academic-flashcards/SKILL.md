---
name: academic-flashcards
description: "Generate exam-grade flashcards for a lecture from the audited note: a card per definition, theorist, study, case, comparison and worked-example specific, audited against the note for coverage, filed as markdown plus a ready-to-import Anki deck. Triggers on: flashcards for this lecture, make Anki cards, generate flashcards, spaced repetition cards, /academic-flashcards."
---

# academic-flashcards

Toolchain and standards: `../academic-core/` (`standards/filing.md`, `standards/visuals.md`).

## Source
The **audited lecture note** is the ground truth — read it in full (a partial read produces false coverage gaps).
No note → run `academic-notes` first. If a card tool or generator is available, treat its output as a *starting
point only* and audit it against the note: generators under-sample, fixating on one content type (e.g. survey
statistics) or on administrative slides while skipping the conceptual frameworks.

## Card design
- One testable idea per card; the front is a question or cue that forces retrieval, not recognition.
- Cover: every definition · every named theorist and citation · every study (aim / method / findings /
  significance / limitations) · every case (background / issue / outcome / significance) · the named specifics of
  each worked example (not only the general concept) · each comparison and commonly-confused pair (a matrix row may
  become a card) · each examiner-level differentiation · 3+ cards per compound outcome.
- **Subject content only** (unless `exclude_admin: false`): no lecturer identity, assessment weighting or logistics.
  A scenario naming "the lecturer" as a stand-in variable is content.
- **Verify, don't assume,** any suspiciously specific auto-generated claim (an exact statistic, a named case, an
  image reference) against the source — extract the PDF text; if it could be image-only, render the page and look.
- **Minimums (a floor):** dense lectures (4+ sections) ≥ 25 cards; lighter lectures (1–3 sections) ≥ 12; ≥ 3 per
  section. Cross-check that every note heading has matching cards.
- Framework shapes and matrices may be cards with a rendered figure on the front (`standards/visuals.md`).

## Steps
1. Read the note; list its headings, tables, studies, cases, examples.
2. Draft the cards; audit coverage against the heading list; add the missing ones.
3. Write the final set as plain `Front<TAB>Back`, one card per line, no header → `cards.tsv`. A multi-line back
   uses `<br>`.
4. Build the deck (needs `pip install genanki`):
   `python3 ../academic-core/scripts/cards/build_apkg.py cards.tsv "[CODE] Lecture [X] — [Title]" "Lecture [X] — Flashcards.apkg"`
   Deck and model IDs derive from the deck name, so re-running updates the deck on import instead of duplicating it.
   If genanki is missing, deliver the TSV (Anki imports tab-separated text directly) and say so.
5. Write the readable markdown version: grouped by outcome, `**front** — back`.
6. File per `standards/filing.md` (artifact `flashcards`): `flashcards/Lecture [X] — [Title]/Lecture [X] —
   Flashcards.{md,tsv,apkg}`; confirm the path; never overwrite without asking.
7. Confirm: card count, deck path, destinations written / skipped (reason), anything not verified.
