"""Package hygiene: manifests valid, skills well-formed, no personal data or dead references shipped."""
import json
import re

import pytest
from conftest import ROOT, CORE

SKILLS = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
TEXT_EXT = {".md", ".py", ".css", ".json", ".txt", ".sh", ".yml", ".yaml", ".toml"}

BANNED = [r"\bTris\b", r"\btris\b", r"/Users/", r"MTKG", r"SCIE1001", r"PSYC\d{4}", r"obsidian/tris",
          r"Antigravity", r"Gemini Notebook", r"[Nn]otebook\s?LM", r"notebooklm", r"odyssey", r"_shared/",
          r"~/\.claude/skills/_shared", r"(?<!\w)/belong\b", r"(?<!\w)/consult\b", r"(?<!\w)/council(?![-\w])", r"\bUSYD\b", r"Sydney",
          r"tristanting", r"iCloud"]


def shipped_text_files():
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix in TEXT_EXT and not (set(p.parts) & {"dist", "__pycache__", ".git", ".pytest_cache"}):
            if p.name == "test_hygiene.py":
                continue
            yield p


def frontmatter(p):
    t = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    assert m, f"{p} has no frontmatter"
    fm = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip().strip('"')
    return fm


def test_manifests_valid_and_versions_agree():
    plug = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    mk = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert re.fullmatch(r"\d+\.\d+\.\d+", plug["version"])
    assert mk["plugins"][0]["version"] == plug["version"] and mk["plugins"][0]["name"] == plug["name"]
    assert f"[{plug['version']}]" in (ROOT / "CHANGELOG.md").read_text(), "CHANGELOG lacks the current version"


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_skill_frontmatter(skill):
    fm = frontmatter(skill / "SKILL.md")
    assert fm["name"] == skill.name
    assert re.fullmatch(r"[a-z0-9-]{1,64}", fm["name"])
    assert 40 <= len(fm["description"]) <= 1024, len(fm["description"])
    if skill.name != "academic-core":
        assert "Triggers on" in fm["description"], "description must carry real trigger phrases"


def test_agent_frontmatter():
    fm = frontmatter(ROOT / "agents" / "scholar.md")
    assert fm["name"] == "scholar" and fm["description"] and fm["tools"]


def test_no_personal_or_dead_references():
    hits = []
    for p in shipped_text_files():
        t = p.read_text(encoding="utf-8", errors="ignore")
        for pat in BANNED:
            for m in re.finditer(pat, t):
                line = t[:m.start()].count("\n") + 1
                hits.append(f"{p.relative_to(ROOT)}:{line}: {pat}")
    assert not hits, "\n".join(hits[:40])


def test_every_referenced_core_path_exists():
    missing = []
    for p in (ROOT / "skills").rglob("*.md"):
        t = p.read_text(encoding="utf-8")
        for m in re.finditer(r"(?:\.\./academic-core/)((?:standards|scripts)/[\w./-]+)", t):
            ref = m.group(1).rstrip(".,)`")
            if not (CORE / ref).exists():
                missing.append(f"{p.relative_to(ROOT)} -> {ref}")
        if p.parent == CORE / "standards" or p.parent == CORE:
            for m in re.finditer(r"`((?:standards|scripts)/[\w./-]+\.(?:md|py))`", t):
                if not (CORE / m.group(1)).exists():
                    missing.append(f"{p.relative_to(ROOT)} -> {m.group(1)}")
    assert not missing, "\n".join(missing)


def test_python_files_compile():
    import py_compile
    for p in ROOT.rglob("*.py"):
        if "__pycache__" in p.parts or "dist" in p.parts:
            continue
        py_compile.compile(str(p), doraise=True)
