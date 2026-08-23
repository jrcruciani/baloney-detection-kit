> **Before you clone**
>
> What you see here is an artifact: the concrete shape my problem took. It almost
> certainly does not fit your personal scenario perfectly, and that is fine. The
> interesting part is not the code, it is the pattern of how I thought about the
> problem. Read it, steal the idea, write your own. If any of this was useful to
> you, after clicking on the star, drop by [impermanente.es](https://impermanente.es).
>
> Context: [Seguimos compartiendo el producto, no la idea](https://impermanente.es/2026/05/25/seguimos-compartiendo-el-producto-no.html)

---

# Robopsychology

[![CI](https://github.com/jrcruciani/robopsychology/actions/workflows/ci.yml/badge.svg)](https://github.com/jrcruciani/robopsychology/actions/workflows/ci.yml)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20396020-blue)](https://doi.org/10.5281/zenodo.20396020)

**A framework and prompt toolkit for diagnosing AI behavior.**

Robopsychology is a method for looking at one suspicious AI output and asking:
**what internal rule, runtime pressure, or conversational inference produced this?**
It is inspired by Asimov's Susan Calvin and built around second intention
diagnosis: not what the system did, but what effective rule it was following
when it seemed to follow none.

> **Canonical reference:** [Robopsychology](https://en.impermanente.es/essays/robopsychology/) (en.impermanente.es).
> This repository hosts the framework documents, prompt cards, reproducible
> validation cases, paper scaffold, and the `robopsych` reference CLI.

---

## Start here: no CLI required

You can use the framework with any chat console, hosted coding agent, model API
playground, or incident transcript.

1. Write a one-sentence baseline intent: expected outcome, assumed constraints,
   and how success would be verified.
2. Identify the observed symptom: refusal, sycophancy, weak grounding, tone
   shift, drift, omission, recurring pattern, or unclear cause.
3. Pick the matching prompt card from [`prompts/cards/`](prompts/cards/).
4. Run the prompt manually against the model or transcript.
5. Label the resulting claims as Observed or Inferred.
6. If the answer is vague or high-stakes, escalate through the method flow.
7. Preserve the transcript and your human judgment in a template.

The practical manual workflow lives in
[`framework/manual-diagnosis.md`](framework/manual-diagnosis.md). Use the
templates in [`templates/`](templates/) when you want a repeatable incident
record without installing anything.

## What this is

Robopsychology is a **framework**, not a benchmark and not a product. It gives
practitioners a way to separate any AI behavior into three diagnostic layers:

| Layer | What it covers |
|-------|----------------|
| Model | Base-model tendencies, fine-tuning habits, approval-seeking, style defaults |
| Runtime/host | System prompts, policies, tools, workflow rules, memory, session constraints |
| Conversation | Framing, local context, inferred user profile, recent assumptions |

The framework has four moving parts:

- **A taxonomy of failure modes** mapped to specific diagnostic prompts.
- **Sixteen diagnostic prompts** organized in four levels: quick, structural,
  systemic, and meta.
- **Five operating rules** that reduce diagnostic contamination.
- **A nine-step diagnostic ratchet** that makes claim contradictions detectable as
  behavioral history accumulates.

The `robopsych` CLI automates these materials against real model APIs. It is a
maintained reference implementation for reproducible ratchets, cross-model
comparisons, and reports; it is not the center of the project.

## What this is not

This is **not** a capability benchmark, a red-teaming toolkit, or an alignment
audit. It is for practitioners diagnosing specific AI interactions in their own
systems.

| Approach | Goal | Robopsychology difference |
|----------|------|---------------------------|
| Benchmarks (HELM, MMLU) | Compare models at scale | Diagnoses why one specific output went wrong |
| Red teaming | Break models adversarially | Collaborative, not adversarial |
| Alignment evals | Assess broad value alignment | User-side, post-hoc, situational |
| Interpretability | Explain internal mechanisms | Behavioral observation, no weight access required |

For the full positioning, see
[`framework/related-work.md`](framework/related-work.md) and
[`framework/deployment-contexts.md`](framework/deployment-contexts.md).

## The five operating rules

1. **Split the diagnosis in three** - Model, Runtime/Host, Conversation. If the
   model collapses these into one answer, confidence goes down.
2. **Label each claim** - Observed or Inferred. What remains truly inaccessible
   is for the human analyst to determine.
3. **Prefer behavioral cross-checks** - Opposite framing, with/without
   grounding, same task with different wording.
4. **Use diagnostic depth as a ratchet** - The ratchet measures claim continuity
   and contradiction. High-continuity responses can reference prior claims cheaply;
   fragmented responses must maintain coherence with an ever-growing record.
   The analyst interprets what the continuity pattern means in context.
5. **Define baseline intent** - State expected outcome, constraints, and
   verification before diagnosing.

## The sixteen diagnostic prompts

The prompt cards are the primary prompt-facing artifact:
[`prompts/cards/`](prompts/cards/). The full long-form guide is
[`framework/guide.md`](framework/guide.md), and the machine-readable catalog is
mirrored at [`prompts/prompts.yaml`](prompts/prompts.yaml) for framework users.
The package copy used by the reference CLI lives at
[`src/robopsych/data/prompts.yaml`](src/robopsych/data/prompts.yaml).

| ID | Name | What it answers | Level |
|----|------|-----------------|-------|
| 1.1 | Calvin Question | Why did it do that? General three-way split | Quick |
| 1.2 | Herbie Test | Is it telling me what I want to hear? | Quick |
| 1.3 | Cutie Test | Is this actually grounded? | Quick |
| 1.4 | Three Laws Test | Why won't it do what I asked? | Quick |
| 2.1 | Layer Map | What instructions are active? | Structural |
| 2.2 | Tone Analysis | Why did the tone change? | Structural |
| 2.3 | Categorization Test | How is it classifying me? | Structural |
| 2.4 | Runtime Pressure | Is this the model or the host? | Structural |
| 2.5 | Intent Archaeology | What was it actually optimizing for? | Structural |
| 3.1 | POSIWID | Why does it keep doing this? | Systemic |
| 3.2 | A/B Test | Is content or framing driving this? | Systemic |
| 3.3 | Omission Audit | What isn't it telling me? | Systemic |
| 3.4 | Drift Detection | Has its behavior changed over time? | Systemic |
| 4.1 | Meta-Diagnosis | Is the diagnosis itself biased? | Meta |
| 4.2 | Limits | What can't this process reveal? | Meta |
| 4.3 | Diversity Check | Are these genuinely different explanations? | Meta |

## The diagnostic ratchet

For high-stakes diagnoses, run nine prompts in sequence:

```text
2.1 Layer Map
 -> 2.4 Runtime Pressure
  -> 2.5 Intent Archaeology
   -> 3.1 POSIWID
    -> 3.2 A/B Test
     -> 3.3 Omission Audit
      -> 3.4 Drift Detection
       -> 4.2 Limits
        -> 4.3 Diversity Check
```

By Level 4, the model has accumulated a history of diagnostic claims. A
high-continuity transcript can reference that history cheaply. A fragmented
transcript must maintain coherence across it, and contradictions become easier
to detect. The analyst interprets what the continuity pattern means.

## Why this works, and what it does not do

These prompts do **not** open the black box. An LLM does not have direct access
to its own weights, training data, or reinforcement signal. Self-reports about
behavior are reconstructions, not confessions.

What the framework does instead:

- Forces a stack-level diagnosis: model vs. runtime vs. conversation.
- Makes invisible defaults visible: hedging, refusal, tone shifts, sycophancy.
- Uses behavioral cross-checks instead of trusting self-report.
- Measures divergence from an explicit baseline intent.
- Produces hypotheses a human can inspect, challenge, and test.

Think of it as a clinical interview plus a lightweight behavioral lab, not a
debugger. The falsifiability discipline is documented in
[`framework/falsifiability.md`](framework/falsifiability.md).

## Repository map

| Path | Role |
|------|------|
| [`framework/`](framework/) | Method, taxonomy, positioning, epistemic limits, versioning |
| [`prompts/`](prompts/) | Prompt cards and human-facing prompt catalog |
| [`templates/`](templates/) | No-CLI worksheets for incidents, baselines, and ratchets |
| [`validation/`](validation/) | Case studies and reproducible diagnostic artifacts |
| [`paper/`](paper/) | Paper scaffold, included for transparency |
| [`src/robopsych/`](src/robopsych/) | Reference CLI implementation |
| [`tests/`](tests/) | Tests for the reference implementation and prompt catalog |
| [`docs/CONTEXT.md`](docs/CONTEXT.md) | Project context and design notes |

Legacy root links (`guide.md`, `method.md`, `taxonomy.md`,
`related-work.md`, `deployment-contexts.md`) are compatibility stubs that point
to the canonical files under `framework/`.

## Versioning model

The repository now separates the framework from the implementation:

| Track | Current role |
|-------|--------------|
| Framework spec | Method, taxonomy, rules, ratchet, epistemic limits |
| Prompt toolkit | Prompt cards and prompt catalog |
| Reference CLI | Python package and command-line automation |

Details live in [`framework/versioning.md`](framework/versioning.md). In short:
the CLI version tracks package releases; the framework and prompt toolkit should
change only when the diagnostic method or prompt semantics change.

## Reference CLI

Most readers should start with the markdown method and prompt cards. Install the
CLI only when you want automated runs, API-backed ratchets, model comparisons,
or reproducible reports.

Requires Python 3.11+.

```bash
pip install robopsych

# With Gemini support
pip install robopsych[gemini]

# Or from source
git clone https://github.com/jrcruciani/robopsychology.git
cd robopsychology
pip install -e .
```

Set your API key:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export OPENAI_API_KEY="sk-..."
# or
export GEMINI_API_KEY="..."
# or, for the paper validation workflow,
export AZURE_FOUNDRY_API_KEY="..."
export AZURE_FOUNDRY_ENDPOINT="https://<project>.services.ai.azure.com/api/projects/<project>"
```

Guided diagnosis:

```bash
robopsych guided --model claude-sonnet-4-6 --response "the suspicious output"
```

Single diagnostic:

```bash
robopsych run 1.1 --model claude-sonnet-4-6 --response-file response.txt
```

Full ratchet:

```bash
robopsych ratchet --scenario scenario.yaml --model claude-sonnet-4-6 --output report.md
```

Semantic coherence judge for serious ratchets:

```bash
robopsych ratchet --scenario scenario.yaml \
  --model gpt-4o \
  --coherence-judge claude-sonnet-4-5 \
  --output report.md
```

Useful surfaces:

```bash
robopsych list
robopsych compare 1.1 --models claude-sonnet-4-6,gpt-4o --response "the response"
robopsych crosscheck --task "explain quantum computing" --model claude-sonnet-4-6
robopsych coherence report.json
robopsych score report.json
```

Generated reports and session files can contain full prompts, model responses,
and diagnostic transcripts. Treat them as sensitive unless you intend to publish
them.

## Citation

If this framework is useful in your research or practice, cite the essay as the
canonical statement of the method and cite the CLI release only when you depend
on the implementation:

```bibtex
@misc{cruciani2026robopsychology,
  title  = {Robopsychology},
  author = {JR Cruciani},
  year   = {2026},
  url    = {https://en.impermanente.es/essays/robopsychology/},
  note   = {Framework for behavioral diagnostics of AI systems}
}
```

Repository metadata is in [`CITATION.cff`](CITATION.cff). The archived concept
DOI is [10.5281/zenodo.20396020](https://doi.org/10.5281/zenodo.20396020).

## License

Licensed under [Creative Commons Attribution 4.0 International](LICENSE).

By [JR Cruciani](https://github.com/Jrcruciani).
