#!/usr/bin/env python3
"""Content-authoring API for academic NOTES (HTML string -> weasyprint -> PDF).

Design contract: standards/pdf-design.md (academic-core).

USAGE — author by calling these functions, never by hand-writing raw HTML:

    from blocks import *
    reset_counters()                         # once per document
    body = "".join([
        doctitle("SCI1001 · INTRODUCTION TO SCIENCE · WEEK 1",
                 "Lecture 1: What Unifies and Distinguishes Science?",
                 "the demarcation problem, falsification, and whether "
                 "philosophy of science matters"),
        lo_abstract("learning outcomes",
                    ["state and apply the demarcation problem …", "…"],
                    note="no numbered LO list was issued for this lecture — "
                         "outcomes above are inferred from its structure."),
        lo("LO1", "the demarcation problem — what unifies and distinguishes science"),
        p("the lecture opens with two questions …"),
        definition("demarcation problem",
                   p("the challenge of drawing a definition that captures every "
                     "member of a category while excluding every non-member.")),
        table(["criterion", "science without it", "non-science with it"],
              [["experiments", "historical sciences …", "cooking …"]]),
        figure("fig1.png", "the taxonomy hierarchy: domain → … → species"),
        related_end("<strong>Lecture 2 — The Use and Misuse of Data</strong> · "
                    "this lecture's falsification framework is re-used directly …"),
    ])
    html = document("Lecture 1 — What Unifies and Distinguishes Science?", body,
                    doc_label="SCI1001 — Introduction to Science")
    render(html, "Lecture 1 — What Unifies and Distinguishes Science.pdf")

Stdlib only for authoring; render() imports weasyprint.
"""
from __future__ import annotations

import html as _html
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(_HERE, "style.css")

_c = {"fig": 0, "tab": 0}


def reset_counters() -> None:
    """Call once per new document — resets figure/table numbering to 0."""
    _c["fig"] = 0
    _c["tab"] = 0


def esc(s) -> str:
    return _html.escape(str(s), quote=False)


# --------------------------------------------------------------------------- #
# text helpers (so body content is never hand-written HTML)
# --------------------------------------------------------------------------- #
def p(html_str: str) -> str:
    return f"<p>{html_str}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def ol(items: list[str]) -> str:
    return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def b(s: str) -> str:
    return f"<strong>{esc(s)}</strong>"


def i(s: str) -> str:
    return f"<em>{esc(s)}</em>"


# --------------------------------------------------------------------------- #
# structure
# --------------------------------------------------------------------------- #
def runhead(text: str) -> str:
    """Invisible zero-height marker; drives the @page footer's middle segment.
    doctitle() emits one automatically; call this directly only for per-section
    footers."""
    return f'<div class="runhead">{esc(text)}</div>'


def doctitle(kicker: str, title: str, subtitle: str) -> str:
    """Page-1 title block, in normal flow — kicker → h1 → italic subtitle → rule.
    Also emits the document-wide .runhead marker (= the title)."""
    return (
        f'{runhead(title)}'
        f'<div class="doctitle">'
        f'<p class="kicker">{esc(kicker)}</p>'
        f'<h1>{esc(title)}</h1>'
        f'<p class="subtitle">{esc(subtitle)}</p>'
        f'<hr>'
        f'</div>')


def lo_abstract(label: str, items: list[str], note: str | None = None,
                ordered: bool = True) -> str:
    """Scope / outcomes block under the title rule: small-caps label → list →
    optional italic note, framed by two thin rules. Never a metadata card."""
    lst = (ol if ordered else ul)([esc(x) for x in items])
    note_html = f'<p class="note">{esc(note)}</p>' if note else ""
    return (f'<div class="lo-abstract">'
            f'<span class="k">{esc(label)}</span>{lst}{note_html}'
            f'</div>')


def lo(tag: str, title: str) -> str:
    """Top-level section heading: small-caps tag prefix, then title, solid rule
    under. `tag` is any short string (LO1, LO2a, APPENDIX, …)."""
    return (f'<h1 class="section-head">'
            f'<span class="tag">{esc(tag)}</span>{esc(title)}</h1>')


def h2(title: str) -> str:
    return f"<h2>{esc(title)}</h2>"


def h3(title: str) -> str:
    return f"<h3>{esc(title)}</h3>"


# --------------------------------------------------------------------------- #
# callout boxes — one CSS rule; only the italic-bold label changes
# --------------------------------------------------------------------------- #
def box(kind: str, title: str, body_html: str) -> str:
    """Generic callout. `kind` is a semantic tag only — NO per-kind styling.
    The label auto-gets a trailing '.' so the run-in reads as a sentence."""
    return (f'<div class="box" data-kind="{esc(kind)}">'
            f'<p class="box-title">{esc(title)}.</p>\n{body_html}</div>')


