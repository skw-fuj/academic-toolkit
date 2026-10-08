# MCQ Construction Standard — exam-grade, pattern-proof item writing

**Authoritative shared spec.** Every MCQ set produced by any academic-toolkit skill — `academic-mcq` and `academic-exam` (practice and consolidation sets) — is built to
this standard and passes the Part 3 self-audit before it is presented as final. This file is the
single source of truth; a skill's `SKILL.md` points here rather than restating the rules.

Sourced from: NBME *Item-Writing Guide* (6th ed.); Haladyna, Downing & Rodriguez (2002), "A review
of multiple-choice item-writing guidelines for classroom assessment," *Applied Measurement in
Education* 15(3) — the 31-rule taxonomy built from 27 testing textbooks + 27 empirical studies;
Haladyna & Downing (1989), the original 43-rule taxonomy; Rodriguez (2005), "Three options are
optimal for multiple-choice items: a meta-analysis of 80 years of research," *Educational
Measurement: Issues and Practice* 24(2); Vanderbilt University Center for Teaching (Brame, 2013);
University of Texas Austin CTL; University of Michigan Online Teaching; ACS Multiple-Choice Item
Writing Guidelines. This is the medical-licensing-exam-grade (NBME/USMLE-style) approach — the most
rigorously researched item-writing tradition — and it generalises directly to university-level exam
construction.

This standard extends the inline writing rules in `academic-mcq` and the `check_answer_pattern.py` letter-sequence checker. Where a skill's own steps and this file overlap, this file governs.

---

## Part 1 — testwiseness flaws (what makes an item *guessable without knowing the content*)

This is the part that directly answers "the answer can't be a detectable pattern." Testwiseness
flaws let a savvy test-taker eliminate or identify options using cues that have nothing to do with
whether they know the material. Every rule below is a specific, named version of that general
problem.

| flaw | what it looks like | the fix |
|---|---|---|
| **length cueing** | the correct option is noticeably longer / more detailed / more hedged than the distractors | write all options to approximately the same length and level of detail; if the true answer genuinely needs more words, pad distractors with equivalent plausible detail rather than trimming the answer |
| **grammatical cueing** | an option doesn't grammatically fit the stem (e.g. stem ends in "an" but only one option starts with a vowel), so testwise students eliminate the others without reading them | use a **closed lead-in** — the stem ends as a complete question, not a fill-in-the-blank the options must grammatically complete; re-read every option immediately after the stem to confirm each fits equally |
| **absolute terms in distractors** | "always," "never," "all," "none," "only" in a wrong option | testwise students know absolutes are usually false and eliminate them on sight; avoid absolutes in *any* option, correct or not, unless the content genuinely is absolute |
| **hedge-word cueing in the correct answer** | "may," "can," "could," "sometimes" in the *correct* option | these read as "technically always true," cueing the answer; if the correct answer is conditional, phrase the stem to make the condition explicit instead of hedging the option |
| **vague-frequency terms** | "usually," "often," "rarely," "occasionally," "many," "few" | NBME's own internal study found these terms are interpreted as wildly different percentages by different readers — avoid entirely; use a specific quantifier or restructure the item |
| **logical / convergence cueing** | the correct answer is the numeric middle value of a sorted list, or shares more sub-features with the *set* of distractors than any single distractor does | shuffle numeric options so the answer isn't reliably medial; make distractors independent of each other, not overlapping variations that make one option statistically "the average of the others" |
| **clang association** | the correct option reuses a distinctive word or phrase straight from the stem | vary the phrasing between stem and correct answer; a distractor reusing stem language is fine — it's a legitimate way to make a distractor *more* attractive |
| **positional bias** | the correct letter isn't randomly distributed across items — e.g. always C, or a repeating ABCD cycle, or a learnable bigram | assign correct-answer position pseudo-randomly per item; **after drafting a full set, run `check_answer_pattern.py` on the letter sequence** and re-order flagged items until it passes |
| **"all of the above" / "none of the above"** | used to pad out the list | avoid both. "All of the above" is solvable by recognising just two options are correct without knowing the third; "none of the above" tests recognising wrongness, a different skill, and interacts badly with partial-credit reasoning. Write a genuine additional plausible distractor instead |
| **overlapping / non-mutually-exclusive options** | numeric ranges that overlap (e.g. "10–20" and "15–25"), or two options both defensible as correct | every distractor must be clearly, singularly wrong once you know the content — check pairwise for overlap before finalising |
| **implausible "filler" distractors** | an option no one would ever pick, effectively cutting a 4-option item to a 3-option guess | every distractor must be genuinely plausible to someone with a partial or common misunderstanding — the best source is **actual student errors** on this exact content, not options invented to fill a slot |
| **item interdependence** | answering one question gives away the answer to another in the same set | check the full set for chains where the stem or a distractor of item N reveals the answer to item M |
| **stem unanswerable without options ("cover-the-options" failure)** | the stem is vague enough that you can only find the answer by reading the options and reasoning backward | write the stem so a knowledgeable person could answer it with the options covered; if they can't, the stem needs more content, not better distractors |
| **negative stems without emphasis** | "which of the following is NOT..." / "...EXCEPT" buried in sentence case | avoid negative stems by default — they measure something different and are easy to misread under time pressure; if unavoidable, the negation must be bold/capitalised and used sparingly across the set |

