#!/usr/bin/env python3
"""Render an audited academic markdown file to a PDF through the house design system.

The markdown (notes, summaries, revision sheets, question sets) is the working
source; this converts a copy of it to the house-standard PDF (`blocks.py` +
`style.css`), stripping `[[wiki-links]]` and mapping markdown to the builder
functions. Deterministic, stdlib + blocks.py only.

    python3 md_to_pdf.py "Lecture 5 — ….md" "Lecture 5 — ….pdf" \
        [--doc-label "BIOL1001 — Introductory Biology"] \
        [--kicker "BIOL1001 · INTRODUCTORY BIOLOGY · WEEK 5"] \
        [--expect "some string"]  (repeatable)

Markdown handled: YAML frontmatter (title/subtitle/subject) · `## LO<n> — text`
and other `## ` headings (→ section heads; the LO texts also seed the
learning-outcomes abstract) · `### ` → h2 · `#### ` → h3 · pipe tables (incl.
empty leading header cell) · `- ` / `1. ` lists · `> **Label.** body`
blockquotes → callout box · `**bold**` · `*italic*` · `` `code` `` ·
`[[a|b]]`/`[[a]]` → text · `---` dividers dropped · `## related` → related_end.
"""
from __future__ import annotations

import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blocks as B  # noqa: E402


# --------------------------------------------------------------------------- #
# inline markdown -> HTML
# --------------------------------------------------------------------------- #
def _emphasis(s: str) -> str:
    """`**`/`*`/`***` -> <strong>/<em>, handled with a toggle stack so nested and
    run-on markers (**bold *italic***) don't mis-nest the way a two-pass regex does.
    Content already inside <code>…</code> is passed through untouched."""
    if "<code>" in s:
        return "".join(p if p.startswith("<code>") else _emphasis(p)
                       for p in re.split(r"(<code>.*?</code>)", s))
    strong = em = False
    out: list[str] = []
    for chunk in re.split(r"(\*+)", s):
        if not chunk or set(chunk) != {"*"}:
            out.append(chunk)
            continue
        k = len(chunk)
        n2, n1 = k // 2, k % 2
        toks = (["em"] + ["strong"] * n2) if (n1 and em) else \
               (["strong"] * n2 + ["em"]) if n1 else \
               ["strong"] * n2
        for t in toks:
            if t == "strong":
                out.append("</strong>" if strong else "<strong>"); strong = not strong
            else:
                out.append("</em>" if em else "<em>"); em = not em
    if em:
        out.append("</em>")
    if strong:
        out.append("</strong>")
    return "".join(out)


_MATH_SYM = {
    r"\pm": "\u00b1", r"\times": "\u00d7", r"\cdot": "\u00b7", r"\div": "\u00f7",
    r"\mid": "|", r"\cap": "\u2229", r"\cup": "\u222a",
    r"\approx": "\u2248", r"\neq": "\u2260", r"\ge": "\u2265", r"\geq": "\u2265",
    r"\le": "\u2264", r"\leq": "\u2264", r"\ll": "\u226a", r"\gg": "\u226b",
    r"\alpha": "\u03b1", r"\beta": "\u03b2", r"\sigma": "\u03c3", r"\mu": "\u03bc",
    r"\to": "\u2192", r"\rightarrow": "\u2192", r"\pi": "\u03c0", r"\%": "%",
    r"\,": "\u2009", r"\;": "\u2009", r"\ ": " ", r"\\": " ",
}
_SUP = str.maketrans("0123456789+-=()nk", "\u2070\u00b9\u00b2\u00b3\u2074\u2075"
                     "\u2076\u2077\u2078\u2079\u207a\u207b\u207c\u207d\u207e\u207f\u1d4f")
_SUB = str.maketrans("0123456789+-=()", "\u2080\u2081\u2082\u2083\u2084\u2085"
                     "\u2086\u2087\u2088\u2089\u208a\u208b\u208c\u208d\u208e")


