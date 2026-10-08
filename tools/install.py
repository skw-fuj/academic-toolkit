#!/usr/bin/env python3
"""Install the academic-toolkit skills and agent for Claude Code (drag-and-drop equivalent).

    python3 tools/install.py                       # user scope  -> ~/.claude/
    python3 tools/install.py --project .           # one project -> ./.claude/
    python3 tools/install.py --dir /some/.claude   # explicit target
    python3 tools/install.py --dry-run             # show what would happen
    python3 tools/install.py --force               # replace existing skills (old copy is backed up)
    python3 tools/install.py --uninstall           # remove exactly what this tool installed
    python3 tools/install.py --deps                # also pip-install optional dependencies
    python3 tools/install.py --only academic-notes,academic-mcq   # just these skills (+ academic-core, always)
                                                   # add "scholar" to the list to install the agent too

Never overwrites an existing skill or agent without --force; with --force the old copy is moved to
`<name>.bak-<timestamp>` rather than deleted. Stdlib only; Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORD = ".academic-toolkit-install.json"


def version() -> str:
    return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]


def target_dir(args) -> Path:
    if args.dir:
        return Path(args.dir).expanduser().resolve()
    if args.project is not None:
        return (Path(args.project).expanduser().resolve() / ".claude")
    return Path.home() / ".claude"


def sources(only=None):
    skills = sorted(p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
    agents = sorted((ROOT / "agents").glob("*.md"))
    if only:
        names = {s.strip() for s in only.split(",") if s.strip()}
        known = {s.name for s in skills} | {a.stem for a in agents}
        bad = sorted(names - known)
        if bad:
            raise SystemExit(f"unknown name(s): {', '.join(bad)}\navailable: {', '.join(sorted(known))}")
        # academic-core holds the shared standards/scripts every academic skill needs: always installed
        skills = [s for s in skills if s.name in names or s.name == "academic-core"]
        agents = [a for a in agents if a.stem in names]
    return skills, agents


def backup(path: Path, dry: bool) -> Path:
    dest = path.with_name(f"{path.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
    print(f"  backup  {path} -> {dest.name}")
    if not dry:
        path.rename(dest)
    return dest


def install(args) -> int:
    base = target_dir(args)
    skills, agents = sources(args.only)
    plan, conflicts = [], []
    for s in skills:
        dst = base / "skills" / s.name
        plan.append(("skill", s, dst))
        if dst.exists():
            conflicts.append(dst)
    for a in agents:
        dst = base / "agents" / a.name
        plan.append(("agent", a, dst))
        if dst.exists():
            conflicts.append(dst)

    print(f"academic-toolkit {version()} -> {base}" + ("  [dry run]" if args.dry_run else ""))
    if conflicts and not args.force:
        print("\nThese already exist and were NOT touched:")
        for c in conflicts:
            print(f"  exists  {c}")
        print("\nRe-run with --force to replace them (the old copies are backed up, not deleted),\n"
              "or --dir/--project to install somewhere else.")
        return 2

    installed = []
    for kind, src, dst in plan:
        if dst.exists():
            backup(dst, args.dry_run)
        print(f"  install {kind:5s} {dst}")
        if args.dry_run:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        else:
            shutil.copy2(src, dst)
        installed.append(str(dst))

    if not args.dry_run:
        rec = base / "skills" / "academic-core" / RECORD
        rec.write_text(json.dumps({"version": version(), "installed": installed,
                                   "time": time.strftime("%Y-%m-%dT%H:%M:%S")}, indent=2))

    if args.deps and not args.dry_run:
        req = ROOT / "requirements.txt"
        print("\nInstalling optional Python dependencies…")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)], check=False)

    if not args.dry_run:
        doctor = base / "skills" / "academic-core" / "scripts" / "doctor.py"
        print("\nHealth check:")
        subprocess.run([sys.executable, str(doctor)], check=False)
        print("\nNext: restart Claude Code, then try  /academic-study  or  “make notes for this lecture”.\n"
              "Optional: python3 " + str(base / "skills/academic-core/scripts/filing/resolve.py")
              + " init --output-root ~/Documents/academics")
    return 0


def uninstall(args) -> int:
    base = target_dir(args)
    rec = base / "skills" / "academic-core" / RECORD
    if not rec.is_file():
        print(f"No install record at {rec}; nothing removed (refusing to guess which files are ours).")
        return 1
    data = json.loads(rec.read_text())
    for p in map(Path, data["installed"]):
        try:
            p.resolve().relative_to(base.resolve())
        except ValueError:
            print(f"  SKIPPED {p}: outside {base} (record file looks tampered; not touching it)")
            continue
        if args.dry_run:
            print(f"  would remove {p}")
            continue
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
        print(f"  removed {p}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", help="explicit .claude target directory")
    ap.add_argument("--project", nargs="?", const=".", help="install into <PROJECT>/.claude (default: current dir)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--only", help="comma-separated skill names to install (academic-core is always included)")
    ap.add_argument("--deps", action="store_true", help="pip-install requirements.txt afterwards")
    args = ap.parse_args()
    return uninstall(args) if args.uninstall else install(args)


if __name__ == "__main__":
    sys.exit(main())
