# Architecture

```
academic-toolkit/
├─ .claude-plugin/        plugin.json · marketplace.json
├─ skills/
│  ├─ academic-core/      standards/ (5 specs) · scripts/ (validators, PDF, figures, MCQ, cards, filing, doctor)
│  ├─ academic-study/     front door + pipeline
│  ├─ academic-notes · -summary · -revise · -flashcards · -mcq · -saq · -exam · -recall
│  ├─ assembly            deliberation
│  └─ prompt-making       prompt engineering
├─ agents/scholar.md      delegating agent
├─ config/                example config
├─ tools/                 install.py · build_dist.py
└─ tests/                 pytest suite
```

## Design decisions
1. **Skills are thin; standards and scripts are shared.** Each skill states *what to do and in what order* and points
   to `academic-core` for rules and tools. Fix a rule once; every skill inherits it.
2. **Deterministic gates for everything checkable.** Note structure (`validate_note.py`), answer-letter patterns,
   MCQ mechanics, figure label collisions, PDF content, destination resolution are scripts with tests that make
   each one fail on purpose. Judgement (depth, plausibility, grammar fit) stays with the model and is named as such.
3. **The audited note is the single source of truth.** Summaries, cards, questions and recall read the note, never
   the raw slides, so an error is fixed in one place.
4. **Config over hardcoding.** Spelling, grade band, heading case, links, admin policy and destinations are config.
   The shipped defaults are the house standard the toolkit was built on; nothing is personal.
5. **Same skill text in chat and Code.** Relative `../academic-core/` paths work for siblings in Code and the plugin;
   `build_dist.py` vendors the core into each chat zip and rewrites the paths. A test proves every reference resolves.
6. **Never claim what didn't happen.** Skills report written / skipped-with-reason per destination and say when a
   check was done by reading rather than by script.
7. **No external-service dependency.** Notebook generators, note apps and registries are optional mirrors, never
   requirements. Missing optional tools degrade output (PDF → markdown, Anki → TSV) and say so.

## Pipeline data flow
slides + outcomes → **notes** (validated, PDF) → **summary** → **flashcards** / **mcq** / **saq** → **recall**;
`revise` and `exam` read the note(s). Every artifact is filed through `resolve.py` behind a confirmation gate.

## Extending
New skill: `skills/<name>/SKILL.md` (frontmatter `name` = folder, description ≤ 1024 chars with "Triggers on");
reference core with `../academic-core/…`; add an artifact key to `ARTIFACT_SUBFOLDER` if it files output;
`pytest` enforces the rest.