def _mathify(s: str) -> str:
    """Small LaTeX -> unicode/plain renderer for the simple stats expressions the
    notes use ($…$ / $$…$$). weasyprint has no math engine; these read fine as text."""
    s = s.strip().replace("{,}", ",")
    s = re.sub(r"\\text\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\hat\{?(\w)\}?", lambda m: m.group(1) + "\u0302", s)
    s = re.sub(r"\\bar\{?(\w)\}?", lambda m: m.group(1) + "\u0304", s)
    for _ in range(2):  # up to one nesting level of \frac
        s = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1) / (\2)", s)
    for k, v in _MATH_SYM.items():
        s = s.replace(k, v)
    s = re.sub(r"\^\{([^{}]+)\}", lambda m: m.group(1).translate(_SUP), s)
    s = re.sub(r"\^(\w)", lambda m: m.group(1).translate(_SUP), s)
    s = re.sub(r"_\{([^{}]+)\}", lambda m: m.group(1).translate(_SUB), s)
    s = re.sub(r"_(\w)", lambda m: m.group(1).translate(_SUB), s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s{2,}", " ", s).strip()


def _inline(s: str) -> str:
    s = re.sub(r"\[\[([^\]|]+?)\\?\|([^\]]+?)\]\]", lambda m: m.group(2), s)
    s = re.sub(r"\[\[([^\]]+?)\]\]", lambda m: m.group(1), s)
    # inline maths: only $…$ that actually contains a LaTeX command (never currency)
    s = re.sub(r"\$([^$\n]*\\[a-zA-Z][^$\n]*)\$", lambda m: _mathify(m.group(1)), s)
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"~~(.+?)~~", r"<s>\1</s>", s)
    s = _emphasis(s)
    s = re.sub(r"\[([^\]]+)\]\((?:https?:[^)]+)\)", r"\1", s)  # md links -> text
    return s


def _split_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        km = re.match(r'^([A-Za-z0-9_-]+):\s*"?(.*?)"?\s*$', line)
        if km:
            meta[km.group(1)] = km.group(2)
    return meta, m.group(2)


def _table(rows: list[str]) -> str:
    def cells(r):
        r = r.strip()
        if r.startswith("|"):
            r = r[1:]
        if r.endswith("|"):
            r = r[:-1]
        # resolve [[wiki|links]] to plain text FIRST so their internal pipe
        # (escaped or not) can't be mistaken for a column delimiter, then
        # shield any remaining escaped \| (e.g. maths: P(A \| B)) before the split
        r = _strip_links(r)
        r = r.replace("\\|", "\x00")
        return [c.strip().replace("\x00", "|") for c in r.split("|")]
    header = cells(rows[0])
    body = [cells(r) for r in rows[2:]]  # rows[1] is the |---|---| separator
    # wide matrices are cramped at A4 portrait — go tight from 4 columns up
    tight = len(header) >= 4
    return B.table([_inline(h) for h in header],
                   [[_inline(c) for c in row] for row in body], tight=tight)


_BOX_LABELS = {
    "definition": B.definition, "mechanism": B.mechanism,
    "worked example": B.example, "case study": B.case,
    "exam note": B.exam, "nuance": B.nuance,
}
_BOX_RE = re.compile(
    r"^\*\*(Definition|Mechanism|Worked example|Case study|Exam note|Nuance)"
    r"\s*[—–-]\s*(.+?)\.?\*\*\s*(.*)$", re.S)


def _maybe_box(text: str):
    """A paragraph that opens with a house callout label -> the matching box.
    Only the six named labels; other bold run-ins (`**Options and tactics.**`)
    stay as paragraphs."""
    m = _BOX_RE.match(text.strip())
    if not m:
        return None
    fn = _BOX_LABELS[m.group(1).lower()]
    return fn(_strip_links(m.group(2).strip()), B.p(_inline(m.group(3).strip())))


