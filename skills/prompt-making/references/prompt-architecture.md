# Prompt architecture (deep reference)

> Adapted from the `prompt-architecture` cluster of `MC Dean/ai-design-skills` (MIT licence). See NOTICE.
> Load this when drafting a non-trivial system prompt, agent instruction set, or reusable template.

## System-prompt anatomy (order matters)
Role → context → constraints → format → examples. Lead with *who the model is and why it exists*, then what it
must/mustn't do, then the exact output shape, then 1–2 worked examples last. Common structural mistakes: burying the
role, stating format before constraints, examples that contradict the instructions, constraints that can't be checked.

## Context engineering (what goes in the window, in what order)
- **Context budget** — every token competes; include only what changes the output.
- **Information architecture** — put the load-bearing constraint near the task, not buried in a preamble.
- **Quality signals** — if the model keeps missing an instruction, the fix is usually *placement* (move it closer to
  the task) or *salience* (make it a rule, not prose), not repetition.

## Constraint specification
Types: format, length, tone, content boundaries. Write them **checkable** — "under 150 words" beats "concise";
"exactly these 4 fields" beats "structured". A length cap plus a completeness demand can conflict: resolve it
explicitly rather than leaving the model to guess which wins.

## Few-shot patterns
Examples demonstrate the *distribution* you want, not just the format: make them representative, include a hard or
edge case, keep them consistent with the stated rules. One example gets over-fitted; 2–3 well-chosen beat 6 similar.

## Chain-of-thought design
Helps on multi-step reasoning, maths and trade-off decisions; hurts on simple lookups and when the "reasoning" is
post-hoc rationalisation. Name the steps and say what each must produce, rather than "think step by step".

## Template design
Fixed scaffold + typed variables + composition points. Design slots so a filled template cannot be malformed. A
template is good when a non-author can fill it correctly without reading its source. Version templates like code.

## Prompt versioning
Version any prompt that ships; record what changed and why; test against a fixed case set before rollout (a fix for
one case can regress another).
