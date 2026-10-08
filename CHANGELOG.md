# Changelog
All notable changes to this project are documented here. Format: Keep a Changelog; versioning: SemVer.

## [1.2.0] — 2026-10-08
### Added
- **Free-chat edition** (`free/`, built by `tools/build_free.py`): 15 self-contained, script-free `-lite` skills
  (one `SKILL.md` each, ≤1200 words) plus 14 paste-in prompt files, for Claude chat that cannot run code or read
  bundled files. Checks become written checklists reported as "checked by reading"; MCQ answer keys are
  precomputed and verified against the real checker; PDFs via a print-ready HTML page; Anki via a TSV block.
- Tests prove every lite skill has no script/file dependency, honest self-audit wording, size limits, a complete
  router, and that all 18 embedded answer keys pass the real pattern checker.

## [1.1.0] — 2026-10-08
### Added
- `academic-visual` (mind map, slide outline, podcast script, video storyboard — text artifacts only),
  `academic-assignment` (research pack with verified-source rules), `academic-stats` (methods and interpretation).
- `md_to_pdf.py` renders fenced code blocks as preserved monospace (mind-map hierarchies keep their structure).
- Artifact keys `mindmap`, `slides`, `podcast`, `video`, `assignment`, `stats` in the resolver.
### Notes
- The suite is now complete: 14 skills + `academic-core` + `scholar` agent.

## [1.0.1] — 2026-10-08
### Added
- `install.py --only a,b,c` installs just the named skills (plus `academic-core`, always); add `scholar` for the agent.
  Unknown names fail with the list of valid ones.
### Documented
- Skills are independent; academic skills share `academic-core`, so hand-copied skills must take it with them.

## [1.0.0] — 2026-10-08
First public package, generalised from a personal study system.
### Added
- Eleven skills (`academic-study`, `-notes`, `-summary`, `-revise`, `-flashcards`, `-mcq`, `-saq`, `-exam`,
  `-recall`, `assembly`, `prompt-making`), a shared `academic-core` toolchain, and a `scholar` agent.
- Claude Code plugin (`.claude-plugin/`), cross-platform installer (`tools/install.py`, `install.sh`) with
  conflict detection, backups and exact uninstall, and per-skill zips for Claude chat (`tools/build_dist.py`).
- Config-driven filing (`resolve.py`) replacing hardcoded paths; configurable spelling, grade band, heading case,
  wiki-links, admin-content exclusion and mirrors.
- `doctor.py` health check; pytest suite (format validator, MCQ gates, resolver, PDF render, figure overlap gate,
  installer, build output, package hygiene).
### Changed vs the source system
- `validate_note.py` now fails notes with content before the first learning outcome, flags administrative content,
  and supports `--heading-case` / `--wikilinks` instead of assuming one house style.
- `md_to_pdf.py` gained a real CLI (argparse), lettered MCQ-option blocks, an H1 title fallback, `--lang`, and
  `--no-abstract`.
- `audit_mcq_set.py` located its answer-pattern checker through a skill folder that no longer exists, so the
  answer-position check was silently skipped (reported as a note, never as a failure); it now resolves the
  checker next to itself and the test suite proves it runs.
- Found and fixed during review: resolver prefix collision (`BIOL100` vs `BIOL1001`), prose "A. …" mis-rendered as an
  option block, uninstall trusting its record file, Windows-hostile zip entry names.
- Removed every external-service dependency (notebook generators, Notion/vault specifics, personal registry).
