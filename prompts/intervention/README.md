# Prompt Matrix

Use these prompts as copy-paste distributions of the same framework. They differ
by context, not by values: every variant preserves the BDK loop:

**Trigger -> Mode -> Protocol -> Output -> Review**

| Prompt | Use when | Copy target |
|--------|----------|-------------|
| [`prompt-compact.md`](prompt-compact.md) | You have a short custom-instructions field | Personal LLM settings |
| [`prompt-full.md`](prompt-full.md) | You want the complete default behavior in one prompt | System prompt or project instruction |
| [`prompt-high-stakes.md`](prompt-high-stakes.md) | False validation could cause material harm | Medical, legal, financial, safety, public-sector, political, or mental-health-adjacent assistants |
| [`prompt-agent.md`](prompt-agent.md) | The assistant can use tools, retrieval, agents, or MCP | Agent runtime instructions |
| [`prompt-reviewer.md`](prompt-reviewer.md) | You need to review an answer after it was generated | Human/AI review pass |
| [`prompt-second-opinion.md`](prompt-second-opinion.md) | You want external critique from a model that has not seen the first answer | External reviewer |

## Languages and translation review

English (`en`) is the canonical reference and the default for existing CLI/API
callers. Spanish (`es`) adds faithful translations, not localized behavior:
[`es/prompt-compact.md`](es/prompt-compact.md),
[`es/prompt-full.md`](es/prompt-full.md), and the self-contained
[`ROOT_PROMPT.es.md`](../../ROOT_PROMPT.es.md).

```bash
bdk apply compact --lang es
bdk apply full --lang es --output system-prompt.es.md
```

Only compact/full are available in Spanish. Languages and variants are
explicitly allowlisted; unsupported languages or unavailable pairs fail without
falling back to English. Python callers can use
`get_intervention("full", lang="es")` and `list_interventions(lang="es")`;
omitting `lang` preserves the English API.

Mixed headings are intentional: Spanish prose preserves the English section and
mode names, Light labels (`Claim`, `Check`, `Alternative`, `Next`), and Full output
labels so machine heading parsing stays compatible. Spanish size is not assessed
using the English token estimate below.

The translation preserves the two gates, no-claim exclusions, concise Light,
Full, Stabilization/reopening, claim-specific evidence methods, novelty split,
false-balance guard, AI critique diversity, and high-stakes boundaries.
**Human Spanish-language review and maintainer behavior/version sign-off are
required before merge.** `prompt-v2.0` is retained to align with the English
contract, not as proof of semantic or behavioral equivalence. Structural tests
verify text distribution and CLI wiring, not translation quality, model behavior,
or efficacy; historical evidence is unchanged.

Portuguese and French are intentionally deferred in
[#10](https://github.com/jrcruciani/baloney-detection-kit/issues/10).
Spanish skill/plugin copies are not part of this distribution.

## Selection rule

Choose the smallest prompt that preserves rigor in your context:

1. If you are an individual user, start with `prompt-compact.md`.
2. If you are configuring an assistant, use `prompt-full.md` or `ROOT_PROMPT.md`.
3. If the domain can create material harm, use `prompt-high-stakes.md`.
4. If the runtime has tools or subagents, use `prompt-agent.md`.
5. If the response already exists, use `prompt-reviewer.md`.
6. If you want external contrast, use `prompt-second-opinion.md`; treat it as
   critique diversity, not independent evidence.

Choosing a high-stakes variant is not a trigger. Every live variant follows two
gates: first require an actual claim signal, then select the lightest mode by
mismatch and consequence. A high-stakes domain alone never forces Full.
Ordinary no-claim questions and the listed exclusions need no intervention;
Light is a 3-4-line response, not the full template.

## Canonical contract and synchronization

The fenced block between `<!-- bdk:prompt:start -->` and
`<!-- bdk:prompt:end -->` in [`prompt-full.md`](prompt-full.md) is the canonical
full behavior contract. It is concise and self-contained; root does not depend
on external instructions or use a separately authored compact fallback.

Run from the repository:

```bash
python scripts/sync_prompts.py
python scripts/sync_prompts.py --check
```

The generator copies that **exact full block** into the marked regions of
[`ROOT_PROMPT.md`](../../ROOT_PROMPT.md) and
[`skill/SKILL.md`](../../skill/SKILL.md), and its inner text into
[`critical_investigation_mode.txt`](../../skill/prompts/critical_investigation_mode.txt).
It also mirrors all six `prompt-*.md` files byte-for-byte into
`src/bdk/data/interventions/` for `bdk apply`. For Spanish, it copies the exact
marked full block from `es/prompt-full.md` into `ROOT_PROMPT.es.md` and mirrors
the compact/full source files byte-for-byte into `src/bdk/data/interventions/es/`.
Spanish is never generated from English text automatically; edit the Spanish
sources after reviewing changes to the canonical English contract, then sync.
No Spanish skill text or plugin copy is generated. Specialized variants remain
context-specific adaptations, not alternate canonical full contracts; review
their gates and safeguards when editing the canonical behavior.

Only marked regions are replaced in both roots and English skill Markdown;
headings, prose, YAML metadata, and resource paths outside them are preserved. Edit the canonical
block, not these generated blocks. Missing/duplicate/reversed delimiters or
invalid source/wrapper version markers fail explicitly before any writes.
`--check` reports missing/stale generated outputs without writing, with exit
status 1 for drift, 2 for invalid input, and 0 for synchronization. Diagnostic
cards, historical examples, calibration, and preregistration are not generated.

Size checks count Unicode characters and whitespace-delimited words, using
characters / 4 as a rough English token estimate, **not a model tokenizer**.
The copyable full block targets roughly 1,000-1,200 estimated tokens; file-level
counts additionally include Markdown wrappers. Tests bound the block and root
file separately, so wrapper overhead is not passed off as prompt size.

## Versioning

English/Spanish intervention Markdown, both roots, plain English skill text, and
packaged mirrors start with `<!-- bdk prompt-v2.0 -->`.
**Exception:** `skill/SKILL.md` keeps YAML frontmatter
as its first block, with the marker immediately after the closing `---`.
Diagnostic cards have their own scope and are not assigned this marker.

If you embed a prompt in a product, classroom, evaluation, or team workflow, pin
the repository commit and note which prompt file you used. See
[`../../VERSIONING.md`](../../VERSIONING.md).
The two-gate/Light-output refinement retains `prompt-v2.0` by explicit request,
but is a distributed behavior change requiring maintainer behavior/version
sign-off before merge; see [`CHANGELOG.md`](../../CHANGELOG.md). Deterministic
checks verify text and distribution integrity, not actual model firing.
