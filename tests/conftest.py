import importlib.util
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "skills" / "academic-core"
SCRIPTS = CORE / "scripts"
FIX = Path(__file__).resolve().parent / "fixtures"

if os.path.isdir("/opt/homebrew/lib"):   # macOS: weasyprint needs the Homebrew pango/cairo path
    os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")


def has_module(name):
    return importlib.util.find_spec(name) is not None


def weasyprint_works():
    import subprocess
    r = subprocess.run([sys.executable, "-c", "import weasyprint"], capture_output=True)
    return r.returncode == 0


needs_weasyprint = pytest.mark.skipif(not weasyprint_works(), reason="weasyprint not importable")
needs_matplotlib = pytest.mark.skipif(not has_module("matplotlib"), reason="matplotlib missing")
needs_genanki = pytest.mark.skipif(not has_module("genanki"), reason="genanki missing")
needs_pdftotext = pytest.mark.skipif(shutil.which("pdftotext") is None and not has_module("pypdf"),
                                     reason="no PDF text extractor")


def pdf_text(path):
    import subprocess
    if shutil.which("pdftotext"):
        return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True).stdout
    import pypdf
    return "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(str(path)).pages)


@pytest.fixture
def run():
    import subprocess

    def _run(*args, cwd=None, env=None):
        e = dict(os.environ)
        e.update(env or {})
        return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=cwd, env=e)
    return _run
