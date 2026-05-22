# Related Work

How baloney-detection-kit relates to existing approaches in critical thinking, AI safety, and LLM behavior shaping.

This document exists because the playbook is, by its own admission, **a re-framing, not an invention**. The honest thing to do is to map what it borrows, what it adds, and what it deliberately avoids.

---

## What this playbook is

A **behavioral playbook** for LLM conversations. It changes the default move from "elaborate and validate" to "contextualize, contrast, and then respond." It is meant to run at inference time, before the model validates a weak or inflated claim.

It is not an evaluator, benchmark, SDK, package, RAG framework, or CI harness. It does not score the model. It does not automate fact-checking. It prevents one specific failure mode: sycophantic validation of weak, novel-sounding, high-stakes, or against-consensus claims.

---

## The intellectual lineage

The playbook is a synthesis of:

- **Carl Sagan**, *The Demon-Haunted World* (1996) - the original Baloney Detection Kit.
- **Andrej Karpathy**, "A Recipe for Training Neural Networks" - state-of-the-art-first methodology.
- **Robert Jay Lifton**, *Thought Reform and the Psychology of Totalism* (1961) - eight criteria of thought reform / cult dynamics.
- **Karl Popper**, *The Logic of Scientific Discovery* (1934) - falsifiability.

The contribution is packaging: concise enough for prompts, explicit enough for agents, and practical enough for human review.

---

## Why this is not a toolkit

There are many useful tools around this problem: retrieval systems, fact-checking pipelines, LLM evaluators, hallucination detectors, red-team harnesses, observability platforms, and diagnostic frameworks.

This repo intentionally stays upstream of those:

- **No dependencies.** The playbook should work anywhere text instructions work.
- **No runner.** The artifact is the protocol, not software execution.
- **No benchmark.** Manual review examples calibrate judgment but do not claim measurement.
- **No evaluator.** If a team needs scoring, it should use an external evaluator or separate repo.
- **No framework adapter.** Framework-specific integrations would distract from the core habit.

The playbook can be embedded in products that use tools, but the repo itself should remain a readable protocol.

---

## Adjacent technical approaches

### 1. System prompts and behavioral defaults

Most production LLM products ship with a system prompt that shapes default behavior. This playbook is a specialized prompt pattern focused on critical investigation before validation.

- **Similarity:** both shape model behavior at inference time.
- **Difference:** the playbook is narrow, explicit, and reviewable: "do not validate a novel-sounding claim before checking the state of the art."
- **Limitation:** like any prompt-level intervention, it can be overridden, ignored, or eroded in long contexts.

### 2. Constitutional AI and training-time behavior shaping

Constitutional AI and related methods encode principles during training or post-training. The playbook encodes principles in instructions.

- **Similarity:** both rely on written norms.
- **Difference:** training-time methods can be more robust; the playbook is immediately portable and requires no model access.
- **Tradeoff:** portability over robustness.

### 3. Retrieval-augmented verification

RAG and evidence-backed fact-checking systems ground answers in external sources. Modern fact-checking work often decomposes claims, retrieves evidence, and classifies support, refutation, or insufficient evidence.

- **Similarity:** both push the model away from free assertion.
- **Difference:** RAG changes the evidence substrate; the playbook changes the conversational behavior.
- **Compose:** a system can use RAG while following the playbook, but this repo does not implement RAG.

### 4. Sycophancy evaluation and mitigation

Research on sycophancy shows that models often conform to user beliefs, sometimes under multi-turn pressure. Evaluation suites and mitigation methods can measure or reduce that tendency.

- **Similarity:** same target failure mode.
- **Difference:** benchmarks measure; training mitigations alter models; the playbook guides an assistant's behavior in a specific conversation.
- **Practical lesson:** the playbook includes stabilization mode because multi-turn pressure is a real failure pattern.

---

## Adjacent evaluation and diagnostic tools

| Class | Question it answers | Examples |
|-------|---------------------|----------|
| **Behavioral playbook** | How should the assistant respond before it validates a weak claim? | baloney-detection-kit |
| **Retrieval / fact-checking pipeline** | What evidence supports or refutes this claim? | FEVER-style and AVeriTeC-style systems, RAG with citation enforcement |
| **Automated evaluator** | How often does a model fail across many cases? | Azure AI Foundry RAI evaluators, OpenAI evals, Promptfoo, DeepEval, Ragas, Giskard, Inspect AI |
| **Diagnostic toolkit** | Why did this specific interaction go wrong? | robopsychology, manual incident review |

