# Academic Toolkit

A study system for university students that runs inside Claude. Give it a lecture — slides, transcript, learning
outcomes — and it produces top-band notes, an exam summary, flashcards, pattern-proof multiple-choice questions,
short-answer questions with model answers, practice exams, and an active-recall session. Every artifact is gated by
a deterministic check rather than by good intentions.

Works in **Claude chat** (upload skills) and **Claude Code** (drag-and-drop or plugin).

| | |
|---|---|
| **academic-study** | front door: runs the whole pipeline for a lecture or routes to one tool |
| **academic-notes** | notes with one H2 per learning outcome, mechanisms and studies explained, every source visual rendered, validated, PDF |
| **academic-summary** | the separate 1–2 page exam summary |
| **academic-revise** | dense revision sheet: recall cues, matrix, formulas, figures, worked problem, examiner traps |
| **academic-flashcards** | audited card set + importable Anki deck |
| **academic-mcq** | NBME/Haladyna-standard items, answer-sequence gate, 9-point audit, PDF |
| **academic-saq** | short-answer questions, model answers, mark scheme, marking |
| **academic-exam** | printable A/B practice exams with separate solutions; topic consolidation + gap audit |
| **academic-recall** | one-question-at-a-time retrieval practice, gap audit, spaced-review list |
| **academic-visual** | mind map, teach-back slide outline, podcast script, video storyboard (text artifacts) |
| **academic-assignment** | essay/report/literature-review research pack with verified sources and mandatory counter-evidence |
| **academic-stats** | which test, study design, power, honest interpretation of results |
| **assembly** | a pantheon of analytical minds that deliberates any hard question and preserves dissent |
| **prompt-making** | draft, critique and harden any prompt |
| **academic-core** | shared standards and scripts (not invoked directly) |
| **scholar** (agent) | delegate any study task to a dedicated agent |

## Install

### Claude chat (claude.ai / desktop / mobile)
1. Download the zips in `chat-skills/` (start with **academic-notes.zip**; add the others you want).
2. Settings → Capabilities → Skills → **Upload skill**, once per zip.
3. Start a chat, attach your slides, and say *"make notes for this lecture"*.

Each zip is self-contained. In chat without code execution the skills still work: they write the same content and
state which checks were done by reading instead of by script — they never imply a script ran. With code execution
enabled, the validators and PDF export run for real.

### Claude Code — drag and drop
Unzip `academic-toolkit-<version>-claude-code-dropin.zip` into your home folder (all projects) or a project folder.
That puts `.claude/skills/*` and `.claude/agents/scholar.md` in place. Restart Claude Code.
Prefer conflict detection and backups? Use the installer:

```bash
./install.sh                 # user scope (~/.claude)       python3 tools/install.py on Windows
./install.sh --project .     # this project only
./install.sh --only academic-notes,academic-mcq   # just the skills you want (+ academic-core)
./install.sh --force         # replace existing (old copies are backed up, never deleted)
./install.sh --uninstall     # removes exactly what it installed
```

> **Pick only what you want.** Every skill is separate. The academic skills share one folder, `academic-core`
> (standards and scripts). If you copy skill folders by hand, copy `academic-core` with them; `--only` does this for you.

### Claude Code — plugin
```text
/plugin marketplace add /path/to/academic-toolkit
/plugin install academic-toolkit@academic-toolkit
```
or `claude --plugin-dir /path/to/academic-toolkit` to try it for one session.

## Optional dependencies (for PDF, figures, Anki)
```bash
pip install -r requirements.txt
# macOS:          brew install pango poppler && brew install --cask font-liberation
# Debian/Ubuntu:  sudo apt install fonts-liberation poppler-utils libpango-1.0-0 libpangoft2-1.0-0
# Windows:        install the GTK runtime for WeasyPrint and the Liberation fonts
python3 skills/academic-core/scripts/doctor.py     # tells you exactly what is missing and the fix
```
Notes, questions and cards work without any of this; only PDF/figure/Anki output needs it.

## First run
```text
/academic-study            then attach slides + outcomes, or say:
"Make notes for BIOL1001 Lecture 3 — Cell Membranes and Transport from these slides."
```
It will ask once where to save files, remember the answer, show the destination before writing, and report honestly
what was written and what was skipped.

## Configuration
Copy `config/academic-toolkit.example.json` to `~/.academic-toolkit/config.json` (or run
`python3 skills/academic-core/scripts/filing/resolve.py init --output-root ~/Documents/academics`).

| key | effect |
|---|---|
| `output_root`, `term_folders`, `current_term` | where files go; optional `<root>/<term>/<subject>/` layout |
| `mirrors` | extra roots to copy into (e.g. an Obsidian vault) |
| `spelling` | `en-AU` · `en-GB` · `en-US` … for all generated text |
| `target_grade` | the band questions and model answers aim at |
| `heading_case` | `lower` (default house style) · `sentence` · `any` |
| `wikilinks` | `true` to wiki-link key terms for Obsidian graphs |
| `exclude_admin` | `true` drops lecturer identity, assessment weighting and logistics from notes and questions |

## The standard it enforces
- **One spine:** `## LO<n> — <outcome verbatim>` … `## related`. No preamble, summary, or checklist inside a note.
- **Content, never narration:** no "the slide shows", no process commentary, no cross-lecture scene-setting.
- **Depth floor:** a reader who never attended must be able to sit the exam on the note alone.
- **Visuals are a duty:** comparisons become matrices, models become their real shape, every source figure is
  reproduced — and the figure builder *refuses to write* an image whose labels collide.
- **No guessable MCQs:** answer-letter sequences are checked by script (frequency, runs, cycles, repeated bigrams).
- **Verified, not asserted:** PDFs are re-read for the expected content; "clean exit" is never accepted as proof.
- **Honest reporting:** every run states what was written, skipped and unverified.

## Develop and verify
```bash
pip install -r requirements-dev.txt
python3 -m pytest -q            # format validator, MCQ gates, resolver, PDF, figures, installer, build, hygiene
python3 tools/build_dist.py     # → dist/ (plugin zip, drop-in zip, chat-skills/*.zip, SHA256SUMS)
```
See `docs/ARCHITECTURE.md`, `docs/INSTALL.md`, `docs/ASSEMBLY-VERDICT.md`, `docs/COUNCIL-REVIEW.md`, `CHANGELOG.md`.

## Limits
- It prepares study material from the material you give it; it does not replace attending, reading or thinking.
- It will not fabricate citations or data; where a source is unreadable it omits and tells you.
- Generated questions are practice, not past papers; check the real exam's format and your unit outline.
- Assembly is reasoning support, not professional medical, legal, financial or mental-health advice.

MIT licensed. Third-party attributions in `NOTICE`.
