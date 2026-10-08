# Install guide

## Which package do I need?
| You use | Take | Do |
|---|---|---|
| Claude chat | `chat-skills/*.zip` | Settings → Capabilities → Skills → Upload skill (one zip at a time) |
| Claude Code, simplest | `…-claude-code-dropin.zip` | unzip into `~` or a project; restart |
| Claude Code, safest | the repo / `…-plugin.zip` | `./install.sh` (conflicts detected, backups made) |
| Claude Code plugin manager | the repo / `…-plugin.zip` | `/plugin marketplace add <path>` then `/plugin install academic-toolkit@academic-toolkit` |

Verify downloads against `SHA256SUMS`: `shasum -a 256 -c SHA256SUMS`.

## Minimum set for chat
Upload **academic-notes** first (it carries the standards and validator). Add **academic-study** for the one-stop
pipeline, then summary / flashcards / mcq / saq / recall as needed. `assembly` and `prompt-making` stand alone.

## Installing only some skills
`./install.sh --only academic-notes,academic-mcq` installs those skills plus `academic-core` (always included, because
the academic skills read their standards and scripts from it). Add `scholar` to the list for the agent. By hand: copy
the skill folder **and** `skills/academic-core/` into the same `skills/` directory. `assembly` and `prompt-making`
need nothing else. Chat zips are already self-contained.

## Name collisions
If you already have skills called `assembly` or `prompt-making`, `install.sh` stops and lists them. `--force` moves
yours to `<name>.bak-<timestamp>`. In chat, rename on upload or remove the old one first.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `doctor.py` says weasyprint fails on macOS | `brew install pango`; the toolkit sets `DYLD_FALLBACK_LIBRARY_PATH` automatically when `/opt/homebrew/lib` exists |
| PDF text looks wrong / wrong font | install Liberation fonts (see README); text does not fall back gracefully |
| "No config found" | run `resolve.py init --output-root <folder>` |
| `COLLISION` / `OTHER_TERM` | the subject exists in several terms; the skill asks which — this is deliberate |
| Anki deck missing | `pip install genanki`; the skill falls back to a TSV that Anki imports directly |
| Validator fails a good note | read the FAIL line: it names the exact rule and line; `--heading-case` / `--allow-admin` relax two of them |
| Skills don't appear | restart Claude Code; check `ls ~/.claude/skills/academic-notes/SKILL.md` |

## Uninstall
`./install.sh --uninstall` removes exactly the recorded files. Backups made by `--force` stay.
Plugin: `/plugin uninstall academic-toolkit`. Chat: delete each skill in Settings.
