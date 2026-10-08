import json

from conftest import SCRIPTS


def test_pattern_checker_passes_balanced_and_fails_biased(run):
    ok = run(SCRIPTS / "mcq" / "check_answer_pattern.py", "C,B,D,D,C,C,A,A,D,A,B,B")
    assert ok.returncode == 0 and "PASS" in ok.stdout, ok.stdout
    bad = run(SCRIPTS / "mcq" / "check_answer_pattern.py", "B,B,B,B,B,B,B,B")
    assert bad.returncode == 1 and "FAIL" in bad.stdout


def _items(answers):
    return [{"stem": f"Question {i}?", "options": {"A": "alpha term", "B": "beta term",
                                                  "C": "gamma term", "D": "delta term"}, "answer": a}
            for i, a in enumerate(answers)]


def test_audit_actually_runs_the_position_check(run, tmp_path):
    """Regression: the position check used to be silently skipped. A biased key MUST fail the audit."""
    p = tmp_path / "s.json"
    p.write_text(json.dumps(_items("BBBBBBBB")))
    r = run(SCRIPTS / "mcq" / "audit_mcq_set.py", p)
    assert r.returncode == 1, r.stdout
    assert "skipped" not in r.stdout.lower()
    assert "position" in r.stdout.lower() or "answer-position" in r.stdout.lower()


def test_audit_flags_length_cue_and_all_of_the_above(run, tmp_path):
    items = [{"stem": "Which is correct?",
              "options": {"A": "short", "B": "tiny",
                          "C": "a considerably longer, more detailed and carefully hedged correct option text here",
                          "D": "none of the above"}, "answer": "C"}]
    p = tmp_path / "s.json"
    p.write_text(json.dumps(items))
    r = run(SCRIPTS / "mcq" / "audit_mcq_set.py", p)
    assert r.returncode == 1
    low = r.stdout.lower()
    assert "none of the above" in low or "all/none" in low
