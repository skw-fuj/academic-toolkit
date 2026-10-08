#!/usr/bin/env python3
"""Render an academic HTML document to PDF via weasyprint, then VERIFY the output
actually contains the content (a clean render is not proof — no-op != success).

    python3 render_pdf.py input.html "output.pdf" [--expect "string" --expect "string" ...]

- Sets DYLD_FALLBACK_LIBRARY_PATH so weasyprint finds the Homebrew pango/cairo
  stack on this machine (the documented macOS gotcha; libs are installed under
  /opt/homebrew/lib but not on the default loader path).
- After writing the PDF: re-opens it, extracts text, and fails loudly if the PDF
  is empty, has zero pages, or any --expect string is missing.

Exit 0 only when the PDF is written AND verified. Exit non-zero otherwise.
"""
import os
import subprocess
import sys

# must be set before weasyprint's C extensions load
_BREW_LIB = "/opt/homebrew/lib"
if os.path.isdir(_BREW_LIB):
    existing = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    parts = [_BREW_LIB, "/usr/local/lib", "/usr/lib", os.path.expanduser("~/lib")]
    if existing:
        parts.append(existing)
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(dict.fromkeys(parts))
    # weasyprint may need a re-exec if we were started without the var
    if os.environ.get("_ACAD_RENDER_REEXEC") != "1":
        os.environ["_ACAD_RENDER_REEXEC"] = "1"
        os.execv(sys.executable, [sys.executable] + sys.argv)


def _parse_args(argv):
    if len(argv) < 3:
        print(__doc__)
        sys.exit(2)
    inp, outp = argv[1], argv[2]
    expects = []
    i = 3
    while i < len(argv):
        if argv[i] == "--expect" and i + 1 < len(argv):
            expects.append(argv[i + 1])
            i += 2
        else:
            i += 1
    return inp, outp, expects


def _extract_text(pdf_path):
    # prefer pdftotext (homebrew), fall back to pypdf
    try:
        r = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout
    except FileNotFoundError:
        pass
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as e:  # noqa: BLE001
        return f""  # verification will fail on emptiness, which is correct


def main():
    inp, outp, expects = _parse_args(sys.argv)
    if not os.path.exists(inp):
        sys.exit(f"render_pdf: input not found: {inp}")

    try:
        from weasyprint import HTML
    except Exception as e:  # noqa: BLE001
        sys.exit(f"render_pdf: weasyprint import failed ({e}). "
                 f"Needs Homebrew pango/cairo; check DYLD_FALLBACK_LIBRARY_PATH.")

    HTML(filename=inp).write_pdf(outp)

    if not os.path.exists(outp) or os.path.getsize(outp) < 800:
        sys.exit(f"render_pdf: FAIL — {outp} missing or suspiciously small "
                 f"({os.path.getsize(outp) if os.path.exists(outp) else 0} bytes)")

    text = _extract_text(outp)
    if not text.strip():
        sys.exit(f"render_pdf: FAIL — {outp} has no extractable text (render produced a blank PDF)")

    missing = [s for s in expects if s not in text]
    if missing:
        sys.exit("render_pdf: FAIL — expected content missing from PDF:\n  " +
                 "\n  ".join(repr(m) for m in missing))

    pages = text.count("\x0c") + 1
    print(f"render_pdf: OK — {outp} ({os.path.getsize(outp)} bytes, ~{pages} page(s), "
          f"{len(text.split())} words, {len(expects)} marker(s) verified)")


if __name__ == "__main__":
    main()
