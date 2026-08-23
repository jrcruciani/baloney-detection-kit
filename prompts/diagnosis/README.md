# Prompt Toolkit

This directory exposes the prompts as the primary framework artifact.

| Artifact | Purpose |
|----------|---------|
| [`cards/`](cards/) | One operational card per diagnostic prompt |
| [`catalog.yaml`](catalog.yaml) | Human-facing mirror of the machine-readable prompt catalog |
| [`../../framework/diagnosis/guide.md`](../../framework/diagnosis/guide.md) | Full prompt text, rationale, and epistemic note |

The reference CLI uses the packaged copy at
[`../../src/bdk/data/prompts.yaml`](../../src/bdk/data/prompts.yaml). Tests
assert that both YAML catalogs stay in sync.

## How to use a card

1. Read **When to use** and **When not to use**.
2. Fill the required inputs, if any.
3. Copy the source prompt from `../../framework/diagnosis/guide.md` or `catalog.yaml`.
4. Run the prompt manually.
5. Read Observed claims as evidence candidates and Inferred claims as
   hypotheses.
6. Escalate only when the result is vague, high-stakes, or behaviorally
   suspicious.
