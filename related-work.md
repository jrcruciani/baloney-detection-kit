# Related Work

How baloney-detection-kit relates to existing approaches in critical thinking, AI safety, and LLM behavior shaping.

This document exists because the kit is, by its own admission, **a re-framing, not an invention**. The honest thing to do is to map exactly what it borrows, what it adds, and what alternatives exist.

---

## What this kit IS

A **behavioral intervention** for LLMs, packaged as a drop-in prompt and as a skill. It changes the default behavior of a model from "elaborate and validate" to "research, contextualize, contrast, then respond." It is meant to run *at inference time*, before the model has had the chance to validate a weak claim.

It is not an evaluator. It is not a benchmark. It does not score the model. It does not detect failures after the fact. It tries to **prevent one specific failure mode — sycophantic validation of weak novel claims — by changing what the model does in the moment**.

---

## The intellectual lineage (already in the README)

The kit is a synthesis. The README and `SKILL.md` already credit the four primary sources:

- **Carl Sagan**, *The Demon-Haunted World* (1996) — the original Baloney Detection Kit.
- **Andrej Karpathy**, "A Recipe for Training Neural Networks" — state-of-the-art-first methodology.
- **Robert Jay Lifton**, *Thought Reform and the Psychology of Totalism* (1961) — eight criteria of thought reform / cult dynamics.
- **Karl Popper**, *The Logic of Scientific Discovery* (1934) — falsifiability.

This document does not re-summarize them. It positions the kit relative to the **technical** AI-safety landscape that has grown around the same problem the kit addresses.

---

## Adjacent technical approaches

The problem of "LLMs validate weak claims by default" is widely recognized. There are at least four families of technical responses. The kit is one of them; honest comparison helps users pick the right one.

### 1. System prompts and behavioral defaults

Most production LLM products ship with a system prompt that shapes default behavior — politeness, refusal patterns, persona, etc. The kit is, technically, **a specialized system prompt** focused on critical investigation defaults rather than generic helpfulness.

- **Difference**: most production system prompts optimize for *helpful, harmless, honest* in the abstract. The kit operationalizes one specific commitment — "do not validate a novel-sounding claim before checking the literature" — concretely enough to be testable.
- **Limitation**: like any system prompt, it can be overridden by user instructions, eroded by long contexts, or ignored by the model under pressure. It is friction, not a guarantee.

### 2. Constitutional AI and rule-based behavior shaping

Anthropic's constitutional AI (Bai et al. 2022) trains models to follow a set of written principles, used both at training time (RLAIF) and at inference time (model self-critique against the constitution).

- **Similarity**: both approaches encode behavioral principles as text the model can be asked to follow.
- **Difference**: constitutional AI bakes the principles into model weights via training. The kit is a **drop-in** that works on already-trained models without any access to weights or training pipelines. The price is that the kit is shallower — it lives in the prompt, not in the parameters.
- **When constitutional AI fits better**: you control training, want the behavior to be robust across many contexts, and can afford the training cycle.
- **When the kit fits better**: you don't control training (you are calling an API), you want to change behavior today, and you accept that prompt-level interventions are more fragile than weight-level ones.

### 3. RAG with citation enforcement

Retrieval-augmented generation pipelines often enforce citations — the model is required to ground every claim in retrieved sources, and unsupported claims are stripped or flagged. Tools like Perplexity, Phind, and several enterprise RAG frameworks operate this way.

