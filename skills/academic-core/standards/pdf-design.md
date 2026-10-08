# Academic PDF design system

**Read this file before generating any academic PDF — notes, summaries, revision sheets.** It is a fixed
pipeline: load it, apply it. Every document must match every other document produced under this system:
same fonts, box style, table rules, diagram palette, and the full two-part title block (title block *and*
scope/outcomes abstract). A document that does not match was described, not applied: discard and redo.

**Content, not framing.** The body begins with the first learning outcome — no preamble, no orientation
paragraph, no "this lecture sits in / opens / is the hinge for / builds directly on". Cross-lecture
connections belong only in `## related` at the end (plus an inline link at the one point a prior concept
is genuinely re-used). `md_to_pdf.py` strips the body `# Title` H1 and every `> ` hub line above the first
heading; it cannot strip a prose preamble — that must not be written into the `.md`.

## Scope

- **In scope:** notes, exam summaries and revision sheets — markdown → HTML builders → weasyprint → PDF.
- **Separate system:** practice-question worksheets (`scripts/worksheet/`: `wblocks.py`, `worksheet.css`) —
  fillable lines, mark-boxes, set dividers, separate solutions PDF.
- Plain markdown→PDF (a flat pandoc export) is never the notes output.

## Toolchain

- **Render path:** content is built as HTML strings by the `scripts/pdf/blocks.py` helper functions,
  styled by the single shared `scripts/pdf/style.css`, rendered by weasyprint. `blocks.render()` wraps
  `weasyprint.HTML(string=…, base_url=…).write_pdf(path)`, sets the Homebrew library path on macOS
  when needed, and **verifies** the output (non-empty, has extractable text, all `expect` markers
  present — a clean render is not proof).
- **Fonts:** `Liberation Serif` / `Liberation Sans` (SIL OFL). Install: macOS `brew install --cask font-liberation`;
  Debian/Ubuntu `apt install fonts-liberation`; Windows: download the Liberation fonts. `make_diagrams.py`
  registers installed Liberation files with matplotlib directly and falls back to DejaVu Sans for diagrams.
  Document text does not fall back gracefully, so keep the font installed — `scripts/doctor.py` checks.
- **Two colour systems that never mix:** the document (text / headings / tables / boxes) is pure
  black / grey / white — **no colour at all**. Diagrams are the only place colour appears, on their
  own restrained palette (below).

---

## Global page setup (`@page`)

```
size: A4;  margin: 25mm 24mm 22mm 24mm;
@bottom-center footer:  <doc label>  ·  string(runhead)  ·  <page number>
  8.5pt, #6b6b6b, Liberation Serif, 0.5pt #cfcfcf top rule, 5pt padding-top, 0.2px tracking
```

**Running-header technique.** An invisible, zero-height `.runhead` marker anywhere in the flow sets
`string(runhead)`; the footer's middle segment always reflects the most recent marker above the
current page — updates automatically across page breaks, no per-page work.

```html
<div class="runhead">Lecture 1 — What Unifies and Distinguishes Science?</div>
```

