# Filing convention

Authoritative for every academic-toolkit skill. Skills cite this file and call `scripts/filing/resolve.py`;
they never hardcode a folder, term, or subject table.

## Config
A small JSON file (copy `config/academic-toolkit.example.json`; `resolve.py init` writes one). Search order:
`--config`, `$ACADEMIC_TOOLKIT_CONFIG`, `./.academic-toolkit.json`, `~/.academic-toolkit/config.json`.

| key | meaning | default |
|---|---|---|
| `output_root` | folder holding your subjects | `~/Documents/academics` |
| `term_folders` | `true` → `<root>/<term>/<subject>/…`; `false` → `<root>/<subject>/…` | `false` |
| `current_term` | active term folder name (term_folders only) | `""` |
| `mirrors` | extra roots to copy into, e.g. an Obsidian vault: `[{"name":"obsidian","path":"~/Vault/Academics"}]` | `[]` |
| `spelling` | `en-AU` · `en-GB` · `en-US` … applied to all generated text | `en-AU` |
| `target_grade` | the top band questions and model answers aim at | `top band (e.g. HD 85%+)` |
| `heading_case` | `lower` · `sentence` · `any` (validator) | `lower` |
| `wikilinks` | `true` → wiki-link key terms (Obsidian graph) | `false` |
| `exclude_admin` | drop lecturer identity, assessment weighting and unit logistics from content | `true` |

## The resolver
```bash
python3 skills/academic-core/scripts/filing/resolve.py --subject BIOL1001 --artifact notes
```
Returns JSON. Exit 0 only on `status: "OK"`; every other status means **ask the student first**.

| Status | Meaning | Required action |
|---|---|---|
| `OK` | one clean match | show path, confirm (first time per subject per session), write |
| `NEEDS_CONFIG` | no config file | ask where files go, run `resolve.py init` |
| `NEEDS_TERM` | term folders on, `current_term` unset | ask which term is active |
| `NOT_FOUND` | no folder for the subject | ask; `--create` builds it only after a yes |
| `COLLISION` | subject exists in several terms/folders | always ask; never auto-pick |
| `OTHER_TERM` | found, but not in the current term | always ask |
| `UNKNOWN_ARTIFACT` | artifact key not registered | use a listed key |

`--create` only after confirmation; it refuses on any other status (except `NOT_FOUND`, where it builds the
new subject folder).

## Artifact → subfolder → filename
| Artifact | Subfolder | Filename |
|---|---|---|
| notes | `notes/` | `Lecture [X] — [Title].{md,pdf}` |
| summaries | `summaries/` | `Lecture [X] — [Title] — Exam Summary.{md,pdf}` |
| revision | `revision/` | `Revision — Lecture [X] — [Title].pdf` (PDF only) |
| flashcards | `flashcards/Lecture [X] — [Title]/` | `Lecture [X] — Flashcards.{md,tsv,apkg}` |
| mcq | `mcq/` | `Lecture [X] — MCQ Worksheet.{md,pdf}` |
| saq | `saq/` | `Lecture [X] — SAQ Worksheet.{md,pdf}` |
| practice | `practice/` | `[Code] [Topic] — Practice Questions.pdf` + `… — Practice Solutions.pdf` |
| recall | `recall/` | `[Date] Recall Log.md` (session log + gap audit) |
| consolidate | `consolidation/` | `Topic MCQ.md` · `Topic SAQ.md` · `Gap Audit.md` |

## The destination-confirmation gate
1. Call the resolver **before** writing anything.
2. First output for a subject in a session: print the resolved path and wait for an explicit yes; reuse the
   confirmed path silently afterwards.
3. Always re-ask on `COLLISION`, `OTHER_TERM`, `NOT_FOUND`, `NEEDS_TERM`.
4. Never create folders unprompted, and never guess a term or year.
5. Never overwrite an existing file without asking.
6. Report honestly at the end: name every destination written and every one skipped, with the reason.

## Mirrors (optional)
If `mirrors` is configured, copy each finished file to the mirror path the resolver returns in `mirror_paths`.
For an Obsidian vault set `wikilinks: true` so notes carry `[[links]]`; the PDF bridge strips them. For Notion
(or any connected docs tool), use the connector if it is available in the session and say so plainly if it is
not — never claim a mirror you did not write. `scripts/pdf/md_to_notion.py` converts a note to
Notion-flavoured markdown.

## Chat-only environments
With no filesystem (Claude chat without code execution), skip the resolver: deliver the finished markdown as the
reply or a downloadable file, and say which files the student should save where.
