# Contributing
1. `pip install -r requirements-dev.txt` and run `python3 -m pytest -q` — it must pass before and after your change.
2. Skills are prompts: keep `description` ≤ 1024 characters with real trigger phrases; keep always-loaded text short and
   put detail in files read on demand.
3. No personal data, absolute paths, or external-service assumptions in any shipped file (`tests/test_hygiene.py`
   enforces this).
4. A check that can only pass is decorative — every new gate needs a test that makes it fail on purpose.
5. Bump `.claude-plugin/plugin.json` + `marketplace.json` + `CHANGELOG.md` together; run `python3 tools/build_dist.py`.
