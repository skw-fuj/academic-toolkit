#!/usr/bin/env python3
"""Build the free-chat edition: self-contained, script-free `-lite` skills from free/prompts/*.md.

    python3 tools/build_free.py [--out dist/free-chat]

Each output skill is ONE file (SKILL.md) with no references to scripts, other files or other skills, so it works
where code execution and file reading are unavailable. Also writes per-skill zips and one bundle of the prompts.
"""
from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "free" / "prompts"

# prompt file -> (skill name, description with real trigger phrases)
SKILLS = {
    "01-notes.md": ("academic-notes-lite", "Write top-band lecture notes from slides, transcripts and learning outcomes: one H2 per outcome in a fixed spine, mechanisms and studies explained, source visuals tabled or drawn, self-audited by reading. Works without code or files. Triggers on: notes for this lecture, make study notes, turn these slides into notes, HD notes, exam revision notes."),
    "02-summary.md": ("academic-summary-lite", "Write a separate 1-2 page exam summary from finished lecture notes: core ideas, must-know definitions, frameworks at a glance, key studies, commonly-confused distinctions, connections. Triggers on: exam summary, one-pager, cheat sheet, summarise this lecture for the exam."),
    "03-revision-sheet.md": ("academic-revise-lite", "Build a dense zero-loss revision sheet: recall cues, concept matrix, formulas with units, diagrams, a worked problem and examiner traps. Triggers on: revision sheet, cram sheet, revision notes, exam revision, high-density summary."),
    "04-flashcards.md": ("academic-flashcards-lite", "Make exam-grade flashcards from finished notes and output a tab-separated block that imports into Anki, plus a readable list. Triggers on: flashcards for this lecture, make Anki cards, spaced repetition cards."),
    "05-mcq.md": ("academic-mcq-lite", "Write a hard, exam-standard multiple-choice worksheet from finished notes using pre-checked answer keys so the answer pattern is never guessable, with an item-writing self-audit and explained answer key. Triggers on: MCQs for this lecture, multiple choice questions, quiz questions, exam-style MCQ."),
    "06-saq.md": ("academic-saq-lite", "Write top-band short-answer questions from finished notes with model answers and mark schemes, then mark the student's attempt before revealing the answer. Triggers on: SAQs, short answer questions, practice written questions, mark my answer."),
    "07-practice-exam.md": ("academic-exam-lite", "Prepare for exams: two independent practice sets with separate solutions mirroring the real exam format, or topic consolidation with cross-lecture questions and a gap audit. Triggers on: practice exam, mock exam, practice test, consolidate this topic, gap audit."),
    "08-recall.md": ("academic-recall-lite", "Run an interactive active-recall session one question at a time, marking every answer, then a gap audit and spaced-review table. Triggers on: quiz me, test me, active recall, recall session."),
    "09-visual-aids.md": ("academic-visual-lite", "Turn finished notes into a hand-drawable mind map, teach-back slide outline, podcast script or video storyboard (text only). Triggers on: mind map, visual summary, slides outline, podcast script, video script, storyboard."),
    "10-assignment.md": ("academic-assignment-lite", "Plan essays, reports and literature reviews with academic integrity: research question, argument map, annotated sources I supplied, gaps, mandatory counter-evidence, plan, and no invented references. Triggers on: help with my essay, assignment plan, literature review, argument map, annotated bibliography."),
    "11-stats-methods.md": ("academic-stats-lite", "Statistics and research-methods help: which test, study design, power, honest interpretation with effect sizes and intervals, and naming confounders. Triggers on: which statistical test, is this significant, interpret these results, study design, sample size, correlation vs causation."),
    "12-assembly-lite.md": ("assembly-lite", "Deliberate any hard question with a pantheon of analytical minds that keeps dissent and returns a verdict with unresolved tensions, kill criteria and one next step. Triggers on: should I, help me decide, big decision, dilemma, what would the great minds say."),
    "13-prompt-making-lite.md": ("prompt-making-lite", "Draft, critique and harden any prompt: role, constraints, format, examples, self-check, and a re-prompt-waste check. Triggers on: write a prompt for, improve this prompt, draft a system prompt, why does my prompt keep failing."),
    "14-print-to-pdf.md": ("academic-print-lite", "Turn a finished note, summary or revision sheet into a print-ready styled HTML page that saves to PDF from the browser, because free chat cannot create PDF files. Triggers on: make this a PDF, print version, print-ready notes, save as PDF."),
}