def definition(term: str, body_html: str) -> str:
    return box("def", f"Definition — {term}", body_html)


def mechanism(title: str, body_html: str) -> str:
    return box("mech", f"Mechanism — {title}", body_html)


def example(title: str, body_html: str) -> str:
    return box("ex", f"Worked example — {title}", body_html)


def case(title: str, body_html: str) -> str:
    return box("case", f"Case study — {title}", body_html)


def exam(title: str, body_html: str) -> str:
    return box("exam", f"Exam note — {title}", body_html)


def nuance(title: str, body_html: str) -> str:
    return box("nuance", f"Nuance — {title}", body_html)


# --------------------------------------------------------------------------- #
# tables / figures
# --------------------------------------------------------------------------- #
def table(headers: list[str], rows: list[list[str]], caption: str | None = None,
          hl_col: int | None = None, tight: bool = False) -> str:
    """Booktabs table — rules only, never shaded.
      caption=None  -> uncaptioned, UNNUMBERED (the common case)
      caption="..." -> auto-numbers 'Table N. ...'
      hl_col=<int>  -> bolds that column (class hl; no colour)
      tight=True    -> denser padding / smaller font
    """
    cls = ' class="tight"' if tight else ""
    cap = ""
    if caption is not None:
        _c["tab"] += 1
        cap = f"<caption>Table {_c['tab']}. {esc(caption)}</caption>"

    def cell(tag, text, idx):
        hc = " class=\"hl\"" if hl_col is not None and idx == hl_col else ""
        return f"<{tag}{hc}>{text if isinstance(text, str) else esc(text)}</{tag}>"

    thead = "<thead><tr>" + "".join(
        cell("th", h, n) for n, h in enumerate(headers)) + "</tr></thead>"
    tbody = "<tbody>" + "".join(
        "<tr>" + "".join(cell("td", c, n) for n, c in enumerate(r)) + "</tr>"
        for r in rows) + "</tbody>"
    return f"<table{cls}>{cap}{thead}{tbody}</table>"


def figure(src: str, caption: str, wide: bool = False) -> str:
    """Always auto-numbers 'Figure N. ...', restarting at 1 per document
    (reset_counters()). The image carries only axis / data labels — the caption
    carries the description."""
    _c["fig"] += 1
    cls = ' class="wide"' if wide else ""
    return (f'<figure{cls}><img src="{esc(src)}" alt="">'
            f'<figcaption>Figure {_c["fig"]}. {esc(caption)}</figcaption></figure>')


# --------------------------------------------------------------------------- #
# supplementary
# --------------------------------------------------------------------------- #
def formula(html_str: str) -> str:
    return f'<p class="formula">{html_str}</p>'


def checklist(items: list[str]) -> str:
    return ('<ul class="checklist">'
            + "".join(f"<li>{x}</li>" for x in items) + "</ul>")


def quote(html_str: str) -> str:
    return f'<p class="quote-block">{html_str}</p>'


def related_end(html_str: str) -> str:
    """The 'see also' / cross-reference block at the close of a document —
    small, italic, grey, rule-separated, never boxed. Lead with 'related:'."""
    return f'<div class="related-end">{html_str}</div>'


# --------------------------------------------------------------------------- #
# document wrapper + render
# --------------------------------------------------------------------------- #
def document(title: str, body_html: str, *, doc_label: str,
             lang: str = "en") -> str:
    """Wrap authored body content in the HTML skeleton. `doc_label` is the left
    segment of the running footer (usually the subject, e.g.
    'SCI1001 — Introduction to Science'). The middle segment is the .runhead marker
    doctitle() sets; the right is the page number."""
    label_css = _html.escape(doc_label, quote=True)
    return (
        f'<!DOCTYPE html><html lang="{lang}" style="--doc-label: \'{label_css}\'">'
        f'<head><meta charset="utf-8"><title>{esc(title)}</title>'
        f'<link rel="stylesheet" href="file://{CSS_PATH}">'
        f'</head><body>\n{body_html}\n</body></html>\n')


