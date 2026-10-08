#!/usr/bin/env python3
"""Convert an audited lecture NOTE (.md) to Notion-flavoured markdown for the
`scope` database mirror (academic-notes step 7c).

Same content rules as md_to_pdf.py: strips YAML frontmatter, the body `# Title`
H1, every `> ` hub/metadata line above the first `## `, `[[wiki-links]]`, and any
orientation/`## framing`-style section. Pipe tables become `<table>` blocks
(Notion's enhanced-markdown table form). Prints the body to stdout.

    python3 md_to_notion.py "Lecture 5 — ….md"
"""
from __future__ import annotations

import re
import sys

_FRAMING_HEADING = re.compile(
    r"^##\s+(framing|context|orientation|from .* to |where this fits|how this "
    r"lecture fits|overview\b).*$", re.I)


def _wl(s: str) -> str:
    # inside [[...]] the display-pipe may be escaped (\|) so it survives md tables
    s = re.sub(r"\[\[([^\]|]+?)\\?\|([^\]]+?)\]\]", lambda m: m.group(2), s)
    return re.sub(r"\[\[([^\]]+?)\]\]", lambda m: m.group(1), s)


def _table(rows: list[str]) -> str:
    def cells(r):
        r = r.strip()
        if r.startswith("|"):
            r = r[1:]
        if r.endswith("|"):
            r = r[:-1]
        # split on unescaped pipes only, then unescape literal \| inside a cell
        return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", r)]
    head = cells(rows[0])
    body = [cells(r) for r in rows[2:]]
    out = ['<table header-row="true">',
           "<tr>" + "".join(f"<td>{h}</td>" for h in head) + "</tr>"]
    for r in body:
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def convert(md: str) -> str:
    md = re.sub(r"^---\n.*?\n---\n", "", md, count=1, flags=re.S)
    lines = md.splitlines()
    out: list[str] = []
    i, n = 0, len(lines)
    seen_heading = False
    skip_section = False
    while i < n:
        ln = _wl(lines[i])
        s = ln.strip()
        h = re.match(r"^(#{1,6})\s+(.*)$", s)

        if not seen_heading and (re.match(r"^#\s+\S", s) or s.startswith(">")):
            i += 1
            continue
        if s == "---" or re.match(r"^!\[.*\]\(.*\)\s*$", s):  # rules, local figures
            i += 1
            continue

        if h and len(h.group(1)) >= 2:
            seen_heading = True
            skip_section = bool(_FRAMING_HEADING.match(s))
            if not skip_section:
                out.append(s)
            i += 1
            continue
        if skip_section:
            i += 1
            continue

        # pipe table
        if s.startswith("|") and i + 1 < n and re.match(r"^\|?[\s:|-]+\|", lines[i + 1].strip()):
            tbl = []
            while i < n and lines[i].strip().startswith("|"):
                tbl.append(_wl(lines[i]))
                i += 1
            out.append(_table(tbl))
            continue

        out.append(ln)
        i += 1

    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    print(convert(open(sys.argv[1]).read()))