# --------------------------------------------------------------------------- #
# block parser
# --------------------------------------------------------------------------- #
def convert(md_text: str) -> tuple[str, str, str, list[str]]:
    meta, body = _split_frontmatter(md_text)
    lines = body.splitlines()
    out: list[str] = []
    lo_items: list[str] = []
    i, n = 0, len(lines)
    para: list[str] = []
    list_buf: list[str] = []
    list_ordered = False
    in_related = False
    related_buf: list[str] = []

    def flush_para():
        nonlocal para
        if para:
            joined = " ".join(x.strip() for x in para)
            box = _maybe_box(joined)
            out.append(box if box else B.p(_inline(joined)))
            para = []

    def flush_list():
        nonlocal list_buf
        if list_buf:
            items = [_inline(x) for x in list_buf]
            out.append(B.ol(items) if list_ordered else B.ul(items))
            list_buf = []

    seen_heading = False
    while i < n:
        ln = lines[i]
        s = ln.strip()

        # drop horizontal rules and blank lines
        if s == "---" or s == "":
            flush_para(); flush_list()
            i += 1
            continue

        # drop the body H1 (the title lives in the doctitle block)
        if not seen_heading and re.match(r"^#\s+\S", s):
            i += 1
            continue

        # drop every blockquote hub/metadata line that sits ABOVE the first
        # section heading ("> part of …", "> theme A …", etc.) — these are graph
        # scaffolding, not content
        if not seen_heading and s.startswith(">"):
            i += 1
            continue

        # display maths:  $$ … $$  (single line, or opening line of a block)
        if s.startswith("$$"):
            flush_para(); flush_list()
            buf = [s]
            while not (buf[-1].rstrip().endswith("$$") and
                       (len(buf) > 1 or len(buf[-1].strip()) > 2)):
                i += 1
                if i >= n:
                    break
                buf.append(lines[i].strip())
            inner = " ".join(buf).strip().strip("$").strip()
            out.append(B.formula(_mathify(inner)))
            i += 1
            continue

        # figure:  ![caption](path)   or   ![caption|wide](path)
        im = re.match(r"^!\[(.*?)\]\((.+?)\)\s*$", s)
        if im:
            flush_para(); flush_list()
            cap, src = im.group(1), im.group(2)
            wide = cap.endswith("|wide")
            cap = cap[:-5] if wide else cap
            out.append(B.figure(src, _strip_links(cap), wide=wide))
            i += 1
            continue

        # headings
        hm = re.match(r"^(#{2,4})\s+(.*)$", s)
        if hm:
            flush_para(); flush_list()
            seen_heading = True
            level, txt = len(hm.group(1)), hm.group(2).strip()
            if level == 2:
                if re.match(r"^related$", txt, re.I):
                    in_related = True
                    i += 1
                    continue
                in_related = False
                lom = re.match(r"^(LO\d+[a-z]?)\s*[—-]\s*(.*)$", txt)
                if lom:
                    out.append(B.lo(lom.group(1), lom.group(2)))
                    lo_items.append(lom.group(2))
                else:
                    out.append(B.lo("", txt))
            elif level == 3:
                out.append(B.h2(_strip_links(txt)))
            else:
                out.append(B.h3(_strip_links(txt)))
            i += 1
            continue

        if in_related:
            m = re.match(r"^-\s+(.*)$", s)
            if m:
                related_buf.append(_inline(m.group(1)))
            i += 1
            continue

        # blockquote callout: > **Label.** rest...   (may span lines)
        if s.startswith(">"):
            flush_para(); flush_list()
            q = []
            while i < n and lines[i].strip().startswith(">"):
                q.append(lines[i].strip()[1:].strip())
                i += 1
            qtext = " ".join(x for x in q if x)
            lm = re.match(r"^\*\*(.+?)\.?\*\*\s*(.*)$", qtext)
            if lm:
                label = lm.group(1).rstrip(".")
                out.append(B.box("note", _strip_links(label),
                                 B.p(_inline(lm.group(2)))))
            else:
                out.append(B.quote(_inline(qtext)))
            continue

        # table
        if s.startswith("|") and i + 1 < n and re.match(r"^\|?[\s:|-]+\|", lines[i + 1].strip()):
            flush_para(); flush_list()
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            out.append(_table(tbl))
            continue

        # lettered answer options:  A. text / B) text  (consecutive lines -> one hanging-indent block)
        if re.match(r"^A[.)]\s+\S", s) and i + 1 < n and re.match(r"^B[.)]\s+\S", lines[i + 1].strip()):
            flush_para(); flush_list()
            opts = []
            while i < n and re.match(r"^[A-E][.)]\s+\S", lines[i].strip()):
                om = re.match(r"^([A-E])[.)]\s+(.*)$", lines[i].strip())
                opts.append(f"<li><span class=\"opt-l\">{om.group(1)}.</span> {_inline(om.group(2))}</li>")
                i += 1
            out.append('<ul class="opts">' + "".join(opts) + "</ul>")
            continue

        # list item
        lm = re.match(r"^(\d+)\.\s+(.*)$", s) or re.match(r"^[-*]\s+(.*)$", s)
        if lm:
            flush_para()
            ordered = bool(re.match(r"^\d+\.", s))
            if list_buf and ordered != list_ordered:
                flush_list()
            list_ordered = ordered
            list_buf.append(lm.group(lm.lastindex))
            i += 1
            continue

        # plain paragraph line
        flush_list()
        para.append(ln)
        i += 1

    flush_para(); flush_list()
    if related_buf:
        out.append(B.related_end("related: " + " · ".join(related_buf)))

    if "title" not in meta:
        h1 = re.search(r"^#\s+(.+)$", body, re.M)
        meta["title"] = h1.group(1).strip() if h1 else "Untitled"
    title = meta.get("title", "Untitled")
    subtitle = meta.get("subtitle", "")
    subject = meta.get("subject", "")
    return "\n".join(out), title, subtitle, [subject, lo_items]  # type: ignore


