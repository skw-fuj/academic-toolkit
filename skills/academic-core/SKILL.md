---
name: academic-core
description: "Shared toolchain and standards for the academic-toolkit skills: note format, PDF design system, visuals contract, MCQ construction standard, filing resolver, validators. Load when another academic skill points here, or when asked how the toolkit works or to run its doctor/health check. Not a study task by itself."
---

# academic-core — shared toolchain & standards

Every other academic-toolkit skill points here. Nothing in this folder is personal: behaviour is set by a small
config file (spelling, grade band, heading case, output folder, optional mirrors).

## Standards (read the one your task needs, not all)
| File | Read it when |
|---|---|
| `standards/note-format.md` | writing or auditing a lecture note; it holds the canonical **notes prompt** |
| `standards/pdf-design.md` | rendering any PDF (notes, summaries, revision) |
| `standards/visuals.md` | deciding what must be a table, diagram or figure |
| `standards/mcq-construction.md` | writing or auditing multiple-choice items |
| `standards/filing.md` | saving anything: config keys, resolver statuses, confirmation gate |

## Scripts (run with `python3`; stdlib unless noted)
| Script | Purpose |
|---|---|
| `scripts/doctor.py` | health check: Python, weasyprint, matplotlib, fonts, poppler, genanki, config |
| `scripts/validate_note.py` | deterministic note-format gate (`--outcomes`, `--heading-case`, `--wikilinks`) |
| `scripts/pdf/md_to_pdf.py` | markdown → house PDF, then verifies content (needs weasyprint) |
| `scripts/pdf/make_diagrams.py` | house figure primitives (needs matplotlib) |
| `scripts/pdf/figures_example.py` | template for a per-subject figure builder |
| `scripts/pdf/md_to_notion.py` | note → Notion-flavoured markdown |
| `scripts/mcq/check_answer_pattern.py` | answer-letter sequence must have no guessable pattern |
| `scripts/mcq/audit_mcq_set.py` | mechanical MCQ audit (length, absolutes, all/none, overlap, positions) |
| `scripts/cards/build_apkg.py` | tab-separated cards → importable Anki deck (needs genanki) |
| `scripts/worksheet/` | fillable practice worksheets (`wblocks.py`, `render_pdf.py`) |
| `scripts/filing/resolve.py` | config-driven destination resolver (`init`, `--subject`, `--artifact`) |

## Operating rules shared by all skills
1. **Never claim what did not happen.** A tool, render, mirror or file counts only if its call appears in the
   transcript. A clean exit code is not proof: verify content (`pdftotext … | grep`, open the file).
2. **Ask, don't guess,** where a value cannot be derived: term, subject code, destination, whether to overwrite.
   Ask before deleting or overwriting anything.
3. **Never fabricate** a citation, study, statistic or figure value. Omit it and say so in chat.
4. **Subject content only** unless `exclude_admin` is false.
5. **Config first.** Read the config (see `standards/filing.md`) for spelling, grade band, heading case, output
   folder. If there is none and files must be saved, run the resolver's `init` after asking.
6. **Chat-only mode.** With no code execution or filesystem, skip scripts: produce the same content in markdown,
   state which checks you did by reading instead of running, and never imply a script ran.
