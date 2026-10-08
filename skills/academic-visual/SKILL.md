---
name: academic-visual
description: "Turn an audited lecture note into alternative study formats: a hand-drawable mind map (indented hierarchy plus Mermaid), a teach-back slide outline with speaker notes, a podcast-style script for listening revision, and a video storyboard script. Text artifacts only — it does not generate audio or video files. Triggers on: mind map for this lecture, visual summary, slides for this lecture, teach-back deck, podcast script, audio revision script, video script, storyboard, /academic-visual."
---

# academic-visual

Toolchain and standards: `../academic-core/` (`standards/visuals.md`, `standards/pdf-design.md`, `standards/filing.md`).
Pick ONE mode. **Source: the audited lecture note** (read it in full). No note → run `academic-notes` first.
Subject content only; test the content, never the lecturer (unless `exclude_admin: false`).
**Honesty:** these modes write *text* artifacts. They do not produce audio, video or slide files. If the student has a
text-to-speech, video or presentation tool, they can feed it the script or outline; never claim a media file exists.

## Mode: mindmap
A navigable hierarchy the student can redraw by hand.
1. Build the tree from the note: root = lecture title → one branch per learning outcome (split compound outcomes at
   the first branch) → key concept → theorist/study, mechanism, limitation or debate. Phrases only, never sentences.
2. Mark contested nodes with `*`; add cross-links as `↔ Node A ↔ Node B — reason` lines under the tree.
3. Cross-check: every outcome heading in the note has a branch; add any node the note covers that the tree missed.
4. Output as a fenced block (monospace keeps the box-drawing characters), plus an optional Mermaid `mindmap` fence:
   ```
   [Lecture Title]
   ├── [LO 1]
   │   ├── [Key concept]
   │   │   ├── [Theorist / study]
   │   │   └── [Limitation / debate *]
   │   └── [Key concept 2]
   ├── [LO 2]
   ↔ Cross-link: [Node A] ↔ [Node B] — [reason]
   ```
5. Verification prompt for the student: "Redraw this from memory, then I'll compare and flag every missing node."
6. Frontmatter `title`, `subtitle`, `subject`; render the PDF with `scripts/pdf/md_to_pdf.py --no-abstract` (fenced blocks
   render as preserved monospace). File as `Lecture [X] — Mindmap.{md,pdf}`, artifact `mindmap`.

## Mode: slides (teach-back outline)
Teaching content back is one of the strongest study techniques; this is the deck for it or for a study group.
1. Keep the note's learning-outcome structure as the slide structure. If the note has none, ask what structure fits
   (topic flow, chronology, concept hierarchy) — do not invent one.
2. One slide = one idea: title that states the claim, ≤ 5 bullets, a table or figure where `standards/visuals.md`'s
   trigger fires, and **speaker notes** carrying the mechanism, the study (aim/method/findings/limitations) and the
   examiner-level distinction.
3. **Excluded from slides entirely:** lecturer bio, assessment weighting and structure, unit logistics.
4. Output markdown: `## Slide n — <claim>` / bullets / `Speaker notes:` paragraph. Check every section of the note has
   a slide; list any under-covered section. File as `Lecture [X] — Slide Outline.md`, artifact `slides`.

## Mode: podcast (script)
A two-voice or single-voice listening script for passive revision (commute, walking).
1. Formats: **deep-dive** (two hosts, plain-language walk through every outcome), **brief** (2-minute summary),
   **critique** (strengths, limits, debates), **debate** (two sides argue a contested point).
2. Cover every learning outcome and named theorist/study, accurately; no filler banter that changes content; spell out
   symbols and formulas as they would be spoken; add a one-line recap after each outcome.
3. Flag anything in the note the script skips. File as `Lecture [X] — Podcast Script.md`, artifact `podcast`.

## Mode: video (storyboard script)
1. Scenes: for each outcome a 20–60 s scene with `VISUAL:` (what is on screen — a diagram, table or build-up of the
   model; whiteboard style suits academic content) and `NARRATION:` (spoken text). Reproduce source visuals as
   described figures; never invent data for a chart.
2. Open with the one question the lecture answers; close with a three-point recap. Target length noted per scene.
3. File as `Lecture [X] — Video Script.md`, artifact `video`.

## Confirm
Which mode, counts (nodes / slides / scenes), coverage check result, destinations written / skipped (reason), and the
reminder that only text was produced.
