#!/usr/bin/env python3
"""Build the distributable packages into dist/.

    python3 tools/build_dist.py [--out dist]

Produces
  academic-toolkit-<v>-plugin.zip            Claude Code plugin (marketplace / --plugin-dir)
  academic-toolkit-<v>-claude-code-dropin.zip  unzip into ~ or a project: .claude/skills + .claude/agents
  chat-skills/<skill>.zip                    one zip per skill for Claude chat (Settings > Capabilities > Skills)
  SHA256SUMS
Chat zips are self-contained: academic-core is vendored inside each zip that needs it and `../academic-core/`
references are rewritten to `academic-core/`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"__pycache__", ".git", "dist", ".pytest_cache", "node_modules", ".venv"}
SKIP_FILES = {".DS_Store"}
LITE_CORE = ["standards"]            # prompt-making / assembly only need the standards text


def version() -> str:
    return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]


def iter_files(base: Path):
    for p in sorted(base.rglob("*")):
        if p.is_file() and not (set(p.relative_to(base).parts) & SKIP_DIRS) \
                and p.name not in SKIP_FILES and p.suffix != ".pyc":
            yield p


def write_zip(zpath: Path, entries):
    zpath.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for arcname, src in entries:
            info = zipfile.ZipInfo.from_file(src, arcname)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, Path(src).read_bytes())


def rewrite(text: str) -> str:
    return text.replace("../academic-core/", "academic-core/")


def build_chat_zip(skill: Path, out: Path) -> Path:
    name = skill.name
    needs_core = name != "academic-core"
    entries = []
    for f in iter_files(skill):
        rel = f.relative_to(skill)
        entries.append((f"{name}/{rel.as_posix()}", f))
    tmp = Path(tempfile.mkdtemp())
    final = []
    for arc, f in entries:
        if f.suffix == ".md":
            t = tmp / arc.replace("/", "__")
            t.write_text(rewrite(f.read_text(encoding="utf-8")), encoding="utf-8")
            final.append((arc, t))
        else:
            final.append((arc, f))
    if needs_core:
        core = ROOT / "skills" / "academic-core"
        lite = name in {"prompt-making", "assembly"}
        for f in iter_files(core):
            rel = f.relative_to(core)
            if f.name == "SKILL.md":
                continue                      # the core skill doc is not needed inside another skill
            if lite and rel.parts[0] not in LITE_CORE:
                continue
            final.append((f"{name}/academic-core/{rel.as_posix()}", f))
    zpath = out / "chat-skills" / f"{name}.zip"
    write_zip(zpath, final)
    shutil.rmtree(tmp, ignore_errors=True)
    return zpath


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist"))
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    v = version()
    made = []

    # 1. plugin zip: the whole repo minus build/cache dirs
    plug = out / f"academic-toolkit-{v}-plugin.zip"
    write_zip(plug, [(f"academic-toolkit/{f.relative_to(ROOT).as_posix()}", f) for f in iter_files(ROOT)])
    made.append(plug)

    # 2. claude-code drop-in
    drop = out / f"academic-toolkit-{v}-claude-code-dropin.zip"
    entries = []
    for f in iter_files(ROOT / "skills"):
        entries.append((f".claude/skills/{f.relative_to(ROOT / 'skills').as_posix()}", f))
    for f in iter_files(ROOT / "agents"):
        entries.append((f".claude/agents/{f.relative_to(ROOT / 'agents').as_posix()}", f))
    readme = out / "_DROPIN_README.txt"
    readme.write_text("Unzip into your home folder (user scope) or a project folder.\n"
                      "Result: .claude/skills/* and .claude/agents/scholar.md. Restart Claude Code.\n"
                      "Existing skills with the same names would be overwritten by unzip: use tools/install.py "
                      "from the plugin zip if you want conflict detection and backups.\n")
    entries.append((".claude/README-academic-toolkit.txt", readme))
    write_zip(drop, entries)
    made.append(drop)

    # 3. chat zips
    for s in sorted((ROOT / "skills").iterdir()):
        if (s / "SKILL.md").is_file():
            made.append(build_chat_zip(s, out))
    readme.unlink()

    # 4. free-chat edition (self-contained, script-free lite skills + paste-in prompts)
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_free.py"), "--out", str(out / "free-chat")], check=True,
                   stdout=subprocess.DEVNULL)
    shutil.rmtree(out / "free-chat" / "skills")        # the zips are the deliverable; unzipped copies are redundant
    made.extend(sorted((out / "free-chat" / "zips").glob("*.zip")))

    sums = []
    for p in made:
        sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out).as_posix()}")
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    for p in made:
        print(f"{p.stat().st_size/1024:8.0f} KB  {p.relative_to(out)}")


if __name__ == "__main__":
    main()
