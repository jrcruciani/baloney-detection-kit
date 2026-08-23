# Prompt catalog

BDK ships two prompt families that implement different stages of one workflow.

## Intervention prompts

[`intervention/`](intervention/) contains prompts that change the assistant's
behavior before it endorses a weak claim:

- `prompt-compact.md`
- `prompt-full.md`
- `prompt-high-stakes.md`
- `prompt-agent.md`
- `prompt-reviewer.md`
- `prompt-second-opinion.md`

Use `bdk apply <variant>` to retrieve the packaged copy.

## Diagnostic prompts

[`diagnosis/`](diagnosis/) contains 16 diagnostic prompts, prompt cards, and the
machine-readable catalog used by the CLI.

Use `bdk list`, `bdk show <id>`, or `bdk guided` to navigate them.
