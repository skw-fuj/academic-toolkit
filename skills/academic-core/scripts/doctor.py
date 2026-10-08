#!/usr/bin/env python3
"""Health check for the academic toolkit. Exit 0 = everything required works; optional gaps are warnings.

    python3 doctor.py [--json]
"""
import glob
import importlib
import json
import os
import platform
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def mod(name):
    try:
        m = importlib.import_module(name)
        return True, getattr(m, "__version__", "")
    except Exception as e:  # noqa: BLE001
        return False, str(e).splitlines()[0][:80]


def fonts_present():
    dirs = [os.path.expanduser("~/Library/Fonts"), "/Library/Fonts", "/usr/share/fonts",
            "/usr/local/share/fonts", os.path.expanduser("~/.local/share/fonts"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")]
    for d in dirs:
        if glob.glob(os.path.join(d, "**", "Liberation*Serif*.ttf"), recursive=True):
            return True
    if shutil.which("fc-list"):
        out = subprocess.run(["fc-list"], capture_output=True, text=True).stdout
        return "Liberation Serif" in out
    return False


def weasyprint_ok():
    env = dict(os.environ)
    if os.path.isdir("/opt/homebrew/lib"):
        env["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/lib:" + env.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    r = subprocess.run([sys.executable, "-c", "import weasyprint;print(weasyprint.__version__)"],
                       capture_output=True, text=True, env=env)
    if r.returncode == 0:
        return True, r.stdout.strip()
    err = r.stderr.strip().splitlines()
    return False, (err[-1][:80] if err else "import failed")


def main():
    rows = []

    def add(name, ok, detail, required, fix=""):
        rows.append({"check": name, "ok": bool(ok), "detail": detail, "required": required, "fix": fix})

    add("python >= 3.9", sys.version_info >= (3, 9), platform.python_version(), True, "install Python 3.9+")
    ok, d = weasyprint_ok()
    add("weasyprint (PDF output)", ok, d, False, "pip install weasyprint  (macOS also: brew install pango)")
    ok, d = mod("matplotlib")
    add("matplotlib (figures)", ok, d, False, "pip install matplotlib")
    ok, d = mod("genanki")
    add("genanki (Anki decks)", ok, d, False, "pip install genanki")
    add("Liberation fonts (PDF text)", fonts_present(), "", False,
        "macOS: brew install --cask font-liberation · Debian/Ubuntu: apt install fonts-liberation")
    pt = shutil.which("pdftotext")
    add("pdftotext (PDF verification)", pt, pt or "", False,
        "macOS: brew install poppler · apt install poppler-utils (pypdf is used as a fallback)")
    sys.path.insert(0, os.path.join(HERE, "filing"))
    try:
        import resolve
        cfg, path = resolve.load_config()
        add("config file", path is not None, str(path or "none — run resolve.py init"), False,
            "python3 resolve.py init --output-root ~/Documents/academics")
        if path:
            add("output_root exists", os.path.isdir(os.path.expanduser(cfg["output_root"])),
                cfg["output_root"], False, "create the folder or change output_root")
    except Exception as e:  # noqa: BLE001
        add("config file", False, str(e)[:80], False)

    if "--json" in sys.argv:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            mark = "ok  " if r["ok"] else ("FAIL" if r["required"] else "warn")
            line = f"  [{mark}] {r['check']}" + (f" — {r['detail']}" if r["detail"] else "")
            if not r["ok"] and r["fix"]:
                line += f"\n         fix: {r['fix']}"
            print(line)
        missing = [r["check"] for r in rows if not r["ok"] and not r["required"]]
        if missing:
            print("\n  Writing notes works without these; missing optional pieces limit: " + ", ".join(missing))
    sys.exit(1 if any(r["required"] and not r["ok"] for r in rows) else 0)


if __name__ == "__main__":
    main()