def render(html_str: str, out_pdf: str, *, expect: list[str] | None = None,
           base_url: str | None = None) -> None:
    """HTML string -> PDF via weasyprint, then VERIFY (a clean render is not
    proof — no-op != success). Sets the Homebrew dyld path weasyprint needs on
    macOS and re-execs once so the C stack loads. `expect` strings must all
    appear in the rendered PDF's extracted text.
    """
    brew = "/opt/homebrew/lib"
    if os.path.isdir(brew) and os.environ.get("_ACAD_NOTES_REEXEC") != "1":
        parts = [brew, "/usr/local/lib", "/usr/lib"]
        cur = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        if cur:
            parts.append(cur)
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(dict.fromkeys(parts))
        os.environ["_ACAD_NOTES_REEXEC"] = "1"
        # re-exec a tiny renderer so weasyprint's extensions load with the path
        tmp = out_pdf + ".src.html"
        with open(tmp, "w") as f:
            f.write(html_str)
        script = (
            "import sys;from weasyprint import HTML;"
            f"HTML(filename={tmp!r}, base_url={base_url or _HERE!r})"
            f".write_pdf({out_pdf!r})")
        r = subprocess.run([sys.executable, "-c", script])
        os.environ.pop("_ACAD_NOTES_REEXEC", None)
        if r.returncode != 0:
            sys.exit(f"render: weasyprint failed for {out_pdf}")
        os.remove(tmp)
    else:
        from weasyprint import HTML
        HTML(string=html_str, base_url=base_url or _HERE).write_pdf(out_pdf)

    if not os.path.exists(out_pdf) or os.path.getsize(out_pdf) < 1000:
        sys.exit(f"render: FAIL — {out_pdf} missing or too small")
    try:
        txt = subprocess.run(["pdftotext", out_pdf, "-"],
                             capture_output=True, text=True).stdout
    except FileNotFoundError:
        import pypdf
        txt = "\n".join((pg.extract_text() or "")
                        for pg in pypdf.PdfReader(out_pdf).pages)
    if not txt.strip():
        sys.exit(f"render: FAIL — {out_pdf} has no extractable text (blank render)")
    missing = [s for s in (expect or []) if s not in txt]
    if missing:
        sys.exit("render: FAIL — expected content missing:\n  "
                 + "\n  ".join(repr(m) for m in missing))
    pages = txt.count("\x0c") + 1
    print(f"render: OK — {out_pdf} ({os.path.getsize(out_pdf)} B, ~{pages} pp, "
          f"{len(txt.split())} words, {len(expect or [])} marker(s) verified)")


if __name__ == "__main__":
    # smoke document exercising every component
    reset_counters()
    body = "".join([
        doctitle("TEST1001 · DESIGN SYSTEM · WEEK 0",
                 "Lecture 0: Notes Toolchain Smoke Test",
                 "every component, rendered once, to eyeball against the house style"),
        lo_abstract("learning outcomes",
                    ["exercise the title block and the scope abstract",
                     "exercise section heads, boxes, tables, figures",
                     "exercise formula, checklist, quote, related-end"],
                    note="this is a smoke test — not real content."),
        lo("LO1", "boxes and body text"),
        p("body text is justified Liberation Serif at 11pt with a 1.55 line-height. "
          "en-dash bullets follow:"),
        ul(["first point — with an em-dash aside",
            "second point, " + b("bold run-in") + " then plain"]),
        definition("smoke test", p("a minimal end-to-end exercise of every "
                                   "builder function, rendered to PDF and eyeballed.")),
        mechanism("why a smoke test", p("it catches a broken selector or a wrong "
                                        "font before real content is generated.")),
        exam("what to check", p("fonts, box style, table rules, figure caption "
                                "numbering, and the running footer.")),
        h2("a sub-section"),
        p("sub-sections inside an LO use " + i("h2") + " (bold italic)."),
        quote("laws of nature · regularities · classification · measurement · "
              "reproducibility · causation · falsification"),
        formula("P(at least one) = 1 − (1 − α)<sup>k</sup>"),
        lo("LO2", "tables and figures"),
        table(["criterion", "with it", "without it"],
              [["experiments", "cooking", "palaeontology"],
               ["evidence", "courts of law", "some theory"]]),
        table(["", "definition"],
              [["Type I", "reject a true H₀"], ["Type II", "fail to reject a false H₀"]],
              hl_col=0),
        table(["n", "p"], [["12", "0.386"], ["48", "0.083"], ["96", "0.014"]],
              caption="a captioned table auto-numbers; uncaptioned ones do not.",
              tight=True),
        checklist(["state the demarcation problem", "evaluate falsificationism",
                   "compare Kuhn and Lakatos"]),
        related_end("<strong>Lecture 1 — Real Content</strong> · this smoke test "
                    "has no successor; this is only a smoke test."),
    ])
    out = os.path.join(_HERE, "_smoke.pdf")
    render(document("Lecture 0 — Notes Toolchain Smoke Test", body,
                    doc_label="TEST1001 — Design System"),
           out, expect=["demarcation problem", "Type I", "auto-numbers"])
