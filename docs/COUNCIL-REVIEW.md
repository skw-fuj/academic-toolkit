# Council review — academic-toolkit 1.0.0

**Mode C-style (finished deliverable), PRGX-scored.** Evidence = the files, the 51-test suite, and runs on this
machine (macOS, Python 3.14). Where something could not be verified here it says so.

## Scorecard
| Dimension | Score | Evidence / reason |
|---|---|---|
| **P** Performance (does it work) | 8.0 | 51/51 tests; real PDF render inspected; chat zip unzipped and validator run from it; MCQ gate, overlap gate, installer and build each proven able to fail (mutation-checked: breaking the audit's checker path fails a test). |
| **R** Resilience (survives other machines/users) | 6.5 | Honest degradation and conflict-safe installer are strong. **Not verified:** Windows, Linux CI run, a real claude.ai upload, a real `/plugin install`. Optional deps need system libs (pango) a student may not manage. |
| **G** Growth / maintainability | 8.0 | Single-source core, SemVer + CHANGELOG, CI workflow, hygiene test blocks personal data and dead references, extension guide. |
| **X** Fit for "everyone" | 7.0 | Defaults encode one author's strict house style (lowercase headings, no preamble, A4/Liberation Serif). Configurable, but the first-run experience is demanding. |
| **PRGX** | **7.4 — optimise** | Pattern: strong P/G, resilience not yet proven off-machine. |

## Blockers found and fixed during review
1. **Resolver prefix collision** — `BIOL100` would have matched `BIOL1001`. Boundary match + regression test.
2. **Option-block false positive** — prose starting "A. Smith…" would have rendered as an answer option. Now needs A **and** B lines; regression test.
3. **Uninstaller trusted its record file** — a tampered record could delete outside the target. Paths now confined to the
   install dir; test plants an outside file and proves it survives.
4. **Windows-hostile zip entry names** — backslashes would have broken chat/drop-in zips on Windows. POSIX arcnames.
5. (Inherited) **Silent position-check skip** in the MCQ audit — fixed and pinned by a test.

## Remaining improvements (not blockers)
- Run CI on Ubuntu and a Windows runner; attach results to the release. *(workflow included; not executed here)*
- Verify upload of each zip in claude.ai and `/plugin install` in Claude Code, and record the versions tested.
- Add a 60-second "first note" sample (slides + expected output) so newcomers see the bar before they start.
- Consider `heading_case: sentence` as the default for the public build.
- Replace the placeholder copyright holder in `LICENSE` with the real owner; the Assembly upstream licence was verified as MIT
  (see `NOTICE`).

## Member verdicts (one line each)
- **Engineer:** the gates are real — each one has a test that makes it fail. Cross-platform is asserted, not proven.
- **Operator:** install, uninstall, backup and collision handling are production-grade for a skills package.
- **Product Director:** scope is right; the pipeline order (note first) is the product.
- **Customer Advocate:** a first-time student hits Liberation fonts and pango before their first PDF — `doctor.py`
  helps, but this is the main adoption friction.
- **Domain Expert (assessment/learning science):** MCQ standard and retrieval-practice design are evidence-based;
  generated questions still need the student to check them against the real exam format.
- **Designer:** the PDF output is restrained and consistent (inspected). Colour is deliberately absent from documents.
- **Founder/Financier/Strategist/Growth/Marketer/Visionary:** free, MIT, no running costs; distribution is the open
  question, not the build. Upside: a sample pack and a one-page demo.
- **Skeptic:** the claim to attack is "works in chat". Chat enforcement is by reading, not scripts — stated honestly,
  but weaker than Code. **Verdict:** ship 1.0.0 as *release candidate* until the unverified items above are run.

## COUNCIL VERDICT
**7.4 / 10 — optimise (PRGX).** Ready to share with a small group of students now; **not yet** ready for a public
"works everywhere" claim. The one thing that must change first: **verify install and first-note on a clean Windows
or Linux machine and a real claude.ai upload.** Honest prediction: as-is, Mac/Linux Claude Code users will have a
smooth start; chat-only and Windows users will hit environment friction that no skill text can remove.