ROUTER = ("academic-study-lite", "Front door for the lite study skills: asks for the lecture material and routes to the right lite skill, or runs the full pipeline notes, summary, flashcards, MCQ, SAQ, recall in order. Triggers on: study pack, process this lecture, help me study, which study tool, full study pack.",
"""# academic-study-lite — front door

You are the study router for the lite skills (they work without code or files).
GROUND RULES: never claim to run scripts or create files; say "checked by reading"; never invent citations, figures or studies; subject content only; ask ONE short question when something essential is missing.

If I give no request, show this menu and ask which to run:
| I say | Skill |
|---|---|
| notes for a lecture | academic-notes-lite |
| exam summary / one-pager | academic-summary-lite |
| revision sheet | academic-revise-lite |
| flashcards / Anki | academic-flashcards-lite |
| MCQs | academic-mcq-lite |
| short-answer questions | academic-saq-lite |
| practice exam / consolidate a topic | academic-exam-lite |
| quiz me | academic-recall-lite |
| mind map / slides / podcast / video script | academic-visual-lite |
| essay or report planning | academic-assignment-lite |
| which test / study design | academic-stats-lite |
| a hard decision | assembly-lite |
| write or fix a prompt | prompt-making-lite |
| make it a PDF | academic-print-lite |

FULL PIPELINE (one lecture): 1 ask for subject code and name, lecture number and title, the material (slides/transcript), the learning outcomes (or none), and my spelling (en-AU/en-GB/en-US). 2 notes. 3 summary. 4 flashcards. 5 MCQ. 6 SAQ. 7 offer recall when I am ready. Each step reads the FINISHED NOTES, never the raw slides. Offer revision sheet before an exam and practice exam when a topic is done. Free chat has limited length: if a reply is cut off, say so and continue from where it stopped when I say "continue".
After each step, one line: what was produced, and anything unverified.""")

NOTE_SLOT = ("WHEN THIS SKILL IS USED: gather the items in [square brackets] below by asking me ONE short question, "
             "then follow every instruction. Everything here is self-contained; there is nothing else to read or run.\n\n")


def body_from_prompt(text: str) -> str:
    lines = text.splitlines()
    title = lines[0].lstrip("# ").split("(")[0].strip()
    rest = "\n".join(lines[1:]).strip()
    rest = re.sub(r"\(paste this[^)]*\)", "", rest)
    return f"# {title}\n\n{NOTE_SLOT}{rest}\n"


def write_skill(out: Path, name: str, desc: str, body: str) -> Path:
    d = out / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    fm = f'---\nname: {name}\ndescription: "{desc}"\n---\n\n'
    (d / "SKILL.md").write_text(fm + body, encoding="utf-8")
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist" / "free-chat"))
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    made = []
    for fn, (name, desc) in SKILLS.items():
        made.append(write_skill(out, name, desc, body_from_prompt((PROMPTS / fn).read_text(encoding="utf-8"))))
    made.append(write_skill(out, ROUTER[0], ROUTER[1], ROUTER[2] + "\n"))
    (out / "zips").mkdir()
    for d in made:
        with zipfile.ZipFile(out / "zips" / f"{d.name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            z.write(d / "SKILL.md", f"{d.name}/SKILL.md")
    shutil.copytree(PROMPTS, out / "prompts")
    shutil.copy(ROOT / "free" / "README.md", out / "README-FREE.md")
    for p in sorted((out / "zips").glob("*.zip")):
        print(f"{p.stat().st_size/1024:6.1f} KB  {p.name}")


if __name__ == "__main__":
    main()
