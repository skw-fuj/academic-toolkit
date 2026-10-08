import json
import subprocess
import sys
import zipfile
from pathlib import Path

from conftest import ROOT

INSTALL = ROOT / "tools" / "install.py"
BUILD = ROOT / "tools" / "build_dist.py"


def run(*a):
    return subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True)


def test_install_refuses_conflicts_backs_up_and_uninstalls(tmp_path):
    t = tmp_path / ".claude"
    assert run(INSTALL, "--dir", t, "--dry-run").returncode == 0 and not t.exists()
    r = run(INSTALL, "--dir", t)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (t / "skills" / "academic-notes" / "SKILL.md").is_file() and (t / "agents" / "scholar.md").is_file()
    # a second plain install must not touch anything
    r = run(INSTALL, "--dir", t)
    assert r.returncode == 2 and "NOT touched" in r.stdout
    # --force backs up, never deletes
    (t / "skills" / "assembly" / "mine.txt").write_text("user edit")
    assert run(INSTALL, "--dir", t, "--force").returncode == 0
    backups = list((t / "skills").glob("assembly.bak-*"))
    assert backups and (backups[0] / "mine.txt").read_text() == "user edit"
    # uninstall removes exactly the recorded files, leaves the backup
    assert run(INSTALL, "--dir", t, "--uninstall").returncode == 0
    assert not (t / "skills" / "academic-notes").exists() and backups[0].exists()


def test_uninstall_refuses_without_record(tmp_path):
    (tmp_path / ".claude" / "skills" / "academic-core").mkdir(parents=True)
    r = run(INSTALL, "--dir", tmp_path / ".claude", "--uninstall")
    assert r.returncode == 1 and "refusing" in r.stdout


def test_dropin_installed_skills_resolve_core_siblings(tmp_path):
    t = tmp_path / ".claude"
    assert run(INSTALL, "--dir", t).returncode == 0
    note_md = (t / "skills" / "academic-notes" / "SKILL.md").read_text()
    assert (t / "skills" / "academic-notes" / ".." / "academic-core" / "scripts" / "validate_note.py").is_file()
    assert "../academic-core/scripts/validate_note.py" in note_md


def test_build_outputs_are_complete_and_chat_zips_self_contained(tmp_path):
    out = tmp_path / "dist"
    r = run(BUILD, "--out", out)
    assert r.returncode == 0, r.stderr
    v = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]
    plug = zipfile.ZipFile(out / f"academic-toolkit-{v}-plugin.zip")
    names = plug.namelist()
    for need in ["academic-toolkit/.claude-plugin/plugin.json", "academic-toolkit/skills/academic-notes/SKILL.md",
                 "academic-toolkit/agents/scholar.md", "academic-toolkit/README.md", "academic-toolkit/LICENSE"]:
        assert need in names, need
    assert not any("__pycache__" in n or n.endswith(".pyc") or "/dist/" in n for n in names)
    drop = zipfile.ZipFile(out / f"academic-toolkit-{v}-claude-code-dropin.zip").namelist()
    assert ".claude/skills/academic-core/scripts/validate_note.py" in drop and ".claude/agents/scholar.md" in drop

    chat = sorted((out / "chat-skills").glob("*.zip"))
    assert len(chat) == len(list((ROOT / "skills").iterdir()))
    for z in chat:
        zf = zipfile.ZipFile(z)
        names = zf.namelist()
        skill = z.stem
        assert f"{skill}/SKILL.md" in names, z
        assert all(n.startswith(f"{skill}/") for n in names), "everything must sit under one top-level folder"
        md = zf.read(f"{skill}/SKILL.md").decode()
        assert "../academic-core/" not in md, f"{z.name}: unrewritten relative core path"
        for ref in set(__import__("re").findall(r"academic-core/((?:standards|scripts)/[\w./-]+)", md)):
            ref = ref.rstrip(".,)`")
            if skill != "academic-core":
                full = f"{skill}/academic-core/{ref}"
                ok = any(n.startswith(full) for n in names) if full.endswith("/") else full in names
                assert ok, f"{z.name} references missing {ref}"
    sums = (out / "SHA256SUMS").read_text().splitlines()
    assert len(sums) == 2 + len(chat)


def test_uninstall_ignores_paths_outside_target(tmp_path):
    t = tmp_path / ".claude"
    assert run(INSTALL, "--dir", t).returncode == 0
    victim = tmp_path / "precious.txt"
    victim.write_text("keep")
    rec = t / "skills" / "academic-core" / ".academic-toolkit-install.json"
    d = json.loads(rec.read_text())
    d["installed"].append(str(victim))
    rec.write_text(json.dumps(d))
    r = run(INSTALL, "--dir", t, "--uninstall")
    assert victim.read_text() == "keep" and "SKIPPED" in r.stdout


def test_doctor_runs_and_reports_json():
    r = run(ROOT / "skills" / "academic-core" / "scripts" / "doctor.py", "--json")
    rows = json.loads(r.stdout)
    assert any(x["check"].startswith("python") and x["ok"] for x in rows)


def test_only_installs_selected_skills_plus_core(tmp_path):
    t = tmp_path / ".claude"
    r = run(INSTALL, "--dir", t, "--only", "academic-mcq,academic-notes")
    assert r.returncode == 0, r.stdout + r.stderr
    got = sorted(p.name for p in (t / "skills").iterdir())
    assert got == ["academic-core", "academic-mcq", "academic-notes"], got
    assert not (t / "agents").exists() or not list((t / "agents").glob("*.md"))
    # the selected skill's core references still resolve
    assert (t / "skills" / "academic-mcq" / ".." / "academic-core" / "scripts" / "mcq" / "check_answer_pattern.py").is_file()


def test_only_agent_and_unknown_name(tmp_path):
    t = tmp_path / ".claude"
    assert run(INSTALL, "--dir", t, "--only", "scholar").returncode == 0
    assert (t / "agents" / "scholar.md").is_file() and (t / "skills" / "academic-core").is_dir()
    r = run(INSTALL, "--dir", tmp_path / "x", "--only", "academic-nope")
    assert r.returncode != 0 and "unknown name" in (r.stdout + r.stderr)
