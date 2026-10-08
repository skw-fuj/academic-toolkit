# Token efficiency for prompts, agents and skills

Principle: **same output quality, fewer tokens.** If compression drops quality, revert it.

## Agent / skill prompts
- **Budget:** always-loaded text (an agent prompt, a skill `description`) should stay short — roughly ≤ 200 tokens.
  Put everything else in files the prompt tells the model to read **only when needed** (index first, detail on demand).
- **Compressed shape:** `Role:` · `Check:` · `Output format:` · `Rules:`. Cut prose that restates the obvious.
- **Structured reports:** `{status} | {result} | {files} | {next}`, not narration.
- **Config over copies:** many similar agents = one engine plus a table of variants, not N near-identical files.
- **Descriptions route:** a skill description must contain the phrases a user actually says ("Triggers on: …"); that
  line decides routing, so spend tokens there, not on marketing.

## Execution prompts
- Don't re-read files already in context; grep a section instead of reading whole files.
- No preamble, no recap, no filler; tables over paragraphs for comparisons; diffs over full rewrites.

## Quality gate
Keep a compression only if tests still pass, edge cases are still handled, a human can still read it, and nothing
required was lost. Otherwise revert.
