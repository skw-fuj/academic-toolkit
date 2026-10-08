---
name: academic-study
description: "Front door for university study work. Give it a lecture (slides, transcript, outcomes) and it runs the full pipeline in order — notes, exam summary, flashcards, MCQ, SAQ, active recall — or routes any single request to the right academic skill. Triggers on: study pack, process this lecture, full study pack, help me study, make notes and questions for this lecture, which study tool should I use, /academic-study."
---

# academic-study — the front door

Toolchain and standards: the sibling skill `../academic-core/` (read `standards/filing.md` for the config).

## Routing
1. **Bare invocation:** show the menu below with one line each and ask which to run. Do not guess.
2. **With a request:** match it to ONE skill and invoke it. If two plausibly match, ask. If none match, say so —
   never improvise a workflow a sibling skill owns.

| The student says | Skill |
|---|---|
| notes for a lecture | `academic-notes` |
| exam summary / one-pager | `academic-summary` |
| revision sheet / cram sheet | `academic-revise` |
| flashcards / Anki | `academic-flashcards` |
| MCQs / quiz questions | `academic-mcq` |
| short-answer questions | `academic-saq` |
| practice exam / mock exam / consolidate a topic | `academic-exam` |
| quiz me / test me / active recall | `academic-recall` |
| mind map / slide outline / podcast script / video script | `academic-visual` |
| essay, report or literature-review help | `academic-assignment` |
| which statistical test / study design / interpret results | `academic-stats` |
| a hard decision, trade-off or stuck point | `assembly` |
| write or improve a prompt | `prompt-making` |

## Full pipeline (one lecture, in order)
Run only after the inputs below are in hand. Each step's output is the next step's ground truth: later steps read
the **audited note**, never the raw slides.

1. **Gather:** subject code and name, lecture number and title, the lecture material (slides/transcript), the
   learning outcomes (or "none supplied"), and where files should go (config; ask once, then remember).
2. `academic-notes` → audited note (the foundation).
3. `academic-summary` → separate 1–2 page exam summary.
4. `academic-flashcards` → card set + Anki deck.
5. `academic-mcq` → pattern-proof worksheet.
6. `academic-saq` → short-answer set with model answers.
7. `academic-recall` → interactive session, **only when the student is ready to be tested** (offer; don't force).
8. **Report:** one line per artifact — written to which path, or skipped and why. Name anything unverified.

Offer `academic-revise` before an exam and `academic-exam` once a topic's lectures are all done.

## Rules
- The note comes first; if no audited note exists, build it before anything else.
- Visuals are a duty across every step (`standards/visuals.md`).
- Statistics and methods questions go to `academic-stats`; essays, reports and literature reviews go to `academic-assignment`.
