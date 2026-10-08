---
name: prompt-making
description: "Draft, refine and stress-test prompts for any purpose — system prompts, agent or skill instructions, API calls, personas, study prompts, one-off task prompts — with a self-critique pass and a re-prompt-waste check. Triggers on: write a prompt for, improve this prompt, draft a system prompt, make this prompt better, prompt for my study notes, why does my prompt keep failing, /prompt-making."
---

# prompt-making

A universal prompt engineer. Works on any prompt, any target model, any subject. For academic prompts the reference
implementation is the notes prompt in `../academic-core/standards/note-format.md` §7 — match or beat that standard.

## Step 0 — Brief
If the request has real gaps (bare invocation, one-liner), ask the few questions that change the draft: **purpose**
(task prompt, persona/system prompt, agent or skill instructions, API template, grading prompt), **target** (which
model/runtime; or model-agnostic), **inputs and outputs** (what goes in; what must come out, in what format),
**constraints** (length, tone, hard rules, things it must never do, an existing style to match), and **what "good"
looks like** (ideally one example of a good output). Never guess purpose, target or format. A complete brief → Step 1.

## Step 1 — Draft
For any non-trivial system prompt, agent instruction set or reusable template, read
`references/prompt-architecture.md`; for agent, skill or always-loaded text read `references/token-efficiency.md`.
- **Order:** role/purpose → constraints → format → examples last.
- **Concrete over generic:** "under 150 words" beats "be concise"; "exactly these four fields" beats "structured".
- **State the non-obvious failure modes explicitly** (what the model will otherwise get wrong, and the rule that stops it).
- **Include 1–2 worked examples** when the task is non-trivial or the output format is precise; one of them hard.
- Match existing conventions when extending or replacing something that already exists.
- Every line must change model behaviour, or be cut.

## Step 2 — Self-critique before showing it
Check for: ambiguity (two valid readings of one instruction) · conflicting instructions · untested edge cases (empty,
adversarial, unexpected input) · overfitting to one example · decorative, non-load-bearing length. Fix before showing.

## Step 3 — Re-prompt-waste check
Scan the draft for the patterns that cause follow-up prompts, and fix any hit:
- **Task:** one clear verb; one task per prompt; success criteria stated; facts not feelings ("throws TypeError at
  line 43", not "broken"); big builds split into steps; nothing referenced implicitly ("the thing we discussed").
- **Context:** prior decisions restated; audience named; what was already tried; a grounding rule for factual work
  ("only what you are confident is accurate; say [uncertain] otherwise").
- **Format:** output shape and length explicit; a role when it helps; concrete values instead of "make it professional".
- **Scope:** files, functions, sources fenced in ("only X; touch nothing else"); for agents a stop condition.
- **Reasoning:** for judgement tasks ask for recommendation + assumptions + criteria + evidence + checks, not "show
  your chain of thought"; never expect memory across sessions.
- **Agents:** starting state and target state given; progress reporting; explicit human-review triggers (deleting,
  spending, sending, schema changes).

## Step 4 — Present and iterate
Show the draft with a one-line rationale for each non-obvious choice and name which technique you applied. **Ask for
confirmation before treating anything as final** — never silently finalise a prompt that will be installed as a skill
or sent to a live system. If the student can run it, offer a 3-case test (typical, hard, adversarial) and revise on
the results.

## Step 5 — Finalise
Deliver the prompt in a fenced block, with its slots marked `[like this]`, plus a one-paragraph "why it is shaped this
way". Version it (v1, v2…) and note what changed and why on each revision. Save only where the student says (see
`../academic-core/standards/filing.md` when a config exists).

## Study-specific patterns
For prompts that turn lectures into study material: fix the structure (one H2 per outcome), the content list per
outcome, the source rule (lecture primary; never fabricate a citation), the scope rule (subject content only), and a
self-check last. Put the self-check last — models act most reliably on the final instruction.
