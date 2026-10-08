# Canonical note format & the notes prompt

The single source of truth for what a lecture note looks like and how it is written. A note that deviates from
this shape is a defect, however good its content. `scripts/validate_note.py` enforces the structural half
deterministically; the judgement half is the audit in `academic-notes`.

## 1 · The shape

```
---  frontmatter  ---                         title · subtitle · subject · type: notes · source · date · status · tags
> part of [[Subject MOC]] · #code #academic   (optional hub line; only when wikilinks are on)

# Lecture <X> — <Title>

## LO1 — <outcome 1, verbatim>
### <sub-section>                              H3 is free-form, led by the content
## LO2a — <part 1 of a multi-part outcome>
## LO2b — <part 2>
## related
```

1. **Heading form is fixed:** `## LO<n> — <outcome text verbatim>`. Case follows `heading_case` (default: lowercase
   except proper nouns, acronyms, scientific terms). Never `## outcome 1`, `## 1.`, a topic-numbered heading, or a
   paraphrase of the outcome.
2. **Multi-part outcomes split** into `LO<n>a`, `LO<n>b`… one heading per part. Never answer two parts under one
   heading; never merge two outcomes.
3. **The note begins with its first LO.** No preamble, orientation paragraph, or "no outcomes document was issued".
4. **Exactly one closing section: `## related`** — sibling, prerequisite and follow-up lectures plus the subject map.
   Every cross-lecture connection lives here, plus an inline link at the single point a prior concept is genuinely
   re-used.
5. **No summary of any kind inside the note.** The exam summary is a separate file (`academic-summary`).
6. **No exam checklist. No section that describes the note** ("outcomes covered", "coverage confirmation").
7. **No outcomes document supplied?** Derive the outcomes from the source's own structure; the derived outcomes ARE
   the headings. Say nothing about the derivation in the note — tell the student in chat.

## 2 · Content scope — subject content only
Excluded, and omitted rather than acknowledged: **lecturer/presenter identity** (bio, credentials, contact),
**assessment structure and weighting** (percentages, due dates, rubrics), **unit logistics** (weekly schedule,
tutorial sign-up, LMS housekeeping). An outcome that is *entirely* one of these is dropped with no heading and no
placeholder; tell the student in chat which one and why. A mixed outcome keeps the content and silently drops the
admin aside. A scenario that names "the lecturer" as a stand-in variable is content — keep it. Genuinely
ambiguous → ask. (`exclude_admin: false` in the config reverses this for subjects where logistics are examinable.)

## 3 · Authorial voice — content only, never narrate the process
A note records the subject matter. It never records how it was made, what you noticed, or what the slides look like.
Remove outright (not softened, not moved into a callout):

- **Process / provenance commentary:** "how the outcomes were derived", "backfilled", "not reproduced here".
- **Extraction-limit flags:** "obscured on the slide", "flagged as external knowledge". If something could not be
  read, omit it and say so in chat.
- **Deck / slide / lecture framing:** "the deck presents X", "the slide shows Y". State the subject directly:
  *"the investment decision is operationalised with the Ansoff matrix"*, not *"the deck operationalises…"*.
- **Scene-setting and cross-lecture positioning:** "this lecture sits in…", "it builds directly on…".

**What stays:** examiner-level differentiations, mechanisms, worked examples, comparisons and commonly-confused
distinctions (they teach the subject), and attribution to a named scholarly source (a citation, not narration).
**The test:** would this sentence still make sense to someone who never saw the slides? Keep it. If it only makes
sense as a comment about the deck or your own working, cut it.

## 4 · The depth floor — the test that replaces a checklist
Judged on clarity and detailed understanding, not word count. Every LO section must let a reader revising *solely
from it* answer recall, application, comparison, evaluation and integration questions. Per LO, all that apply:

- definition of every key term (`**term:** …`; wiki-linked when `wikilinks` is on)
- the mechanism — *why* it works, causally
- theory/model with named theorist and year
- assumptions and the conditions under which it holds
- studies in full: aim / method / findings / significance / limitations
- cases: background / issue / outcome / significance
- worked example — what it illustrates and why that matters
- comparisons and commonly-confused distinctions (as a matrix where the visuals trigger fires)
- examiner-level differentiations — the fine distinction that separates a top band from the next
- strengths, limitations, criticisms, live debates
- applications and implications

