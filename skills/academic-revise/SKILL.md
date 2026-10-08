---
name: academic-revise
description: "Produce a dense, zero-loss revision sheet for a lecture as a PDF: active-recall cues, concept and definition matrix, formulas with units, rebuilt diagrams, one canonical worked problem, and examiner traps — built on cognitive-science principles. Triggers on: revision sheet, revision notes, cram sheet, exam revision, active revision, high-density summary, /academic-revise."
---

# academic-revise

Toolchain and standards: `../academic-core/` (`standards/pdf-design.md`, `standards/visuals.md`, `standards/filing.md`).

## Output format — PDF only, in the house design system
The delivered artifact is a **PDF** rendered through `md_to_pdf.py`. The markdown is a scratch working source and is
not filed. No ASCII art in the PDF: every schematic, flow, cycle, hierarchy or timeline is rebuilt as a real figure
(`scripts/pdf/make_diagrams.py`, `save(..., ax=ax)`), then viewed at real size. Reproduce every visual the lecture
showed; plotted data only from values the source gave.

## Why this layout works (the design is deliberate)
- **Cognitive load (Sweller):** cut narrative transitions and filler; chunk into tight units.
- **Dual coding (Paivio, Mayer):** the figure or table sits beside the definition, not in an appendix.
- **Retrieval practice (Dunlosky et al.):** passive re-reading creates an illusion of competence, so every module
  carries recall prompts.
- **Worked-example effect:** the canonical problem shows every step, skipping no arithmetic or logic.
- **Boundary and trap flagging:** top-band marks are won on boundary conditions and fine distinctions.

## Provenance and quality
Record exact provenance: `[Unit] | Lecture [n] | Week [x] | slide/reading range`. Retain 100% of technical depth —
definitions, mechanisms, edge cases, exceptions. Flag how each concept is tested (calculation, compare/contrast,
definition, mechanism, labelling). If a source is ambiguous or a step is missing, **do not guess**: ask with
concrete options.

## Source markdown schema (scratch file; frontmatter is required or the PDF title is "Untitled")
```markdown
---
title: "[Unit Code] Revision Sheet: [Lecture Title]"
subtitle: "Lecture [X] (Week [Y]) — [source reference]"
subject: [CODE]
---
## 1. Active recall anchor
- [ ] **Q1:** core definition or mechanism  ·  **Q2:** comparison of easily-confused concepts  ·  **Q3:** application/edge case
## 2. Concept and definition matrix
| concept | formal definition / mechanism | boundary condition / key nuance |
## 3. Formulas, models and derivations   (omit if purely qualitative)
$$ equation $$ with every variable and unit listed; numbered derivation steps
## 4. Visual schematics and process flows
![caption](Figures/<name>.png)
## 5. Canonical worked problem and examiner traps
**Worked example — [title].** givens → formula and substitution → answer with units and interpretation
> **Exam note — [trap].** the frequent error under time pressure, then the exact correction for full marks
```
Callouts use the house labels (`**Worked example — …**`, `**Definition — …**`, `> **Exam note — …**`).

## Steps
1. Ingest the audited note (or the source) and the outcomes; lock provenance.
2. Extract everything with zero loss; compress into the schema.
3. Build the figures; look at each PNG at real size.
4. Render: `python3 ../academic-core/scripts/pdf/md_to_pdf.py sheet.md sheet.pdf --doc-label "[CODE] — [Subject]" --kicker "[CODE · REVISION · WEEK n]" --base-url <scratch> --expect "<caption words>"`
5. **Quality gate (no-op ≠ success):** `pdftotext` the PDF; every figure caption is present, the title is not
   "Untitled", no raw ASCII box characters remain, LaTeX converted, page 1 shows the full title block.
6. File the **PDF only** via `standards/filing.md` (artifact `revision`): `Revision — Lecture [X] — [Title].pdf`;
   confirm the path; never overwrite without asking.
7. Confirm: PDF written to [paths] / skipped [why]; state that no `.md` was filed.
