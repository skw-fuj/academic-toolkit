# Academic Toolkit — Free Chat edition

For Claude chat when it **cannot run code or read bundled files**. Every skill here is a single self-contained
`SKILL.md`: the standards are written into it, the MCQ answer keys are precomputed, and every check that a script used
to do is a written checklist Claude runs by reading and reports honestly ("Checked by reading: …").

## Use it (pick one)
1. **Upload the skills (best).** Settings → Capabilities → Skills → Upload, one zip from `zips/` at a time.
   Start with `academic-notes-lite.zip`, `academic-study-lite.zip`, then whichever you need.
   **If you already uploaded the full skills (`academic-notes`, `academic-mcq`…), turn those off or delete them**:
   they expect scripts and will fail or confuse the lite ones. Keep only the `-lite` versions.
2. **No skills available? Paste a prompt.** Open the matching file in `prompts/`, paste it as your first message, then
   attach or paste your material. Works in any chat, any plan.
3. **A Project (if your plan has them):** paste `prompts/01-notes.md` into the Project instructions and keep the other
   prompt files as Project knowledge; say "use the MCQ prompt" etc.

## Say this
- "Make notes for [CODE] Lecture 3 — [title]" + attach slides and outcomes → `academic-notes-lite`
- "Exam summary of these notes" → `academic-summary-lite` · "Flashcards" · "MCQs" · "SAQs" · "Quiz me"
- "Make this a PDF" → `academic-print-lite` (shows a styled page; browser Print → Save as PDF)
- "Study pack for this lecture" → `academic-study-lite` runs the whole pipeline in order

## What is different from the full toolkit (honest list)
| Full toolkit | Free chat edition |
|---|---|
| validator script fails a bad note | a written self-audit; Claude reports pass/fail by reading — less strict, so re-check headings yourself |
| MCQ answer pattern checked by script | answer key chosen from precomputed keys (each was verified by the real checker); items written to fit it |
| PDF and figures rendered by code | styled HTML page you print to PDF; diagrams as Mermaid or tables |
| Anki .apkg built by code | a tab-separated block you save as `cards.txt` and import (File → Import, separator Tab) |
| files saved to your folders | copy the output into your own notes/Docs; Claude cannot save files |
| searches databases (when available) | assignment planner only uses sources you paste; unverified ones are listed as "to find" |

## Free-chat tips
- Replies can be cut off by length limits: say **"continue"**, or ask for one outcome at a time ("write LO1–LO3 first").
- Put slides in as text or PDF; if images, say "look at every slide".
- Long chat? Start a new one per lecture and paste the finished note in.
- Always spot-check: headings match your outcomes, no invented studies, numbers worked out in front of you.
