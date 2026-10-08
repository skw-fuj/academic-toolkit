# Visuals & analytical scaffolding — the contract

Authoritative for every academic-toolkit skill. Visual and analytical generation is active by default: a skill
does not ask permission to render a table or diagram this contract requires. It asks only when the *form* is
genuinely ambiguous. This file owns *what gets drawn and when*; `filing.md` owns *where output goes*.

## 0 — Reproduce every visual the source showed
If a lecture displayed a diagram, graph, chart, plot, model shape (pyramid / matrix / funnel / cycle / venn /
wheel / tree / flow), map, timeline or table, the note must contain that visual **as a rendered artifact**, not
a `(Figure N: …)` parenthetical describing something the reader cannot see.

- **Data graphs** whose numbers are recoverable → clean chart via `scripts/pdf/make_diagrams.py` (house palette).
- **Framework shapes** → render the actual conventional shape, not only a table.
- **Screenshots / photographs** cannot be reproduced → describe in prose; render any data behind them.
- **Never invent data.** If the numbers are not recoverable, omit the figure and say so in chat — never estimate.
- Every figure: caption, axis/node labels, units, source; one accent element at most; no title baked into the
  image (the caption carries it). Verify by content after render (`pdftotext … | grep`), never by exit code.

## 0a — Verify the shape before you render it
A wrong-but-confident diagram is worse than none: a student revising from it learns the wrong shape.
- **Confident** of the canonical structure (Maslow's hierarchy, marketing 4 Ps, a basic SWOT grid) → render.
- **Not confident** of tier/quadrant/stage count, order or labels → search the web first if a search tool is
  available; otherwise mark the figure `[shape unverified — confirm against the source]`.
- Once verified for a subject, reuse the confirmed shape.

## 1 — The trigger test (a duty, not a suggestion)
| If the content is… | Render it as | Route |
|---|---|---|
| two or more things a reader must tell apart | comparison matrix, discriminators as rows | markdown table |
| figures, thresholds, cut-offs, benchmarks | data table with units + source | markdown table |
| a sequence of stages or steps | numbered process table or flow diagram | table, or `make_diagrams.py` |
| a named model (pyramid, matrix, funnel, canvas) | its actual shape | `make_diagrams.py` |
| the evolution of an idea / dated discoveries | timeline | `make_diagrams.py` |
| "which test / method do I use" | decision tree | `make_diagrams.py` or Mermaid |
| input → transformation → output | pipeline diagram | `make_diagrams.py` |
| a statistical partition (e.g. ANOVA sources of variance) | table first; diagram only to supplement | markdown table |
| a concept map for recall | hierarchy / mind map | Mermaid, or a hand-drawable indented outline |

Every artifact stands alone: title, labelled rows/columns or nodes, units where numeric, and the source.

## 2 — Rendering routes, in priority order
1. **Markdown table** — default. Zero dependency, greppable, survives PDF export, cannot hallucinate a value.
2. **House figure** — `scripts/pdf/make_diagrams.py` → PNG (220 dpi) injected as `![caption](Figures/name.png)`.
   Primitives: `new_figure`, `rounded_box` (auto-fits label), `fit_text` (auto-wraps free labels), `arrow`,
   `annotate_point`, `plot_axes`, `save(fig, path, ax=ax)` (**always pass `ax`**: it runs the text-overlap gate and
   refuses to write a figure with colliding labels). Keep per-subject builders in your own `figures/` folder;
   see `scripts/pdf/figures_example.py`.
3. **Mermaid** — a ```mermaid fence when the diagram must stay editable text (Obsidian, GitHub, Claude chat
   artifacts). Pandoc and weasyprint do not render Mermaid into the PDF: use route 2 for anything exported.
4. **Optional diagram skills** (e.g. a diagram-design or hand-drawn skill, if installed) — only for non-examinable
   decoration; never for figures whose labels carry examinable content.

## 3 — Hard limits
- Never render a figure whose labels carry examinable content through an image-generation model: a generated
  raster can misspell a coefficient or mislabel an axis and the student cannot detect it.
- Never invent data to fill a table. A cell with no source is omitted or marked `—`.
- A diagram never replaces the prose that explains the mechanism; it supplements it.
- No decorative visuals. If it does not make something clearer, it does not go in.
- Never claim a render you did not get. If rendering fails, say so and deliver the source file.
- After a figure renders clean, **look at the PNG at real size**: `check_layout` catches text collisions, not
  bad aesthetic judgement.

## 4 — Per-skill duty
| Skill | Obligation |
|---|---|
| academic-notes | Full trigger test on every LO section; matrices/tables mandatory where they fire; framework diagrams where a named model appears. |
| academic-revise | Every schematic rebuilt as a real figure — no ASCII art in the PDF. |
| academic-summary | Reuse note figures by reference only where a framework is clearer drawn than tabled. |
| academic-flashcards | Visual cards for frameworks; a matrix row may become a card. |
| academic-mcq · academic-saq | Where a question turns on reading a table or figure, generate that stimulus. |
| academic-exam | Cross-lecture comparison matrices are the primary consolidation output. |
| academic-recall | Blank out a matrix or diagram as a retrieval-practice artifact. |