## Part 2 — structural conventions (exam-standard format)

- **One-best-answer format**: a focused stem (ideally an applied scenario, not a bare recall
  prompt) + closed lead-in question, followed by homogeneous options with exactly one correct/best
  answer.
- **3–5 options**, not a fixed 4 or 5 by convention. Rodriguez's (2005) meta-analysis found **three
  options perform as well as four or five** in most classroom contexts, provided every distractor
  is genuinely plausible — a well-written 3-option item beats a 4-option item padded with filler.
  (a 4-option default stays fine; this simply permits 3 when the content
  only supports two real distractors.)
- **Homogeneous options**: consistent grammar, format, content category, and length across all
  options in an item — the single rule that, if followed, prevents most of Part 1's flaws at once.
- **Options in logical order** where one exists (alphabetical, numerical ascending, chronological)
  — removes any signal from ordering itself.
- **One testing point per item.** Don't bundle two separate facts into one stem where a test-taker
  could know one and not the other and still get lucky.
- **Test applied understanding over bare recall** where the learning outcome allows — a short
  vignette stem that requires applying a concept is both harder to make guessable and better
  evidence of real understanding (recall alone caps out at mid-band demonstration of understanding).
- **Distractors encode common misconceptions**, not random wrong facts — a distractor reflecting a
  plausible reasoning error does real diagnostic work; one nobody would pick is wasted.

## Part 3 — mandatory self-audit (run on every completed MCQ set before presenting it)

1. **Length check** — scan all options per item; flag any item where one option is visibly longer
   than the others.
2. **Absolute / hedge-word check** — search the full set for "always / never / all / none / only /
   may / can / could / usually / often / rarely / sometimes / many / few"; justify or remove each hit.
3. **Grammar check** — re-read stem + each option together for every item; confirm grammatical fit.
4. **Position distribution check** — run `check_answer_pattern.py "<letter sequence>"`; re-order
   flagged items and re-run until `PASS`. (Covers frequency imbalance, runs, straight cycles,
   learnable transitions, and repeated bigrams — do not eyeball this.)
5. **"All / none of the above" check** — confirm neither appears anywhere in the set.
6. **Overlap check** — for any numeric / range-based item, confirm no two options overlap.
7. **Plausibility check** — for each distractor, ask "would a partially-prepared student ever
   plausibly pick this?" If no, rewrite it around a real misconception.
8. **Cover-the-options check** — read each stem alone (options hidden); confirm it's answerable.
9. **Cross-item check** — confirm no item's stem or distractor reveals another item's answer.

`scripts/mcq/audit_mcq_set.py` automates the mechanical parts of checks 1, 2, 5, and 6 and shells out
to `check_answer_pattern.py` for check 4; checks 3, 7, 8, 9 are judgement passes done by reading.

Only after all nine checks pass should the set be presented as final. This audit is the
deliverable-quality gate — it replaces "make more MCQs" with "make MCQs that survive this list."
