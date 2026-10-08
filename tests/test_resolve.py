import json

from conftest import SCRIPTS


def cfg_file(tmp_path, **over):
    root = tmp_path / "uni"
    root.mkdir(exist_ok=True)
    cfg = {"output_root": str(root), "term_folders": False}
    cfg.update(over)
    f = tmp_path / "cfg.json"
    f.write_text(json.dumps(cfg))
    return f, root


def res(run, cfg, *a):
    r = run(SCRIPTS / "filing" / "resolve.py", "--config", cfg, *a)
    return r.returncode, json.loads(r.stdout)


def test_needs_config_when_none(run, tmp_path):
    r = run(SCRIPTS / "filing" / "resolve.py", "--subject", "X1", "--artifact", "notes",
            cwd=tmp_path, env={"HOME": str(tmp_path), "ACADEMIC_TOOLKIT_CONFIG": ""})
    assert r.returncode == 1 and json.loads(r.stdout)["status"] == "NEEDS_CONFIG"


def test_flat_ok_and_normalised_code(run, tmp_path):
    f, root = cfg_file(tmp_path)
    (root / "BIOL1001 — Biology").mkdir()
    code, out = res(run, f, "--subject", "biol 1001", "--artifact", "mcq")
    assert code == 0 and out["status"] == "OK"
    assert out["resolved_path"].endswith("BIOL1001 — Biology/mcq")


def test_not_found_then_create_builds_subject(run, tmp_path):
    f, root = cfg_file(tmp_path)
    code, out = res(run, f, "--subject", "CHEM2002", "--artifact", "notes")
    assert code == 1 and out["status"] == "NOT_FOUND"
    assert not (root / "CHEM2002").exists(), "must not create without --create"
    code, out = res(run, f, "--subject", "CHEM2002", "--artifact", "notes", "--create")
    assert out["created"] and (root / "CHEM2002" / "notes").is_dir()


def test_collision_across_terms_and_other_term(run, tmp_path):
    f, root = cfg_file(tmp_path, term_folders=True, current_term="2026 S2")
    (root / "2025 S2" / "BIOL1001").mkdir(parents=True)
    code, out = res(run, f, "--subject", "BIOL1001", "--artifact", "notes")
    assert out["status"] == "OTHER_TERM" and code == 1
    (root / "2026 S2" / "BIOL1001").mkdir(parents=True)
    code, out = res(run, f, "--subject", "BIOL1001", "--artifact", "notes")
    assert out["status"] == "COLLISION" and code == 1
    assert out["suggested"] if "suggested" in out else out["resolved_path"].startswith(str(root / "2026 S2"))


def test_needs_term(run, tmp_path):
    f, root = cfg_file(tmp_path, term_folders=True, current_term="")
    (root / "T1" / "BIOL1001").mkdir(parents=True)
    _, out = res(run, f, "--subject", "BIOL1001", "--artifact", "notes")
    assert out["status"] == "NEEDS_TERM"


def test_create_refused_on_collision_and_unknown_artifact(run, tmp_path):
    f, root = cfg_file(tmp_path)
    (root / "A1 — original").mkdir()
    (root / "A1 — duplicate").mkdir()
    code, out = res(run, f, "--subject", "A1", "--artifact", "notes", "--create")
    assert out["status"] == "COLLISION" and out["created"] is False
    _, out = res(run, f, "--subject", "A1", "--artifact", "podcast")
    assert out["status"] == "UNKNOWN_ARTIFACT"


def test_init_writes_config_and_refuses_overwrite(run, tmp_path):
    c = tmp_path / "c.json"
    r = run(SCRIPTS / "filing" / "resolve.py", "init", "--output-root", str(tmp_path), "--config", c)
    assert r.returncode == 0 and json.loads(c.read_text())["output_root"] == str(tmp_path)
    r = run(SCRIPTS / "filing" / "resolve.py", "init", "--output-root", "/x", "--config", c)
    assert r.returncode == 1 and json.loads(c.read_text())["output_root"] == str(tmp_path)


def test_mirrors_resolved(run, tmp_path):
    f, root = cfg_file(tmp_path, mirrors=[{"name": "vault", "path": str(tmp_path / "vault")}])
    (root / "BIOL1001").mkdir()
    _, out = res(run, f, "--subject", "BIOL1001", "--artifact", "notes")
    assert out["mirror_paths"][0]["path"].endswith("vault/BIOL1001/notes")


def test_code_prefix_does_not_match_longer_code(run, tmp_path):
    f, root = cfg_file(tmp_path)
    (root / "BIOL1001 — Biology").mkdir()
    (root / "BIOL10010").mkdir()
    code, out = res(run, f, "--subject", "BIOL100", "--artifact", "notes")
    assert out["status"] == "NOT_FOUND", out
    code, out = res(run, f, "--subject", "BIOL1001", "--artifact", "notes")
    assert out["status"] == "OK" and "Biology" in out["resolved_path"]
