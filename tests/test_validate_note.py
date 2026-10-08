import json
import sys

from conftest import FIX, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
import validate_note  # noqa: E402


def test_good_note_is_compliant(run):
    r = run(SCRIPTS / "validate_note.py", FIX / "good_note.md", "--json")
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data["compliant"] and not data["errors"]


def test_bad_note_fails_each_rule(run):
    r = run(SCRIPTS / "validate_note.py", FIX / "bad_note.md", "--json")
    assert r.returncode == 1
    errs = " | ".join(json.loads(r.stdout)["errors"])
    for needle in ["before the first learning outcome", "banned section", "must end with '## related'",
                   "Title Case", "not the canonical form"]:
        assert needle in errs, needle


def test_preamble_is_a_hard_failure(tmp_path):
    n = tmp_path / "n.md"
    n.write_text("---\ntitle: x\n---\nThis note opens with scene-setting.\n\n## LO1 — define x\ntext\n\n## related\n- y\n")
    errs, _ = validate_note.validate(n)
    assert any("before the first learning outcome" in e for e in errs)


def test_lo_gap_split_and_duplicate(tmp_path):
    n = tmp_path / "n.md"
    n.write_text("## LO1 — a\nx\n## LO3 — c\nx\n## LO3 — c\nx\n## LO4 — d\n## LO4a — d1\n## related\n")
    errs, _ = validate_note.validate(n)
    joined = " ".join(errs)
    assert "out of sequence" in joined and "duplicate heading" in joined and "both bare and split" in joined


def test_outcomes_document_must_match_verbatim(tmp_path):
    n = tmp_path / "n.md"
    n.write_text("## LO1 — define osmosis\nx\n## related\n")
    errs, _ = validate_note.validate(n, outcomes=["explain diffusion"])
    assert any("does not match the outcomes document" in e for e in errs)
    errs, _ = validate_note.validate(n, outcomes=["define osmosis"])
    assert not errs


def test_heading_case_modes(tmp_path):
    n = tmp_path / "n.md"
    n.write_text("## LO1 — Describe The Plasma Membrane Model\nx\n## related\n")
    assert validate_note.validate(n, heading_case="lower")[0]
    assert not validate_note.validate(n, heading_case="any")[0]


def test_wikilink_warning_only_when_requested(tmp_path):
    n = tmp_path / "n.md"
    n.write_text("## LO1 — define x\n| a | b |\n|---|---|\n| 1 | 2 |\n## related\n")
    assert not any("wiki-links" in w for w in validate_note.validate(n)[1])
    assert any("wiki-links" in w for w in validate_note.validate(n, wikilinks=True)[1])


def test_admin_warning_can_be_silenced(tmp_path):
    n = tmp_path / "n.md"
    n.write_text("## LO1 — define x\nEmail prof@uni.edu.\n## related\n")
    assert any("administrative" in w for w in validate_note.validate(n)[1])
    assert not any("administrative" in w for w in validate_note.validate(n, allow_admin=True)[1])
