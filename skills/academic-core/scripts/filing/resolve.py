#!/usr/bin/env python3
"""Resolve where an academic artifact should be filed.

One source of truth for every academic-toolkit skill. Reads a small JSON config
(see config/academic-toolkit.example.json) and scans the output folder live, so
a new term or subject never needs a code edit.

Never creates a directory unless --create is passed, and --create is only ever
passed after the student has confirmed the destination.

Usage:
    resolve.py init --output-root ~/Documents/university [--terms]   # write config
    resolve.py --subject BIOL1001 --artifact notes
    resolve.py --subject BIOL1001 --artifact mcq --create            # after confirmation

Config search order: --config, $ACADEMIC_TOOLKIT_CONFIG, ./.academic-toolkit.json,
~/.academic-toolkit/config.json.

Exit 0 only when status is OK; every other status exits 1 and means "ask first".
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_CONFIG = {
    "output_root": "~/Documents/academics",
    "term_folders": False,      # True: <root>/<term>/<subject>/<artifact>; False: <root>/<subject>/<artifact>
    "current_term": "",         # folder name of the active term, e.g. "2026 S2" (term_folders only)
    "mirrors": [],              # extra roots, e.g. [{"name": "obsidian", "path": "~/Vault/Academics"}]
    "spelling": "en-AU",
    "target_grade": "top band (e.g. HD 85%+)",
    "heading_case": "lower",    # lower | sentence | any
    "wikilinks": False,         # True when filing into Obsidian-style vaults
    "exclude_admin": True,      # drop lecturer identity / assessment weighting / logistics from content
}

# Artifact -> subfolder under the subject. The authoritative map.
ARTIFACT_SUBFOLDER = {
    "notes": "notes",
    "summaries": "summaries",
    "revision": "revision",
    "flashcards": "flashcards",
    "mcq": "mcq",
    "saq": "saq",
    "practice": "practice",
    "recall": "recall",
    "consolidate": "consolidation",
    "mindmap": "mindmaps",
    "slides": "slides",
    "podcast": "podcast",
    "video": "video",
    "assignment": "assignments",
    "stats": "stats",
}


def normalise(code: str) -> str:
    """'biol 1001' / 'BIOL-1001' -> 'biol1001'."""
    return re.sub(r"[\s_\-]+", "", code).lower()


def config_paths(explicit: str | None) -> list[Path]:
    out = []
    if explicit:
        out.append(Path(explicit).expanduser())
    if os.environ.get("ACADEMIC_TOOLKIT_CONFIG"):
        out.append(Path(os.environ["ACADEMIC_TOOLKIT_CONFIG"]).expanduser())
    out.append(Path.cwd() / ".academic-toolkit.json")
    out.append(Path.home() / ".academic-toolkit" / "config.json")
    return out


def load_config(explicit: str | None = None) -> tuple[dict, Path | None]:
    for p in config_paths(explicit):
        if p.is_file():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise SystemExit(f"config {p} is not valid JSON: {e}")
            return {**DEFAULT_CONFIG, **data}, p
    return dict(DEFAULT_CONFIG), None


def subject_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith("."))


def matches_code(folder: str, target: str) -> bool:
    """'biol1001' matches 'BIOL1001', 'BIOL1001 — Biology'; it must NOT match 'BIOL10010' or 'BIOL100' vs 'BIOL1001'."""
    n = normalise(folder)
    return n == target or (n.startswith(target) and not n[len(target)].isalnum())


def find_subject(cfg: dict, root: Path, code: str) -> list[dict]:
    """Every location holding this subject code. More than one = collision."""
    target = normalise(code)
    hits = []
    if cfg["term_folders"]:
        for term in subject_dirs(root):
            for sub in subject_dirs(term):
                if matches_code(sub.name, target):
                    hits.append({"term": term.name, "folder": sub.name, "path": str(sub)})
    else:
        for sub in subject_dirs(root):
            if matches_code(sub.name, target):
                hits.append({"term": "", "folder": sub.name, "path": str(sub)})
    return hits


def resolve(cfg: dict, code: str, artifact: str, config_file: Path | None) -> dict:
    artifact = artifact.lower()
    if artifact not in ARTIFACT_SUBFOLDER:
        return {"status": "UNKNOWN_ARTIFACT", "artifact": artifact,
                "known": sorted(ARTIFACT_SUBFOLDER)}

    root = Path(cfg["output_root"]).expanduser()
    sub = ARTIFACT_SUBFOLDER[artifact]
    out = {
        "subject_code": normalise(code),
        "artifact": artifact,
        "subfolder": sub,
        "config_file": str(config_file) if config_file else None,
        "output_root": str(root),
        "needs_confirmation": True,   # the gate is never optional
    }

    if config_file is None:
        out["status"] = "NEEDS_CONFIG"
        out["message"] = ("No config found. Ask the student where files should go, then run "
                          "`resolve.py init --output-root <folder>`. Never invent a destination.")
        return out
    if not root.is_dir():
        out["status"] = "NOT_FOUND"
        out["message"] = f"Output root {root} does not exist. Ask before creating it."
        return out

    matches = find_subject(cfg, root, code)
    out["matches"] = matches

    if not matches:
        out["status"] = "NOT_FOUND"
        out["message"] = (f"No folder for '{code}' under {root}. Ask the student for the exact "
                          "destination (or whether to create it); do not invent one.")
        return out

    if len(matches) > 1:
        cur = [m for m in matches if m["term"] == cfg["current_term"]]
        out["status"] = "COLLISION"
        out["message"] = (f"'{code}' matches {len(matches)} folders: "
                          + ", ".join(f"{m['term']}/{m['folder']}" if m["term"] else m["folder"]
                                      for m in matches)
                          + ". Confirm which one before writing.")
        out["resolved_path"] = str(Path(cur[0]["path"]) / sub) if cur else None
        return out

    only = matches[0]
    path = Path(only["path"]) / sub
    out["resolved_path"] = str(path)
    out["exists"] = path.is_dir()
    out["mirror_paths"] = [
        {"name": m.get("name", "mirror"),
         "path": str(Path(m["path"]).expanduser() / (only["term"] if only["term"] else "")
                     / only["folder"] / sub)}
        for m in cfg.get("mirrors", [])
    ]

    if cfg["term_folders"]:
        if not cfg["current_term"]:
            out["status"] = "NEEDS_TERM"
            out["message"] = ("term_folders is on but current_term is not set. Ask which term "
                              "is active and record it in the config.")
            return out
        if only["term"] != cfg["current_term"]:
            out["status"] = "OTHER_TERM"
            out["message"] = (f"'{code}' was found in '{only['term']}', not the current term "
                              f"'{cfg['current_term']}'. Confirm before writing.")
            return out

    out["status"] = "OK"
    out["message"] = ("Resolved cleanly. Show this path and wait for confirmation "
                      "(first time per subject per session).")
    return out


def cmd_init(args) -> int:
    path = Path(args.config).expanduser() if args.config else Path.home() / ".academic-toolkit" / "config.json"
    cfg = dict(DEFAULT_CONFIG)
    cfg["output_root"] = args.output_root
    cfg["term_folders"] = bool(args.terms)
    if args.current_term:
        cfg["current_term"] = args.current_term
    if path.exists() and not args.force:
        print(json.dumps({"status": "EXISTS", "config_file": str(path),
                          "message": "Config already exists; pass --force to overwrite (ask first)."}, indent=2))
        return 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "WRITTEN", "config_file": str(path), "config": cfg}, indent=2))
    return 0


def main() -> int:
    argv = sys.argv[1:]
    if argv and argv[0] == "init":
        p = argparse.ArgumentParser(prog="resolve.py init")
        p.add_argument("--output-root", required=True)
        p.add_argument("--terms", action="store_true", help="organise as <root>/<term>/<subject>/")
        p.add_argument("--current-term", default="")
        p.add_argument("--config")
        p.add_argument("--force", action="store_true")
        return cmd_init(p.parse_args(argv[1:]))

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--subject", required=True, help="subject code, e.g. BIOL1001")
    p.add_argument("--artifact", required=True, help="|".join(sorted(ARTIFACT_SUBFOLDER)))
    p.add_argument("--create", action="store_true", help="mkdir the resolved path (ONLY after confirmation)")
    p.add_argument("--config")
    args = p.parse_args(argv)

    cfg, cfg_file = load_config(args.config)
    res = resolve(cfg, args.subject, args.artifact, cfg_file)

    if args.create:
        root = Path(cfg["output_root"]).expanduser()
        if res.get("status") == "OK" and res.get("resolved_path"):
            Path(res["resolved_path"]).mkdir(parents=True, exist_ok=True)
            res["created"] = True
            res["exists"] = True
        elif res.get("status") == "NOT_FOUND" and root.is_dir() and cfg_file is not None \
                and (not cfg["term_folders"] or cfg["current_term"]):
            # first artifact for a brand-new subject: build <root>[/<term>]/<CODE>/<artifact>
            base = root / cfg["current_term"] if cfg["term_folders"] else root
            target = base / args.subject.upper().replace(" ", "") / ARTIFACT_SUBFOLDER[args.artifact.lower()]
            target.mkdir(parents=True, exist_ok=True)
            res.update(created=True, exists=True, resolved_path=str(target), status="OK")
        else:
            res["created"] = False
            res["create_refused"] = f"Refused to create: status is {res.get('status')}. Ask first."

    print(json.dumps(res, indent=2))
    return 0 if res.get("status") == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