- **Similarity**: both push the model toward grounding instead of free assertion.
- **Difference**: RAG with citations changes *where the model gets its claims* (an external corpus). The kit changes *how the model evaluates a claim before responding* (against its existing knowledge of the literature, plus the user's own claim). The kit does not require a retrieval index.
- **Compose**: the two stack well. A RAG pipeline gives the model evidence; the kit gives it a critical attitude toward both that evidence and the user's claim. Many "good" RAG-with-critique systems are doing some informal version of this composition already.

### 4. RLHF tuning against sycophancy

Several research lines (Sharma et al. 2023, Anthropic 2024, OpenAI various) describe training-time interventions that directly target sycophancy, including DPO and RLHF runs that reward disagreement with incorrect user assertions.

- **Similarity**: same target — reduce default agreeableness on factual matters.
- **Difference**: training-time, requires data and pipeline access, lives in the weights. The kit is inference-time, requires no training, lives in the prompt.
- **When training-time fits better**: you ship the model and want sycophancy reduction to be a *property of the model* available to all consumers, not a per-deployment add-on.
- **When the kit fits better**: you are deploying *on top of* a model you don't train. You want to change defaults today.

---

## Adjacent evaluation tools (detection, not prevention)

A natural confusion is between this kit and tools that **detect** sycophancy or hallucination *after the fact*. They are complementary, not redundant.

| Class | Question it answers | Examples |
|-------|---------------------|----------|
| **Behavioral intervention** (this kit) | *How do I make the model less likely to validate weak claims in the first place?* | baloney-detection-kit, system prompts, constitutional AI, RAG with citations, RLHF tuning |
| **Diagnostic toolkit** | *Why did the model say this in this specific case?* | [robopsychology](https://github.com/jrcruciani/robopsychology), manual triage |
| **Automated evaluator** | *Across many cases, how often does the model fail on sycophancy / hallucination / etc.?* | Azure AI Foundry RAI evaluators (sycophancy, ungroundedness), OpenAI evals, Promptfoo, DeepEval, Ragas, Giskard, Inspect AI |

A team that takes the problem of mini-cult validation seriously will end up using **at least one tool from each row**. The kit prevents at inference. Robopsychology diagnoses individual incidents. Evaluators measure aggregate behavior over time.

The detection-vs-prevention distinction matters because **a detection-only setup catches problems too late** — the user has already received the validating response. Prevention reduces the rate at which detection has anything to catch.

---

## Adjacent academic / philosophical work

Selected references for readers who want to go deeper than the four primary sources.

### On sycophancy and agreeableness in LLMs

- **Sharma, M. et al. (2023). "Towards Understanding Sycophancy in Language Models."** *arXiv:2310.13548* — systematic study of sycophancy in RLHF-trained models. Establishes that sycophancy is a structural tendency of preference-based training, not a random failure.
- **Perez, E. et al. (2022). "Discovering Language Model Behaviors with Model-Written Evaluations."** *arXiv:2212.09251* — uses models to generate evaluation datasets, including for sycophancy.

### On hallucination and grounding

- **Ji, Z. et al. (2023). "Survey of Hallucination in Natural Language Generation."** *ACM Computing Surveys.*
- **Huang, L. et al. (2023). "A Survey on Hallucination in Large Language Models."** *arXiv:2311.05232.*

### On model self-reports and introspection

- **Turpin, M. et al. (2023). "Language Models Don't Always Say What They Think."** *arXiv:2305.04388* — chain-of-thought explanations don't reliably reflect actual computation. Important caveat for any approach that asks the model to "reason about its own reasoning," including this kit.

### On constitutional AI and behavior shaping

- **Bai, Y. et al. (2022). "Constitutional AI: Harmlessness from AI Feedback."** *arXiv:2212.08073* — trains models to follow a written constitution. Closest training-time analog to what this kit does at inference time.

### On the social problem the kit targets

- **Lifton, R. J. (1961).** *Thought Reform and the Psychology of Totalism* — eight criteria of cult dynamics. Pre-LLM, but the criteria translate directly to one-on-one model interactions where the model plays the role of validating crowd. See `essay/mini-cultos-ai.md`.
- **Tufekci, Z. (2018). "YouTube, the Great Radicalizer."** *NYT.*
- **Zuboff, S. (2019).** *The Age of Surveillance Capitalism.*
- **Sunstein, C. R. (2009).** *Going to Extremes: How Like Minds Unite and Divide* — group polarization dynamics, applicable to a one-person-plus-LLM "group of two."

### On critical thinking traditions the kit borrows from

- **Sagan, C. (1996).** *The Demon-Haunted World* — the original Baloney Detection Kit.
- **Popper, K. (1934).** *The Logic of Scientific Discovery* — falsifiability.
- **Kahneman, D. (2011).** *Thinking, Fast and Slow* — System 1 / System 2 framing; the kit is, mechanically, an attempt to force System 2 evaluation in a setting that defaults to System 1.

---

## Honest gaps in this kit

Things the kit does **not** do, and where you should look elsewhere.

- **It does not measure its own effect.** There is no built-in evaluation harness. To measure whether the kit reduces mini-cult thinking in your deployment, you need an evaluator (Foundry RAI evals, Promptfoo, etc.) and a controlled comparison.
- **It does not survive determined adversarial users.** Anyone who actively wants to bypass the protocol can re-prompt, jailbreak, or simply ignore the output. The kit is friction, not enforcement.
- **It does not work equally well across languages and topics.** The state-of-the-art research step depends on the model's training coverage. For low-resource languages or niche fields, the kit will sometimes fail to identify rediscovery. This is a knowledge limitation of the underlying model, not of the protocol, but the user pays the cost.
- **It does not address agentic loops.** When a model calls itself in a long plan, the protocol applies only at the entry prompt. Drift during the loop is not addressed. For diagnosing what happened across an agent loop, see [robopsychology](https://github.com/jrcruciani/robopsychology) (specifically prompts 3.4 and 2.5).
- **It does not handle creative or speculative work.** As stated in `SKILL.md`, the protocol is intentionally not invoked for openly speculative writing or genuine open-ended exploration. Detecting the difference between "I am brainstorming" and "I have discovered" is itself a hard problem the kit punts on.

---

## Positioning summary

| Dimension | baloney-detection-kit | System prompts | Constitutional AI | RAG with citations | RAI evaluators | robopsychology |
|-----------|----------------------|----------------|-------------------|--------------------|-----------------|-----------------|
| **Stage** | Inference-time | Inference-time | Train + inference | Inference-time | Post-hoc / batch | Post-hoc / per-case |
| **Goal** | Prevent sycophantic validation | General behavior shaping | Encode principles | Force grounding to corpus | Measure failure rates | Diagnose specific failures |
| **Requires** | Prompt access | Prompt access | Training pipeline + data | Retrieval index + corpus | Test set + scoring infra | Reproducible interaction |
| **Output** | Modified model response | Modified model response | Modified model response | Modified model response | Aggregate scores | Qualitative diagnosis |
| **Strength** | Drop-in, no infra | Universal, simple | Robust across contexts | Verifiable grounding | Quantifiable, trackable | Causal explanation per case |
| **Weakness** | Fragile, can be overridden | Same | Needs training cycle | Needs corpus | Cannot explain *why* | Manual, slow per case |

A serious deployment will combine more than one of these. The kit is good at being one piece of that combination — specifically, the cheapest, most droppable piece available today.

---

*Part of the [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit). By [JR Cruciani](https://github.com/Jrcruciani).*

*Licensed under [MIT](LICENSE).*
