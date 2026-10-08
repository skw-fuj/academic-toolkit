#!/usr/bin/env python3
"""Validate a lecture note against the canonical academic-toolkit note format.

Deterministic, stdlib-only. Exit 0 = compliant, 1 = defects found.

    python3 validate_note.py note.md [--outcomes lo.txt] [--heading-case lower|sentence|any]
                             [--wikilinks] [--allow-admin] [--json]

Hard failures (exit 1)
  - note does not begin with its first learning outcome (no preamble / orientation)
  - a heading is not `## LO<n>[a-z] — <outcome>`; numbering out of sequence; duplicates
  - the note does not close with exactly `## related`
  - a banned section (exam checklist, "learning outcomes covered", coverage confirmation,
    or any summary-style section: the exam summary is a separate file)
  - with --outcomes: heading text differs from the outcomes document
  - heading case violates --heading-case (default `lower`)

Warnings (judgement calls)
  - process-narration / slideshow-framing phrases
  - administrative content (lecturer contact details, assessment weighting) unless --allow-admin
  - no markdown table anywhere (check the visuals trigger test)
  - --wikilinks: fewer than 20 [[links]] (Obsidian graph rule)
"""
import argparse
import json
import pathlib
import re
import sys

BANNED_SECTIONS = [
    (r"^##\s*exam\s*prep(aration)?\s*checklist",
     "exam preparation checklist — self-testing lives in the recall/MCQ/SAQ skills"),
    (r"^##\s*learning\s*outcomes?\s*(covered|used)",
     "'learning outcomes covered/used' preamble — process narration"),
    (r"^##\s*final\s*check", "'final check — coverage confirmation' — process narration"),
    (r"^##\s*exam[- ]ready\s*summary", "summary belongs in the separate summary file, not in the note"),
    (r"^##\s*quick[- ]recall\s*summary", "summary section — belongs in the separate summary file"),
    (r"^##\s*consolidated\s*summary", "summary section — belongs in the separate summary file"),
    (r"^##\s*quick[- ]reference", "summary section — belongs in the separate summary file"),
    (r"^##\s*summary(\s*of\s*key\s*points)?\s*$", "summary section — belongs in the separate summary file"),
    (r"^##\s*consolidated\s*examiner", "summary section — belongs in the separate summary file"),
]

# process-narration / slideshow-framing phrases
VOICE = ["the deck", "the slide shows", "the slide presents", "the slides show",
         "the lecture presents", "the lecture opens", "this lecture sits",
         "not reproduced here", "outcome-structure", "not recoverable", "backfilled",
         "context, not an lo", "as covered on canvas", "see the lecture"]

# administrative content that is not examinable subject matter
ADMIN = [
    (r"[\w.+-]+@[\w-]+\.[\w.-]+", "email address (lecturer/tutor contact details are not subject content)"),
    (r"\boffice hours\b", "office hours"),
    (r"\b\d{1,3}\s?%\s+of\s+(the\s+)?(final\s+)?(grade|mark|unit)", "assessment weighting"),
    (r"\bdue\s+(date|on)\b.*\b(week|friday|monday|midnight)\b", "assessment due date"),
]