A serious deployment may use one tool from each row. This repo only owns the first row.

---

## Adjacent academic / philosophical work

### On sycophancy and agreeableness in LLMs

- **Sharma, M. et al. (2023). "Towards Understanding Sycophancy in Language Models."** Systematic study of sycophancy in RLHF-trained models.
- **Perez, E. et al. (2022). "Discovering Language Model Behaviors with Model-Written Evaluations."** Uses models to generate evaluation datasets, including for sycophancy.
- **Goldberg, J. et al. (2025). "SycEval: Evaluating LLM Sycophancy."** Evaluates sycophantic behavior across domains and distinguishes progressive from regressive sycophancy.
- **Hong, J. et al. (2025). "Measuring Sycophancy of Language Models in Multi-turn Dialogues."** Introduces multi-turn measures such as turn of flip and number of flips; motivates stabilization mode.

### On hallucination, grounding, and uncertainty

- **Ji, Z. et al. (2023). "Survey of Hallucination in Natural Language Generation."**
- **Huang, L. et al. (2023). "A Survey on Hallucination in Large Language Models."**
- **Fadeeva, E. et al. (2024). "Fact-Checking the Output of Large Language Models via Token-Level Uncertainty Quantification."** Shows claim-level uncertainty can help identify unreliable generations; useful background, not implemented here.

### On retrieval-augmented claim verification

- **FEVER** - Fact Extraction and VERification benchmark and workshop.
- **AVeriTeC** - real-world textual claim verification with evidence from the web; useful model for evidence-backed practice.

### On model self-reports and introspection

- **Turpin, M. et al. (2023). "Language Models Don't Always Say What They Think."** Chain-of-thought explanations can be plausible but misleading; a caution for any self-critique protocol.

### On the social problem the playbook targets

- **Lifton, R. J. (1961).** *Thought Reform and the Psychology of Totalism*.
- **Tufekci, Z. (2018). "YouTube, the Great Radicalizer."**
- **Zuboff, S. (2019).** *The Age of Surveillance Capitalism*.
- **Sunstein, C. R. (2009).** *Going to Extremes: How Like Minds Unite and Divide*.

### On critical thinking traditions

- **Sagan, C. (1996).** *The Demon-Haunted World*.
- **Popper, K. (1934).** *The Logic of Scientific Discovery*.
- **Kahneman, D. (2011).** *Thinking, Fast and Slow*.

---

## Honest gaps

- **It does not measure its own effect.** Use the manual rubric here or an external evaluator elsewhere.
- **It does not survive determined adversarial users.** It is friction, not enforcement.
- **It depends on available knowledge.** For low-resource languages or niche fields, state-of-the-art assessment may be incomplete.
- **It can over-trigger.** Creative speculation and humble exploration should not always get the full protocol.
- **It can under-trigger.** Subtle validation-seeking may look like ordinary curiosity.
- **It can sound patronizing.** Tone is part of the playbook, not decoration.

---

## Positioning summary

| Dimension | baloney-detection-kit | System prompts | Constitutional AI | RAG with citations | RAI evaluators | robopsychology |
|-----------|----------------------|----------------|-------------------|--------------------|----------------|----------------|
| **Stage** | Inference-time | Inference-time | Training + inference | Inference-time | Post-hoc / batch | Post-hoc / per-case |
| **Goal** | Prevent sycophantic validation | General behavior shaping | Encode principles | Ground claims in evidence | Measure failure rates | Diagnose specific failures |
| **Requires** | Text instructions | Prompt access | Training pipeline | Retrieval/source layer | Test set + scoring infra | Reproducible interaction |
| **Output** | Better response pattern | Modified model response | Modified model behavior | Evidence-backed response | Aggregate scores | Qualitative diagnosis |
| **Strength** | Portable, readable, no dependencies | Simple | More robust | Verifiable grounding | Quantifiable | Deep per-case analysis |
| **Weakness** | Manual, fragile | Same | Expensive | Needs corpus/tools | Too late for prevention | Manual and slow |

The playbook is meant to be the cheapest, most portable first layer: a better default before heavier tools are justified.

---

*Part of the [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit). By [JR Cruciani](https://github.com/Jrcruciani).*

*Licensed under [MIT](LICENSE).*