For notes there is exactly **one** marker, emitted by `doctitle()` and set to the lecture title, so
the footer's middle segment is constant. The `<doc label>` (left segment) is the **subject** — e.g.
`SCI1001 — Introduction to Science` — passed as `document(…, doc_label=…)` and injected as a CSS
variable on `<html>`. (`string()` can't take a runtime argument in weasyprint, hence the var.)

## Document colour + type

Fonts: `"Liberation Serif", serif` everywhere — body, headings, tables, formulas. Exception: the
kicker line and the section tags use `"Liberation Sans", sans-serif`, marking them as metadata.

Greyscale, no exceptions:

```
titles / headings     #0f1115 / #111
body text             #1a1a1a
strong / emphasis     #000
secondary / meta      #333 / #555 / #666
hairlines / rules     #999 / #9a9a9a / #cfcfcf
```

Body: `11pt / line-height 1.55 / justified / margin 6px 0`.
**Body bullets** are en-dash markers with a hanging indent (`ul:not(.checklist) > li::before { "–" }`)
— not discs. `.checklist` and `.lo-abstract` keep their own treatment.

## Title-block components (page 1, in normal flow — never a separate cover page)

**1. Title block** — `doctitle(kicker, title, subtitle)`:
kicker (sans, uppercase, 1.3px tracking, 9pt #555) → **h1** (20.5pt bold #0f1115, line-height 1.25)
→ italic subtitle (11.3pt #3a3a3a) → `hr` (1.1pt #111).

**2. Scope / outcomes abstract** — `lo_abstract(label, items, note=None, ordered=True)`, directly
under the title rule: small-caps sans label (`covers` / `learning outcomes` / …) → ordered (or
unordered) list (10.3pt) → optional italic grey note (9pt) → framed top and bottom by 0.7pt #9a9a9a
rules. **This is where scope/outcomes are stated — never a metadata card, never coloured.**

Both sit in normal flow at the top of page 1; main content begins immediately after. Neither is a
cover page.

## Headings

- **`lo(tag, title)`** — `h1.section-head`: 14pt bold #0f1115, a small-caps tag prefix (`LO1`,
  `LO2a`, `APPENDIX` — any short string, 6px gap), solid 1pt #111 rule underneath, `margin-top 24px`,
  `break-after: avoid`.
- **`h2(title)`** — 12pt bold **italic** #111 — sub-sections within an LO. Italic distinguishes it
  from `lo()` at a glance.
- **`h3(title)`** — 10.8pt bold, normal style.

## Body elements

`ol` padding-left 20px; `li` margin-bottom 3px. `strong` → 700 / #000. `.small` → 8.8pt #666.
`sup` → 7.4pt.

## Callout boxes — ONE style, never per-type colour

`box(kind, title, body_html)` → `<div class="box"><p class="box-title">{title}.</p>{body}</div>`.

- Left border 1.6pt #1a1a1a; 13px left padding; `break-inside: avoid`.
- The label is bold italic, renders as its own run-in line; body follows left-aligned (`.box p {
  text-align:left }`), 4px below.
- **The label auto-gets a trailing `.`** — `definition("demarcation problem", …)` produces the
  literal run-in `Definition — demarcation problem.` then the body. Reproduce that punctuation; it's
  what makes the run-in read as a sentence, not a fragment.
- `kind` is a **semantic tag only** — it carries no CSS. Never add per-kind styling.

Wrappers: `definition(term, …)` · `mechanism(title, …)` · `example(title, …)` (`Worked example —`)
· `case(title, …)` (`Case study —`) · `exam(title, …)` (`Exam note —`) · `nuance(title, …)`.

## Tables — booktabs, rules only, never shaded

`table(headers, rows, caption=None, hl_col=None, tight=False)`.

- 10.1pt; header row bold; top rule 1.1pt #000, under-header rule 0.75pt #000, closing rule 1.1pt
  #000; `td` vertical-align top; `thead` repeats on page breaks.
- **No zebra striping, no cell shading, no vertical rules.**
- `caption=None` → uncaptioned, **unnumbered** (the common case — most reference tables).
  `caption="…"` → auto-numbers `Table N. …`. This asymmetry with figures is intentional — do not
  make tables auto-number.
- `hl_col=<int>` → bolds that column (class `hl`). **Bold only, never colour.** Header cells may be
  `""` (the empty top-left corner).
- `tight=True` → denser padding, 9.6pt.

## Figures — always numbered, caption below, no frame

`figure(src, caption, wide=False)`.

- Auto-numbers `Figure N. <description>`, **restarting at 1 per document** (`reset_counters()`).
- `img` max-height 75mm (`wide=True` → 87mm); no border.
- `figcaption` 9.4pt #333, italic, **left-aligned**, below the image.
- The image carries only axis / data labels — **never an in-image title**, which would duplicate the
  caption.
- Every describable structure (flow, hierarchy, comparison, pyramid, cycle, decision process —
  anything with shape) is rebuilt as an actual figure via `make_diagrams.py`, never left as prose.

## Supplementary components

- `formula(html)` — centred italic 12.3pt.
- `checklist(items)` — `.checklist`, en-dash `::before` (not a bullet or checkbox).
- `quote(html)` — `.quote-block`, left 1.4pt #999 rule, italic #333, 10.2pt.
- `related_end(html)` — the "see also" block at the close of a document: 20px top margin, 9px
  padding-top, 0.7pt #9a9a9a top rule, 9.3pt italic #555, **never boxed**. Lead with `related:`; the
  linked title is bold, the reason follows after ` · `.
- `hr.sect` — 0.6pt dashed #b5b5b5 divider.

## Diagram palette — exact values (`make_diagrams.py`)

```python
INK      = "#1a1a1a"   # body text / primary lines
NAVY     = "#2b3a55"   # the one structural accent — muted, not saturated
GREY     = "#8a8f98"   # secondary lines / muted elements
GREY_L   = "#e4e6ea"   # light fills
GREY_XL  = "#f5f6f8"   # very light fills / figure background band
ACCENT   = "#b8873a"   # sparing highlight ONLY
ACCENT_L = "#efe3c8"   # light tint of the accent
WHITE    = "#ffffff"
```

`plt.rcParams`: `font.family` Liberation Sans, `text.color`/`xtick`/`ytick`/`axes.labelcolor` = INK,
`axes.edgecolor` = GREY, `axes.titlesize` = 0, white axes on a GREY_XL figure band.

Conventions (enforced by review of the rendered image at real size, not by code):

- Rounded rectangles (`FancyBboxPatch`, `boxstyle="round,…"`), never sharp corners.
- Thin lines ~1.0–1.8pt. Clean triangular arrowheads (`-|>`).
- Flat fills only — no gradients, shadows, 3D / perspective.
- **NAVY + GREY do all structural work. ACCENT is spent on EXACTLY ONE element per figure** — the
  thing the figure makes a point about. Never decoration. `ACCENT_L` is the fill for that one
  highlighted node.
- No red / teal / purple, no rainbow category colours — distinguish categories by shape / position
  / label.
- Generous spacing — crowded / overlapping elements is the #1 first-draft failure. **This is now
  enforced automatically, not just by eyeballing** (after a shipped figure had two callout labels collide): call `save(fig, path, ax=ax)` — **always pass `ax`** — which runs `check_layout(fig, ax)`
  before writing the file and **raises** (figure NOT saved) if any two text elements overlap. Use
  `fit_text(ax, xy, text, max_w_frac, ...)` for any free-standing (non-boxed) label instead of a
  bare `ax.text(...)` — it auto-wraps on word boundaries (never mid-word) and auto-shrinks to fit
  its column, the callout-label equivalent of `rounded_box()`'s own auto-fit (box-cell labels have
  always auto-shrunk to fit their box; free labels now do too). Still view the rendered PNG at real
  size as a second check — `check_layout` catches text-vs-text and text-vs-box overlap, not bad
  aesthetic judgement (e.g. a label technically fitting but reading awkwardly).
- Export 220 DPI, tight bbox, ~0.13in pad. Never a title inside the image.
- `new_figure()` for structural diagrams (boxes + arrows); `plot_axes()` for genuine plotted data
  (curves / scatter / bar). Primitives: `rounded_box()` (auto-fits its label), `fit_text()`
  (auto-fits a free-standing label), `arrow()`, `annotate_point()` (the one accent callout),
  `check_layout()` (the overlap gate — called automatically by `save(fig, path, ax=ax)`), `save()`.

## Python helper-function reference (the full content-authoring API — `notes/blocks.py`)

```python
reset_counters()                                  # once per document; zeroes figure + table numbering
esc(s)                                            # HTML-escape a string
p(html) · ul(items) · ol(items) · b(s) · i(s)     # text helpers (so body is never hand-written HTML)

runhead(text)                                     # invisible footer-driving marker (doctitle emits one)
doctitle(kicker, title, subtitle)                 # the title block (+ emits the runhead marker)
lo_abstract(label, items, note=None, ordered=True)# the scope / outcomes abstract
lo(tag, title)                                    # top-level section heading (h1.section-head)
h2(title) · h3(title)                             # sub-headings

box(kind, title, body_html)                       # generic callout; auto-appends "." to the label
definition(term, body) · mechanism(title, body) · example(title, body)
case(title, body) · exam(title, body) · nuance(title, body)

table(headers, rows, caption=None, hl_col=None, tight=False)
figure(src, caption, wide=False)                  # always auto-numbers "Figure N."
formula(html) · checklist(items) · quote(html) · related_end(html)

document(title, body_html, *, doc_label, lang="en-AU")   # wrap authored body in the HTML skeleton
render(html, out_pdf, *, expect=[...], base_url=None)    # -> PDF, then VERIFY (no-op != success)
```

**`md_to_pdf.py`** — the bridge for redoing an *existing* audited note's PDF: converts a copy of the
vault `.md` to this design system (strips `[[wiki-links]]`, maps `## LO<n> — text` → section heads +
seeds the learning-outcomes abstract, `### ` → h2, pipe tables → booktabs [tight from 4 cols],
`> **Label.** …` → callout box, `**Mechanism — X.** …` / `**Worked example — …**` etc. → the
matching box, `![cap](path)` → `figure()`). `python3 md_to_pdf.py note.md out.pdf --kicker "…"
--base-url "<Lectures dir>" --expect "…"`. Figures live in `Lectures/Figures/` and the `.md`
references them relatively; render with `--base-url` = the note's directory.

## Generation process, in order

1. **Load** `scripts/pdf/style.css` + `notes/blocks.py` + `scripts/pdf/make_diagrams.py` before writing
   anything. Reuse them verbatim across every subject and session.
2. `reset_counters()`, then author content by **calling the builder functions** — never by
   hand-writing raw HTML inline.
3. Rebuild any describable structure as an actual figure via `make_diagrams.py` + the palette.
   Every diagram script's `save()` call **must** pass `ax=ax` so the overlap gate
   (`check_layout()`) actually runs — a diagram that doesn't pass `ax` gets no protection. Use
   `fit_text()` for any label not already inside a `rounded_box()`.
4. `render(document(title, body, doc_label=subject), out_pdf, expect=[…])` — always through
   `render()` (it sets the dyld path and verifies). Never a plain markdown export.
5. **Self-check** against the previous documents in the set: same fonts, box style, table rules, diagram
   palette, and the full two-part title block. For any figure generated this run, `Read` the
   rendered PNG (not just grep its caption text in the PDF) and look at it at real size — the
   caption landing in the PDF only proves the image embedded, not that its contents are legible.

## Resolved details

- **Footer left segment** = the subject string, passed as `document(doc_label=…)` (not the kicker, which carries the week).
- **Document wrapper / render** — `document()` + `render()` in `blocks.py`.
- **Page breaks** — `break-after: avoid` on headings, `break-inside: avoid` on boxes and figures,
  `thead { display: table-header-group }` so long tables repeat their header.
- **MCQ options** — consecutive `A. text` / `B) text` lines in the markdown source become one hanging-indent
  `ul.opts` block (no run-on paragraph).
- **File map** — `scripts/pdf/{style.css, blocks.py, make_diagrams.py, md_to_pdf.py}` (this system) ·
  `scripts/worksheet/` (practice worksheets).