**The test:** could a student who never attended sit the exam on this note alone and reach the top band? If any LO
section fails, fill it from the source — do not append a checklist telling the reader what the note failed to teach.

## 5 · Voice — a high-achieving student, not a summariser
- **Never transcribe the slides.** Synthesise each slide into explanation, mechanism, significance and connection.
  A sentence lifted from a slide with no added understanding is a defect. Quote only definitions the examiner will
  expect verbatim.
- **Explain, don't list.** A bullet naming a concept without explaining it is a placeholder.
- **Assert, with grounding.** Attribute to the named source; never "research shows".
- **Argue where the field argues.** Present both sides and say where the weight of evidence sits.
- **Connect** to the previous lecture and the subject's spine — in `## related` and inline links.
- **No filler, hedging or padding.** Every sentence teaches.
- Spelling and case per config (`spelling`, `heading_case`).

## 6 · Callout labels (rendered as boxes by `md_to_pdf.py`)
`**Definition — term.** …` · `**Mechanism — title.** …` · `**Worked example — title.** …` ·
`**Case study — title.** …` · `**Exam note — title.** …` · `**Nuance — title.** …` — a bold run-in label, an
em dash, a title, a full stop, then the body, as one paragraph. Any other `> **Label.** …` blockquote becomes a
generic callout. Maths: `$inline$` and `$$display$$`.

## 7 · The notes prompt (verbatim — use it as-is, whether you write the note yourself or pass it to another model)

Fill the `[ ]` slots. Everything else is fixed.

```
ROLE
You are a top-band student and subject expert writing exam revision notes for Lecture [X] of [subject].

INPUTS
Lecture material: [slides / transcript / readings]. Learning outcomes: [outcomes document, or "none supplied"].

GOAL
Produce notes that let a reader revise solely from them and reach the top band on MCQ, SAQ, essay, scenario and
application questions. Maximise outcome coverage, exam applicability and conceptual understanding. Length is an
output, never a target.

STRUCTURE (strict)
- Begin with the first learning outcome. No preamble.
- Every outcome is an H2: `## LO<n> — <outcome text verbatim>` (case: [heading_case]). Split multi-part outcomes
  into LO<n>a, LO<n>b…, each answered fully under its own heading. Never merge, skip, reorder, renumber or paraphrase.
- If none are supplied, derive them from the material's own structure; the derived outcomes are the headings.
- H3 sub-sections are free-form and led by the content.
- End with exactly one section: `## related`. No summary, recap, checklist, or coverage section anywhere.

CONTENT, PER OUTCOME (include all that apply)
definitions · core concepts · theories/models with theorist and year · mechanisms (causal "why") · assumptions ·
studies (aim, method, findings, significance, limitations) · cases (background, issue, outcome, significance) ·
worked examples (what it illustrates, why it matters) · applications and implications · strengths, limitations,
criticisms, debates · comparisons and commonly-confused distinctions · examiner-level differentiations ·
the content of every diagram, figure and table the source showed.

ANALYTICAL SCAFFOLDING (mandatory)
Two-or-more things to tell apart → comparison matrix (markdown table, discriminators as rows). Figures, thresholds,
benchmarks → data table with units and source. A named model → render its actual shape. A sequence → numbered
process table or flow. "Which method do I use" → decision tree. Every table and figure stands alone: title, labelled
axes, units, source. Never invent a value to fill a cell.

SOURCE RULE
The lecture is the primary source. Add external knowledge only where an outcome cannot otherwise be answered fully,
and name it. Never fabricate a study, statistic or citation: omit it instead.

SCOPE
Subject content only: no lecturer identity, assessment weighting or unit logistics. Never describe the slides, the
lecture, or your own process.

STYLE
Exam-focused, information-dense, logically structured. [spelling]. Explain, do not list. Attribute claims to named
sources. Present both sides of genuine debates.

SELF-CHECK BEFORE OUTPUT
Every heading matches the fixed form · note ends with `## related` and nothing else · every outcome fully covered ·
no summary or checklist · no process narration · every source visual is rendered or tabled · every table and figure
is self-contained.
```

**Why the prompt is shaped this way:** the role and goal come first; the fixed structure is stated as a hard
constraint with the failure modes named (preamble, merged outcomes, summary sections); the content list is the
depth floor in operational form; the source rule and scope rule close the two most common failures (fabrication,
admin content); the self-check is last because models act on the final instruction most reliably.
