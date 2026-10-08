#!/usr/bin/env python3
"""HTML block builders for academic worksheets (MCQ + structured short-answer),
rendered to PDF by render_pdf.py (HTML -> weasyprint).

Design contract: standards/pdf-design.md. White page, black ink,
Carlito, no colour fills, no emoji, no cover page, booktabs tables, numbered
figure captions that restart per document, fillable ruled lines sized to mark
value, MCQ options each with an empty hand-mark box, Set A / Set B on a single
forced page break, solutions in a physically separate document.

Every builder returns an HTML fragment string. Compose them, pass the joined
body to `document()`, write the result to a .html file, then:

    python3 render_pdf.py worksheet.html "Subject L1 — Practice Questions.pdf"

Import as a module or call helpers directly. Stdlib only.
"""
from __future__ import annotations

import html
import math
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_CSS = os.path.join(_HERE, "style.css")
WORKSHEET_CSS = os.path.join(_HERE, "worksheet.css")


def esc(s: str) -> str:
    return html.escape(str(s), quote=False)


# --------------------------------------------------------------------------- #
# document shell
# --------------------------------------------------------------------------- #
def document(title: str, body_html: str, *, subtitle: str = "", kicker: str = "",
             css_files: list[str] | None = None, worksheet: bool = True) -> str:
    """Full standalone HTML document. `css_files` defaults to style.css (+ worksheet.css
    when worksheet=True); pass an explicit list to override."""
    if css_files is None:
        css_files = [STYLE_CSS] + ([WORKSHEET_CSS] if worksheet else [])
    style_tags = "\n".join(
        f'<link rel="stylesheet" href="file://{os.path.abspath(p)}">' for p in css_files)
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
{style_tags}
</head>
<body>
{title_block(title, subtitle=subtitle, kicker=kicker)}
{body_html}
</body>
</html>
"""


def title_block(title: str, *, subtitle: str = "", kicker: str = "") -> str:
    out = []
    if kicker:
        out.append(f'<p class="kicker">{esc(kicker)}</p>')
    out.append(f'<h1 class="doc-title">{esc(title)}</h1>')
    if subtitle:
        out.append(f'<p class="doc-subtitle">{esc(subtitle)}</p>')
    out.append('<hr class="title-rule">')
    return "\n".join(out)


def meta_line(text: str) -> str:
    return f'<p class="meta-line">{esc(text)}</p>'


def student_fields() -> str:
    return (
        '<div class="student-fields">'
        '<span class="field">Name:<span class="fill"></span></span>'
        '<span class="field">Date:<span class="fill"></span></span>'
        '<span class="field">Score:<span class="fill"></span> / <span class="total"></span></span>'
        '</div>')


def instructions(text: str, lo_line: str | None = None) -> str:
    out = [f'<p class="instructions-line">{esc(text)}</p>']
    if lo_line:
        out.append(f'<p class="instructions-line">{esc(lo_line)}</p>')
    return "\n".join(out)


def abstract(paragraphs: list[str]) -> str:
    inner = "\n".join(f"<p>{esc(p)}</p>" for p in paragraphs)
    return f'<div class="abstract">{inner}</div>'


def h2(text: str, lo_tag: str | None = None) -> str:
    if lo_tag:
        return f'<h2><span class="lo-tag">{esc(lo_tag)}</span> — {esc(text)}</h2>'
    return f"<h2>{esc(text)}</h2>"


def h3(text: str) -> str:
    return f"<h3>{esc(text)}</h3>"


# --------------------------------------------------------------------------- #
# fillable elements
# --------------------------------------------------------------------------- #
def lines(n: int | None = None, *, words: int | None = None, marks: int | None = None,
          tight: bool = False) -> str:
    """n ruled answer lines. Supply exactly one sizing basis:
      n      — explicit line count
      words  — expected answer length; ~1 line per 20 words (min 2)
      marks  — mark value; ~2 lines per mark (min 2)
    """
    if n is None:
        if words is not None:
            n = max(2, math.ceil(words / 20))
        elif marks is not None:
            n = max(2, marks * 2)
        else:
            n = 3
    cls = "answer-lines tight" if tight else "answer-lines"
    rules = "".join('<div class="rule"></div>' for _ in range(n))
    return f'<div class="{cls}">{rules}</div>'


def fillin_table(headers: list[str], nrows: int, *, row_labels: list[str] | None = None) -> str:
    """A blank fillable data table (natural-frequency / 2x2 questions). Header row
    printed; body cells empty for the student. `row_labels` pre-fills column 1."""
    thead = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body_rows = []
    for r in range(nrows):
        cells = []
        for c in range(len(headers)):
            if c == 0 and row_labels and r < len(row_labels):
                cells.append(f"<td>{esc(row_labels[r])}</td>")
            else:
                cells.append('<td class="blank"></td>')
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<table class="fillin"><thead><tr>{thead}</tr></thead>'
            f'<tbody>{"".join(body_rows)}</tbody></table>')


def set_divider(set_name: str, sub: str = "") -> str:
    sub_html = f'<p class="set-sub">{esc(sub)}</p>' if sub else ""
    return (f'<div class="set-divider"><p class="set-name">{esc(set_name)}</p>{sub_html}</div>')


def pagebreak() -> str:
    return '<div class="pagebreak"></div>'


# --------------------------------------------------------------------------- #
# MCQ
# --------------------------------------------------------------------------- #
_LETTERS = "ABCDEFGH"


def mcq_item(number: int | str, stem: str, options: list[str]) -> str:
    """Stem + 3–5 lettered options, each with an empty hand-mark box."""
    if not 2 <= len(options) <= 6:
        raise ValueError(f"MCQ item {number}: {len(options)} options (want 3–5)")
    opts = "".join(
        f'<li><span class="opt-letter">{_LETTERS[i]}.</span>{esc(o)}</li>'
        for i, o in enumerate(options))
    return (
        f'<div class="mcq-item">'
        f'<p class="stem"><span class="qnum">{esc(number)}.</span>{esc(stem)}</p>'
        f'<ul class="mcq-options">{opts}</ul>'
        f'</div>')


def mcq_solution(number: int | str, answer_letter: str, justification: str,
                 distractor_note: str, lo_tag: str | None = None) -> str:
    """Answer-key row: letter | one-line justification | why the strongest distractor is wrong."""
    tag = f' <span class="skey">[{esc(lo_tag)}]</span>' if lo_tag else ""
    return (
        f'<div class="solution">'
        f'<p class="skey">Q{esc(number)}. Correct answer: {esc(answer_letter)}{tag}</p>'
        f'<p>{esc(justification)}</p>'
        f'<p class="distractor-note">{esc(distractor_note)}</p>'
        f'</div>')


# --------------------------------------------------------------------------- #
# structured short-answer
# --------------------------------------------------------------------------- #
def saq_item(number: int | str, stem: str, parts: list[dict]) -> str:
    """Multi-part structured question.
    parts: [{"label": "a", "text": "...", "marks": 3, "lines": None|int, "table": html|None}, ...]
    A part gets ruled lines sized to its mark value unless `lines` or `table` is given.
    """
    part_html = []
    for p in parts:
        label = p.get("label", "")
        marks = p.get("marks")
        mk = f' <span class="pmarks">({marks} mark{"s" if marks != 1 else ""})</span>' if marks else ""
        lab = f'<strong>({esc(label)})</strong> ' if label else ""
        part_html.append(f'<p>{lab}{esc(p["text"])}{mk}</p>')
        if p.get("table"):
            part_html.append(p["table"])
        else:
            part_html.append(lines(p.get("lines"), marks=marks))
    return (
        f'<div class="saq-item">'
        f'<p class="stem"><span class="qnum">{esc(number)}.</span>{esc(stem)}</p>'
        + "\n".join(part_html) +
        f'</div>')


def saq_solution(number: int | str, worked_answer: str, mark_scheme: str,
                 parts: list[dict] | None = None) -> str:
    """Full worked answer + a one-line mark scheme ('what a full-mark answer needs: ...').
    `parts` optionally gives per-part worked answers as [{"label","answer","scheme"}]."""
    out = [f'<div class="solution"><p class="skey">Q{esc(number)}.</p>']
    if parts:
        for p in parts:
            lab = f'<strong>({esc(p.get("label",""))})</strong> ' if p.get("label") else ""
            out.append(f"<p>{lab}{esc(p['answer'])}</p>")
            if p.get("scheme"):
                out.append(f'<p class="mark-scheme">Full marks: {esc(p["scheme"])}</p>')
    else:
        out.append(f"<p>{esc(worked_answer)}</p>")
        out.append(f'<p class="mark-scheme">Full marks: {esc(mark_scheme)}</p>')
    out.append("</div>")
    return "\n".join(out)


def solutions_banner(text: str = "SOLUTIONS — do not read until you have attempted both sets.") -> str:
    return f'<div class="solutions-banner">{esc(text)}</div>'


# --------------------------------------------------------------------------- #
# figures
# --------------------------------------------------------------------------- #
def figure(src_or_svg: str, caption: str, *, is_svg: bool = False) -> str:
    inner = src_or_svg if is_svg else f'<img src="file://{os.path.abspath(src_or_svg)}" alt="">'
    return f'<figure>{inner}<figcaption>{esc(caption)}</figcaption></figure>'


if __name__ == "__main__":
    # smoke render
    body = "\n".join([
        meta_line("6 questions · Set A + Set B · solutions in a separate document"),
        student_fields(),
        instructions("Select the single best answer for each multiple-choice question. "
                     "Answer short-answer questions in the space provided.",
                     "Covers: LO1 market entry · LO2 pricing · LO3 customer value"),
        h2("multiple choice", "Set A"),
        mcq_item(1, "A firm sells its existing products into a new geographic market. "
                    "Which Ansoff growth strategy is this?",
                 ["Market penetration", "Market development",
                  "Product development", "Diversification"]),
        h2("short answer", "Set A"),
        saq_item(2, "A subscription business reports 1,200 active customers, 5% monthly "
                    "churn, and $40 average monthly revenue per user.",
                 [{"label": "a", "text": "Calculate the average customer lifetime in months.",
                   "marks": 2},
                  {"label": "b", "text": "Calculate customer lifetime value (CLV), showing "
                   "your working.", "marks": 3},
                  {"label": "c", "text": "Explain one limitation of using this CLV figure to "
                   "set the customer acquisition budget.", "marks": 3}]),
        set_divider("Set B", "Independent second attempt — different scenarios, same outcomes"),
        h2("multiple choice", "Set B"),
        mcq_item(1, "A software company launches a new analytics module for its current "
                    "customer base. Which Ansoff growth strategy is this?",
                 ["Market penetration", "Market development",
                  "Product development", "Diversification"]),
    ])
    out = document("Smoke Test — Practice Questions",
                   body, subtitle="TEST1001 — Worksheet Toolchain",
                   kicker="Practice questions")
    p = os.path.join(_HERE, "_smoke.html")
    with open(p, "w") as f:
        f.write(out)
    print(p)