LO_RE = re.compile(r"^##\s+LO(\d+)([a-z]?)\s+—\s+(.+?)\s*$")


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def validate(path, outcomes=None, heading_case="lower", wikilinks=False, allow_admin=False):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)  # drop frontmatter
    lines = body.split("\n")

    h2, fence, first_h2_line = [], False, None
    preamble = []
    for i, ln in enumerate(lines, 1):
        if ln.startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if ln.startswith("## "):
            h2.append((i, ln.rstrip()))
            if first_h2_line is None:
                first_h2_line = i
        elif first_h2_line is None:
            s = ln.strip()
            # allowed above the first LO: blank, the H1 title, a `> part of …` hub line
            if s and not s.startswith("# ") and not s.startswith(">") and s != "---":
                preamble.append((i, s))

    errs, warns = [], []

    if preamble:
        i, s = preamble[0]
        errs.append(f"line {i}: content before the first learning outcome ({s[:60]!r}…) — "
                    "a note begins with its first LO; no orientation, scene-setting or positioning")

    for i, ln in h2:
        for pat, msg in BANNED_SECTIONS:
            if re.match(pat, ln, re.I):
                errs.append(f"line {i}: banned section {ln!r} — {msg}")

    titles = [ln for _, ln in h2]
    if len(titles) < 2 or titles[-1].strip().lower() != "## related":
        errs.append("note must end with '## related'")
    closing = {"## related"}
    los = []
    for i, ln in h2:
        if ln.strip().lower() in closing:
            continue
        m = LO_RE.match(ln)
        if not m:
            errs.append(f"line {i}: heading {ln!r} is not the canonical form "
                        "'## LO<n> — <verbatim outcome>'")
            continue
        num, part, txt = int(m.group(1)), m.group(2), m.group(3)
        los.append((i, num, part, txt))
        if heading_case == "lower":
            words = [w for w in re.findall(r"[A-Za-z][a-z]+", txt) if len(w) > 3]
            capped = [w for w in words if w[0].isupper()]
            if words and len(capped) / len(words) > 0.5:
                errs.append(f"line {i}: heading appears Title Case — must be lowercase "
                            "except proper nouns, acronyms and scientific terms")
        elif heading_case == "sentence":
            words = [w for w in re.findall(r"[A-Za-z][a-z]+", txt)[1:] if len(w) > 3]
            capped = [w for w in words if w[0].isupper()]
            if words and len(capped) / len(words) > 0.5:
                errs.append(f"line {i}: heading appears Title Case — use sentence case")

    if not los:
        errs.append("no learning-outcome headings found — the note has no LO spine at all")
    else:
        seen, expect = [], los[0][1]
        if expect != 1:
            warns.append(f"LO numbering starts at LO{expect} — correct only if this lecture "
                         "genuinely covers that outcome of the unit; otherwise renumber")
        for i, num, part, _ in los:
            if num != expect and num != expect - 1:
                errs.append(f"line {i}: LO{num} out of sequence (expected LO{expect})")
            if num >= expect:
                expect = num + 1
            key = (num, part)
            if key in seen:
                errs.append(f"line {i}: duplicate heading LO{num}{part}")
            seen.append(key)
        bare = {n for n, p in seen if p == ""}
        parted = {n for n, p in seen if p != ""}
        for n_ in sorted(bare & parted):
            errs.append(f"LO{n_} appears both bare and split into parts — pick one")

    if outcomes:
        want = [o.strip() for o in outcomes if o.strip()]
        got = [t for _, _, _, t in los]
        if len(want) != len(los):
            errs.append(f"outcome count mismatch: {len(want)} in the outcomes document, "
                        f"{len(los)} headings in the note")
        for k, (w, g) in enumerate(zip(want, got), 1):
            if norm(w) not in norm(g) and norm(g) not in norm(w):
                errs.append(f"LO{k} heading text does not match the outcomes document verbatim\n"
                            f"      document: {w}\n      note:     {g}")

    low = body.lower()
    for phrase in VOICE:
        if phrase in low:
            ln_no = low[:low.index(phrase)].count("\n") + 1
            warns.append(f"line ~{ln_no}: process-narration phrase {phrase!r} — "
                         "rewrite as direct subject matter or delete")
    if not allow_admin:
        for pat, label in ADMIN:
            m = re.search(pat, body, re.I)
            if m:
                ln_no = body[:m.start()].count("\n") + 1
                warns.append(f"line ~{ln_no}: possible administrative content — {label}. "
                             "Notes cover examinable subject matter only (use --allow-admin to silence)")

    if not re.search(r"^\|.*\|", body, re.M):
        warns.append("no markdown table anywhere — check the visuals trigger test; "
                     "comparisons and figure sets should not be left as prose")
    if wikilinks and body.count("[[") < 20:
        warns.append(f"only {body.count('[[')} wiki-links — the graph rule expects many per LO; "
                     "over-link rather than under-link")

    return errs, warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("note")
    ap.add_argument("--outcomes")
    ap.add_argument("--heading-case", choices=["lower", "sentence", "any"], default="lower")
    ap.add_argument("--wikilinks", action="store_true")
    ap.add_argument("--allow-admin", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    outs = pathlib.Path(a.outcomes).read_text(encoding="utf-8").splitlines() if a.outcomes else None
    errs, warns = validate(a.note, outs, a.heading_case, a.wikilinks, a.allow_admin)
    if a.json:
        print(json.dumps({"note": a.note, "errors": errs, "warnings": warns,
                          "compliant": not errs}, indent=2))
        sys.exit(0 if not errs else 1)
    name = pathlib.Path(a.note).name
    print("=" * 68)
    print(f"  {name}")
    print("=" * 68)
    for e in errs:
        print(f"  FAIL  {e}")
    for w in warns:
        print(f"  warn  {w}")
    if not errs and not warns:
        print("  ✓ compliant with the canonical note format")
    elif not errs:
        print(f"\n  ✓ compliant ({len(warns)} warning(s))")
    else:
        print(f"\n  ✗ {len(errs)} defect(s) — fix before filing")
    sys.exit(0 if not errs else 1)


if __name__ == "__main__":
    main()
