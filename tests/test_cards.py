import zipfile

from conftest import SCRIPTS, needs_genanki


@needs_genanki
def test_apkg_builds_and_is_stable(run, tmp_path):
    tsv = tmp_path / "c.tsv"
    tsv.write_text("What is osmosis?\tMovement of water across a membrane<br>down its water-potential gradient\n"
                   "Define diffusion\tNet movement down a concentration gradient\n")
    a, b = tmp_path / "a.apkg", tmp_path / "b.apkg"
    assert run(SCRIPTS / "cards" / "build_apkg.py", tsv, "BIOL1001 L3", a).returncode == 0
    assert run(SCRIPTS / "cards" / "build_apkg.py", tsv, "BIOL1001 L3", b).returncode == 0
    assert zipfile.is_zipfile(a) and "collection.anki2" in zipfile.ZipFile(a).namelist()
    # same deck name -> same deck/model ids so re-import updates instead of duplicating
    import sqlite3
    def deck_ids(p):
        d = tmp_path / ("x" + p.stem); d.mkdir()
        zipfile.ZipFile(p).extract("collection.anki2", d)
        con = sqlite3.connect(d / "collection.anki2")
        return con.execute("select models, decks from col").fetchone()
    import json
    ma, da = deck_ids(a); mb, db = deck_ids(b)
    assert set(json.loads(ma)) == set(json.loads(mb)) and set(json.loads(da)) == set(json.loads(db))
