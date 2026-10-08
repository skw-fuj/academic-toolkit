"""Free-chat edition: every lite skill must be self-contained and every embedded answer key must be real."""
import re
import subprocess
import sys

import pytest
from conftest import ROOT, SCRIPTS

BUILD = ROOT / "tools" / "build_free.py"
FORBIDDEN = [r"\.py\b", r"scripts/", r"academic-core", r"\.\./", r"python", r"pdftotext", r"pandoc", r"weasyprint",
             r"genanki", r"\.apkg", r"run the script", r"\bpytest\b"]


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("free")
    r = subprocess.run([sys.executable, str(BUILD), "--out", str(out)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return out


def skills(built):
    return sorted((built / "skills").iterdir())


def test_fifteen_lite_skills_each_one_file(built):
    sk = skills(built)
    assert len(sk) == 15
    for s in sk:
        assert [p.name for p in s.iterdir()] == ["SKILL.md"], f"{s.name} must be a single self-contained file"
        assert s.name.endswith("-lite")


@pytest.mark.parametrize("pat", FORBIDDEN)
def test_no_script_or_file_dependencies(built, pat):
    for s in skills(built):
        txt = (s / "SKILL.md").read_text()
        assert not re.search(pat, txt, re.I), f"{s.name}: matches {pat!r}"


def test_frontmatter_and_size_limits(built):
    for s in skills(built):
        txt = (s / "SKILL.md").read_text()
        m = re.match(r'^---\nname: ([a-z0-9-]+)\ndescription: "(.*)"\n---\n', txt, re.S)
        assert m and m.group(1) == s.name
        assert 40 <= len(m.group(2)) <= 1024 and "Triggers on" in m.group(2)
        assert len(txt.split()) <= 1200, f"{s.name} is too long for free-chat context ({len(txt.split())} words)"


def test_every_skill_keeps_the_honesty_rules(built):
    for s in skills(built):
        if s.name in ("academic-print-lite",):
            continue
        txt = (s / "SKILL.md").read_text()
        assert "Never invent" in txt or "never invent" in txt or "Never claim" in txt or "never claim" in txt, s.name
    for s in skills(built):
        if s.name in ("academic-study-lite", "academic-print-lite"):
            continue
        assert "Checked by reading" in (s / "SKILL.md").read_text() or "by reading" in (s / "SKILL.md").read_text(), s.name


def test_embedded_mcq_keys_pass_the_real_checker(built):
    txt = (built / "skills" / "academic-mcq-lite" / "SKILL.md").read_text()
    found = re.findall(r"(\d+) questions, key [AB]: ([A-D](?:,[A-D])+)", txt)
    assert len(found) == 18, len(found)           # 9 lengths x 2 keys
    for n, key in found:
        assert len(key.split(",")) == int(n), (n, key)
        r = subprocess.run([sys.executable, str(SCRIPTS / "mcq" / "check_answer_pattern.py"), key],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"embedded key fails the checker: {key}\n{r.stdout}"


def test_zips_and_prompt_fallbacks_exist(built):
    zips = sorted((built / "zips").glob("*.zip"))
    assert len(zips) == 15
    assert len(list((built / "prompts").glob("*.md"))) == 14
    assert (built / "README-FREE.md").is_file()


def test_study_router_lists_every_other_skill(built):
    txt = (built / "skills" / "academic-study-lite" / "SKILL.md").read_text()
    for s in skills(built):
        if s.name != "academic-study-lite":
            assert s.name in txt, f"router does not mention {s.name}"