def _strip_links(s: str) -> str:
    s = re.sub(r"\[\[([^\]|]+?)\\?\|([^\]]+?)\]\]", lambda m: m.group(2), s)
    return re.sub(r"\[\[([^\]]+?)\]\]", lambda m: m.group(1), s)


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out_pdf")
    ap.add_argument("--doc-label", help="footer left segment, usually the subject")
    ap.add_argument("--kicker", help="small uppercase line above the title")
    ap.add_argument("--base-url", help="folder that relative figure paths resolve against")
    ap.add_argument("--expect", action="append", default=[],
                    help="string that must appear in the rendered PDF (repeatable)")
    ap.add_argument("--lang", default="en", help="HTML lang attribute (hyphenation), e.g. en-AU")
    ap.add_argument("--no-abstract", action="store_true",
                    help="do not seed a learning-outcomes abstract from LO headings")
    ap.add_argument("--abstract-label", default="learning outcomes")
    a = ap.parse_args()

    md = open(a.src, encoding="utf-8").read()
    B.reset_counters()
    body_mid, title, subtitle, extra = convert(md)
    subject, lo_items = extra[0], extra[1]
    doc_label = a.doc_label or subject or title
    kicker = a.kicker or (subject.upper() if subject else title.upper())

    head = [B.doctitle(kicker, title, subtitle)]
    if lo_items and not a.no_abstract:
        head.append(B.lo_abstract(a.abstract_label, lo_items))
    body = "\n".join(head) + "\n" + body_mid

    B.render(B.document(title, body, doc_label=doc_label, lang=a.lang), a.out_pdf,
             expect=a.expect or None,
             base_url=a.base_url or os.path.dirname(os.path.abspath(a.src)))


if __name__ == "__main__":
    main()
