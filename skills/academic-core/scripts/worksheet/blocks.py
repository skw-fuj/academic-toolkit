#!/usr/bin/env python3
"""HTML block builders for standalone academic NOTES rendered as a print PDF
(academic-notes "PDF output mode" — the alternative to Obsidian filing).

This is the lighter sibling of wblocks.py: title block + learning-outcome
sections + definition lists + figures. No fillable elements, no set dividers,
no solutions. Same design contract (standards/pdf-design.md):
white page, black ink, Carlito, no cover page, no colour fills, booktabs tables,
numbered figure captions that restart per document.

The vault note itself still renders via pandoc -> typst. Use this ONLY when the
deliverable is a standalone document (asked for "as a PDF" / "to print", or no
vault context in the session).

    python3 blocks.py            # writes _smoke_notes.html
    python3 render_pdf.py _smoke_notes.html out.pdf
"""
from __future__ import annotations

import os

from wblocks import (  # noqa: F401  re-exported for callers
    esc, document, title_block, abstract, h2, h3, figure, meta_line,
    STYLE_CSS,
)

_HERE = os.path.dirname(os.path.abspath(__file__))


def notes_document(title: str, body_html: str, *, subtitle: str = "",
                   kicker: str = "Lecture notes") -> str:
    """Notes PDF: style.css only (no worksheet.css)."""
    return document(title, body_html, subtitle=subtitle, kicker=kicker,
                    css_files=[STYLE_CSS], worksheet=False)


def lo_section(lo_tag: str, outcome_text: str, body_html: str) -> str:
    """One learning-outcome section: `## LO<n> — <verbatim outcome>` + its body."""
    return h2(outcome_text, lo_tag=lo_tag) + "\n" + body_html


def definition_list(pairs: list[tuple[str, str]]) -> str:
    """Textbook definition list — bold term, hanging-indented definition below.
    Mirrors the typst `terms.item` styling in header.typ."""
    items = "".join(
        f"<dt>{esc(term)}</dt><dd>{esc(defn)}</dd>" for term, defn in pairs)
    return f"<dl class='defs'>{items}</dl>"


def comparison_table(headers: list[str], rows: list[list[str]]) -> str:
    """Booktabs comparison matrix (VISUALS.md default route for 'two or more
    things a reader must tell apart')."""
    thead = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>"


# definition-list CSS is folded in here so blocks.py is self-contained for notes
_DEF_CSS = """
<style>
dl.defs { margin: 8pt 0; }
dl.defs dt { font-weight: 700; margin-top: 7pt; }
dl.defs dd { margin: 2pt 0 0 1.4em; }
</style>
"""


def notes_document_with_defs(title: str, body_html: str, **kw) -> str:
    doc = notes_document(title, body_html, **kw)
    return doc.replace("</head>", _DEF_CSS + "</head>")


if __name__ == "__main__":
    body = "\n".join([
        abstract(["This lecture establishes the demarcation problem and three "
                  "candidate solutions.",
                  "Learning outcomes: LO1 define the demarcation problem · "
                  "LO2 evaluate falsificationism · LO3 compare Kuhn and Lakatos."]),
        lo_section("LO1", "define the demarcation problem",
                   definition_list([
                       ("demarcation problem",
                        "the question of what distinguishes science from non-science "
                        "or pseudoscience."),
                       ("pseudoscience",
                        "a body of claims presented as scientific but not supported by "
                        "the methods or evidential standards of science."),
                   ]) + "<p>The problem is normative, not merely descriptive: it asks "
                        "what science <em>ought</em> to look like.</p>"),
        lo_section("LO2", "evaluate falsificationism",
                   "<p>Popper proposes falsifiability as the criterion of demarcation.</p>" +
                   comparison_table(
                       ["", "Verificationism", "Falsificationism"],
                       [["Unit of appraisal", "confirming instances", "attempted refutations"],
                        ["Problem of induction", "unsolved", "dissolved (deduction only)"],
                        ["Main objection", "no finite confirmation", "Duhem–Quine holism"]])),
    ])
    out = notes_document_with_defs(
        "Lecture 3 — The Demarcation Problem",
        body, subtitle="PHIL1012 — Introductory Logic and Philosophy of Science")
    p = os.path.join(_HERE, "_smoke_notes.html")
    with open(p, "w") as f:
        f.write(out)
    print(p)
