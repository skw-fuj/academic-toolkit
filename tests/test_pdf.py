import re

import pytest
from conftest import FIX, SCRIPTS, needs_matplotlib, needs_pdftotext, needs_weasyprint, pdf_text


@needs_weasyprint
@needs_pdftotext
def test_note_renders_and_content_is_verified(run, tmp_path):
    out = tmp_path / "n.pdf"
    r = run(SCRIPTS / "pdf" / "md_to_pdf.py", FIX / "good_note.md", out, "--doc-label", "BIOL1001",
            "--expect", "fluid mosaic", "--expect", "sodium")
    assert r.returncode == 0, r.stdout + r.stderr
    txt = pdf_text(out)
    assert "Cell Membranes and Transport" in txt and "LO1" in txt and "[[" not in txt and "**" not in txt


@needs_weasyprint
@needs_pdftotext
def test_missing_expected_content_fails_loudly(run, tmp_path):
    r = run(SCRIPTS / "pdf" / "md_to_pdf.py", FIX / "good_note.md", tmp_path / "n.pdf", "--expect", "ZZZ-not-there")
    assert r.returncode != 0 and "expected content missing" in (r.stdout + r.stderr)


@needs_weasyprint
@needs_pdftotext
def test_mcq_options_render_on_separate_lines(run, tmp_path):
    md = tmp_path / "q.md"
    md.write_text("---\ntitle: MCQ\nsubject: X1\n---\n## 1\n**1.** Which gradient drives passive transport?\n\n"
                  "A. Concentration gradient\nB. Pressure gradient\nC. Thermal gradient\nD. Charge gradient\n\n"
                  "## answer key\n**Q1. Correct answer: A**\n")
    out = tmp_path / "q.pdf"
    r = run(SCRIPTS / "pdf" / "md_to_pdf.py", md, out, "--no-abstract")
    assert r.returncode == 0, r.stderr
    txt = pdf_text(out)
    lines = [l for l in txt.splitlines() if re.search(r"\b[A-D]\.\s", l)]
    assert len(lines) >= 4, txt   # each option on its own line, not one run-on paragraph


@needs_weasyprint
def test_no_abstract_flag_and_h1_title_fallback(run, tmp_path):
    md = tmp_path / "t.md"
    md.write_text("# My Heading Title\n\n## LO1 — define x\nbody text here\n\n## related\n- y\n")
    out = tmp_path / "t.pdf"
    r = run(SCRIPTS / "pdf" / "md_to_pdf.py", md, out, "--no-abstract", "--expect", "My Heading Title")
    assert r.returncode == 0, r.stdout + r.stderr


@needs_matplotlib
def test_figure_template_renders(run, tmp_path):
    r = run(SCRIPTS / "pdf" / "figures_example.py", tmp_path)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "stage_flow.png").stat().st_size > 5000


@needs_matplotlib
def test_overlap_gate_refuses_colliding_labels(run, tmp_path):
    """The overlap gate must be able to FAIL; a gate that can only pass is decorative."""
    script = tmp_path / "bad.py"
    script.write_text(
        "import sys; sys.path.insert(0, %r)\n"
        "from make_diagrams import new_figure, save\n"
        "fig, ax = new_figure()\n"
        "ax.text(0.5, 0.5, 'first colliding label', ha='center')\n"
        "ax.text(0.5, 0.5, 'second colliding label', ha='center')\n"
        "save(fig, %r, ax=ax)\n" % (str(SCRIPTS / "pdf"), str(tmp_path / "bad.png")))
    r = run(script)
    assert r.returncode != 0, "overlapping text was allowed through the gate"
    assert not (tmp_path / "bad.png").exists(), "a figure that failed the gate was still written"


@needs_weasyprint
@needs_pdftotext
def test_prose_starting_with_a_dot_is_not_an_option_block(run, tmp_path):
    md = tmp_path / "p.md"
    md.write_text("---\ntitle: T\nsubject: X1\n---\n## LO1 — define x\n"
                  "A. Smith argued that the effect is small.\n\n## related\n- y\n")
    out = tmp_path / "p.pdf"
    r = run(SCRIPTS / "pdf" / "md_to_pdf.py", md, out, "--no-abstract")
    assert r.returncode == 0, r.stderr
    assert "<ul class" not in md.read_text()
    assert "A. Smith argued" in pdf_text(out).replace("\n", " ")


@needs_weasyprint
@needs_pdftotext
def test_fenced_hierarchy_keeps_its_structure(run, tmp_path):
    md = tmp_path / "m.md"
    md.write_text("---\ntitle: Map\nsubject: X1\n---\n## mind map\n```\nLecture\n├── LO1\n│   ├── concept A\n└── LO2\n```\n")
    out = tmp_path / "m.pdf"
    r = run(SCRIPTS / "pdf" / "md_to_pdf.py", md, out, "--no-abstract", "--expect", "concept A")
    assert r.returncode == 0, r.stderr
    txt = pdf_text(out)
    assert "├── LO1" in txt and "└── LO2" in txt, txt
