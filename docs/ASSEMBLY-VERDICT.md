# Assembly verdict — what makes a world-class portable academic-notes toolkit?

**Mode:** Full, 7 seats. **Question:** how should a personal, Mac-bound study system be packaged so any student can
use it in Claude chat or Claude Code, without losing the standards that make it good?
**Seated:** Aristotle (what kind of thing is it?), Feynman (can a stranger use it unaided?), Torvalds (does it ship
and survive maintenance?), Munger (invert: what guarantees failure?), Taleb (hidden fragility), Arendt (the human
stake), Socrates (premises).

## Positions after cross-examination
- **Aristotle:** it is three things wearing one name — *standards* (what good looks like), *procedures* (skills),
  *instruments* (scripts). Package them separately or each rots the others.
- **Feynman:** if the README needs a person to explain it, it failed. One sentence per environment, one command.
- **Torvalds:** a standard nothing enforces is a wish. Every rule that can be a script must be a script, with a test
  that fails on purpose. No hardcoded paths; config or nothing.
- **Munger (inversion):** guaranteed failure = silent no-ops (a check that always passes), portability by
  assumption (works on the author's machine), and a package that quietly overwrites the student's existing skills.
- **Taleb:** the fragile point is the *unverified green*. A PDF that exits 0 with a missing figure, an audit that
  skips its own position check. Verify content, never exit codes.
- **Arendt:** the student is not the author. Do not smuggle one person's name, subjects, house style or accounts
  into a tool for everyone — but do not flatten the standard into mush either.
- **Socrates:** *"Is the house style the product, or a preference?"* Resolved: the **structure and rigour** are the
  product (LO spine, depth floor, visuals duty, no fabrication); **spelling, heading case, links and grade band**
  are preferences — configurable, with the proven defaults.

## Verdict
**Converged (FACT/INFERENCE):** one shared core + thin skills; deterministic gates for everything checkable;
config over hardcoding; honest degradation when optional tools are missing; a test suite that proves each gate can
fail; per-environment packaging from one source (plugin, drop-in, per-skill chat zips with vendored core).

**Unresolved tensions (kept, not smoothed):**
1. *Default strictness vs approachability.* Lowercase headings and a hard "no preamble" rule are demanding for a
   newcomer. Kept as defaults (they are the standard); relaxed via `heading_case` / `exclude_admin`. Whether the
   default should be softer for new users is a judgement call (Torvalds/Aristotle: keep; Feynman/Arendt: soften).
2. *Chat parity.* Chat without code execution cannot run the gates, so enforcement there is by reading. Accepted and
   stated in every skill, not hidden (ASSUMPTION: most chat users have code execution on paid plans).
3. *Persona lenses in Assembly.* Useful scaffolding vs the risk of treating a lens as an authority. Mitigated:
   lenses not impersonation, no fabricated quotes, evidence labels, professional-advice caveat.

**Kill criteria:** if students cannot get a first validated note in under ten minutes from download; if a gate is
found that cannot fail; if any shipped file contains an author-specific path or account.

**Next step taken:** build as specified, then review (see `COUNCIL-REVIEW.md`).

**Evidence labels:** FACT — original skills contained author-specific paths/accounts (grep-verified);
FACT — original `audit_mcq_set.py` skipped its position check via a dead path; INFERENCE — config-driven defaults
preserve quality; ASSUMPTION — chat users can run code; UNKNOWN — behaviour under every future Claude Code plugin
loader change.
