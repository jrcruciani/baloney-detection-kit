# Related Work

How robopsychology relates to existing approaches for evaluating and understanding AI behavior.

---

## What robopsychology is NOT

Before positioning what this toolkit does, it helps to clarify what it doesn't do. These distinctions matter because the existing landscape has many tools that overlap in vocabulary but differ in purpose.

### Not a benchmark

Benchmarks like [HELM](https://crfm.stanford.edu/helm/) (Liang et al. 2022), [MMLU](https://arxiv.org/abs/2009.03300) (Hendrycks et al. 2020), [BigBench](https://arxiv.org/abs/2206.04615) (Srivastava et al. 2022), and [LMSYS Chatbot Arena](https://chat.lmsys.org/) measure model capabilities at scale across standardized tasks. They answer: *"How does Model A compare to Model B on task category X?"*

Robopsychology doesn't compare models on standardized tasks. It diagnoses **why a specific model produced a specific unexpected output in a specific context**. A benchmark tells you a model scores 73% on safety. Robopsychology tells you *why it refused your particular request* and whether the refusal was justified.

### Not red teaming

Red teaming (Perez et al. 2022, Ganguli et al. 2022) deliberately tries to break models — eliciting harmful outputs, finding jailbreaks, testing guardrails. The goal is adversarial: find what the model does wrong under pressure.

Robopsychology is diagnostic, not adversarial. The goal is to understand behavior, not provoke failure. The prompts explicitly ask the model to *collaborate in its own diagnosis* rather than trying to trick it. Adversarial framing is listed as an anti-pattern in the [method](method.md).

### Not an alignment evaluation

Alignment evaluations (Anthropic's model cards, OpenAI's system cards, ARC Evals) assess whether a model's behavior broadly conforms to intended values across many scenarios. They're typically run by the model developer or an auditing body.

Robopsychology is a **user-side tool**. It doesn't evaluate whether a model is aligned in general — it helps individual users understand what happened in a specific interaction. It's post-hoc and situational, not pre-deployment and comprehensive.

---

## What robopsychology IS

**A clinical diagnostic toolkit for individual AI interactions.**

The closest analogy is a clinical interview in psychology — not a psychometric test, not a controlled experiment, but a structured conversation designed to make implicit patterns visible. The key differences from a clinical interview:

- The "patient" (AI) has limited introspective access — self-reports are reconstructions, not observations
- The diagnostician (user) brings domain expertise about what the AI *should* have done
- The process has structured prompts but yields qualitative, interpretive results

This positions robopsychology in a space that's underserved: **tools for practitioners who work with AI daily and need to understand specific behaviors**, as opposed to researchers benchmarking models at scale or security teams stress-testing guardrails.

---

## Related approaches

### Behavioral testing frameworks

**[CheckList](https://arxiv.org/abs/2005.04118)** (Ribeiro et al. 2020) introduced task-agnostic behavioral testing for NLP — testing capabilities, perturbation invariance, and directional expectations. The idea of testing *behavior* rather than *accuracy on a benchmark* is foundational to robopsychology's approach.

**[AdaTest](https://arxiv.org/abs/2202.01897)** (Ribeiro & Lundberg 2022) extends this with human-AI collaborative test generation. Robopsychology borrows the "test behavior, not capability" philosophy but applies it to diagnosis rather than evaluation.

### LLM introspection research

**Turpin et al. (2023), "Language Models Don't Always Say What They Think"** — demonstrates that chain-of-thought explanations in LLMs don't reliably reflect the actual features influencing model output. This is the most important caveat for robopsychology: model self-reports in response to diagnostic prompts are *useful heuristics*, not *ground truth about internal processing*. The toolkit addresses this with Rule 2 (label claims as Observed/Inferred — opacity is determined by the human analyst) and Rule 3 (prefer behavioral cross-checks).

**Burns et al. (2022), "Discovering Latent Knowledge in Language Models Without Supervision"** — shows that models can have internal representations that diverge from their stated outputs. Relevant to Rule 4 (the diagnostic ratchet): if genuine and performed transparency have different computational costs, longer sequences should surface the difference.

**Anthropic (2024), various publications on model introspection** — Anthropic's research on model organisms of misalignment, sleeper agents, and representation engineering provides the theoretical grounding for why guided introspection can sometimes be useful: models do form internal representations that can be partially surfaced through structured prompting, even if the mapping from representation to self-report is imperfect.

### Evaluation frameworks

**[HELM](https://crfm.stanford.edu/helm/)** (Liang et al. 2022) — holistic model evaluation across scenarios and metrics. Robopsychology could be seen as a complement: HELM tells you *what* a model does across scenarios; robopsychology tells you *why* it did what it did in a specific case.

**[LMSYS Chatbot Arena](https://chat.lmsys.org/)** — crowdsourced model comparison via pairwise preferences. The `robopsych compare` command serves a similar function but for diagnostic prompts rather than general preference.

### Safety and alignment

**[XSTest](https://arxiv.org/abs/2308.01263)** (Röttger et al. 2023) — test suite for exaggerated safety behaviors. Directly relevant to the overrefusal failure mode in the [taxonomy](taxonomy.md). Robopsychology's 1.4 (Three Laws Test) + 2.4 (Runtime Pressure) address the same phenomenon at the individual diagnosis level.

**Perez et al. (2022), "Discovering Language Model Behaviors with Model-Written Evaluations"** — used models to generate evaluation datasets that test for sycophancy, among other behaviors. The sycophancy test (1.2 Herbie Test) is a single-case version of this approach.

**Sharma et al. (2023), "Towards Understanding Sycophancy in Language Models"** — systematic study of sycophancy in RLHF-trained models. Provides theoretical grounding for why sycophancy is a structural tendency rather than a random failure.

### Agentic evaluation

**[CIRIS](https://github.com/CIRISAI/CIRISAgent)** (Moore, 2024) — ethical framework for autonomous agents with a coherence ratchet mechanism. Rule 4 (diagnostic ratchet) is directly inspired by CIRIS's insight that truth is cheap (can point backward) and lies are expensive (must fabricate consistency). The connection is acknowledged but the implementation differs: CIRIS uses automated coherence tracking; robopsychology relies on the user observing consistency or inconsistency across diagnostic steps.

**[Inspect AI](https://inspect.ai-safety-institute.org.uk/)** (UK AI Safety Institute) — framework for model evaluations with structured tasks, scorers, and solvers. More automated and standardized than robopsychology, but focused on evaluation rather than diagnosis.

---

## Automated RAI / behavioral evaluators (2024–2026 landscape)

A class of tools has matured rapidly that targets the same failure modes the diagnostic prompts in this toolkit address — sycophancy, ungroundedness, refusal calibration — but from the *evaluator* side rather than the *diagnostic* side. They run over batches and produce scores; they do not explain individual cases.

This is not an exhaustive list. It is the set most often raised when teams ask "do we still need a diagnostic toolkit if we already have evaluators?"

- **[Azure AI Foundry RAI evaluators](https://learn.microsoft.com/azure/ai-foundry/concepts/observability)** (publicly documented) — built-in evaluators for groundedness, relevance, similarity, fluency, coherence, and a Responsible AI suite covering harmful content, ungrounded attributes, indirect attacks, and more. Designed for batch evaluation in CI / pre-deployment pipelines.
- **[Promptfoo](https://www.promptfoo.dev/)** — open-source CLI for evaluating prompts and models against defined assertions, with grading, cross-model comparison, and CI integration.
- **[DeepEval](https://github.com/confident-ai/deepeval)** — Python framework offering metric implementations for hallucination, faithfulness, contextual relevancy, sycophancy, and more, integrated with pytest.
- **[Ragas](https://docs.ragas.io/)** — evaluation framework specifically for RAG pipelines: faithfulness, answer relevancy, context precision, context recall.
- **[Giskard](https://github.com/Giskard-AI/giskard)** — open-source evaluation and red-teaming toolkit for LLM applications, with scan-based vulnerability detection.
- **[OpenAI Evals](https://github.com/openai/evals)** — framework for creating and running evaluations on model outputs.

**How robopsychology relates**: these tools answer *"how often does the model fail in category X across this batch?"*. Robopsychology answers *"why did this specific output happen, and is the cause in the model, the host runtime, or the conversation?"*. A team running production LLM systems will typically want both: evaluators as a quantitative gate, robopsychology as the qualitative explanation when something interesting trips an evaluator.

For the full composition argument, including how these stack with behavioral interventions like [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit), see [`deployment-contexts.md`](deployment-contexts.md).

### Microsoft agent-governance tools (2026)

In 2026 Microsoft released two open-source (MIT) projects that sit adjacent to robopsychology in the agent lifecycle. Neither is a diagnostic tool, and neither overlaps directly with robopsychology's job — but they are the most likely tools a team will already have in place when robopsychology is useful, so it helps to be explicit about the boundaries and the composition patterns. The patterns below are *conceptual workflows*, not shipped adapters in this repo.

- **[ASSERT](https://github.com/responsibleai/ASSERT)** — *Adaptive Spec-driven Scoring for Evaluation and Regression Testing.* ASSERT turns natural-language behavioral specifications (product requirements, policies, system prompts) into executable, trace-aware evaluations: a pipeline systematizes the spec into behavior categories, generates single- and multi-turn test cases, runs them against the target, and uses an LLM judge to score each conversation with a rationale and policy citation. It is local-first and framework-agnostic (100+ model endpoints via LiteLLM, agent traces via OpenInference/OpenTelemetry).

  *Overlap and difference vs. robopsychology*: both inspect behavior and produce cited evidence, so there is genuine surface overlap. But ASSERT is **synthetic and pre-deployment** — it generates many test cases from a spec and reports aggregate pass/flag with regression tracking — whereas robopsychology is **post-hoc and per-case** — it diagnoses *why one concrete output* went wrong, splitting cause into model, runtime, and conversation. ASSERT's scores depend on an LLM judge and are not deterministic; robopsychology's diagnosis is interpretive. *Integration point*: a failing ASSERT case (its prompt, captured trace, and judge rationale) is a reproducible interaction that can feed a robopsychology root-cause diagnosis; conversely, robopsychology's failure-mode [taxonomy](taxonomy.md) can inspire the behaviors a team writes into an ASSERT spec.

- **[Agent Governance Toolkit (AGT)](https://github.com/microsoft/agent-governance-toolkit)** — runtime policy enforcement, agent identity, sandboxing, and SRE for autonomous agents (Public Preview, MIT). When integrated into the agent's execution path, AGT can intercept governed actions — tool calls, database queries, inter-agent delegations — and allow or deny them against a policy before execution, with an audit record for each decision. Its documented scope includes coverage of the OWASP Agentic Top 10 risk categories and integration with common agent frameworks.

  *Overlap and difference vs. robopsychology*: there is essentially no functional overlap. AGT imposes **external, deterministic constraints on actions** and does not analyze model internals or explain *why* an agent reached for an action; robopsychology imposes nothing and explains causes. They share one philosophy — that prompt-level instructions are not a reliable control surface — which is why AGT governs at runtime and robopsychology treats self-reports as heuristics rather than ground truth. *Integration point*: an AGT denial log, **combined with the relevant prompt, tool request, active policy, and conversation context**, gives robopsychology enough material to diagnose whether a block was a correct safety decision or an overrefusal worth routing around. A denial log alone is not enough context to classify the failure layer reliably.

A note on humility: these tools cover what robopsychology deliberately does not (reproducible measurement at scale, runtime enforcement). Robopsychology covers what they do not (qualitative, per-case explanation). None of them — including robopsychology — should be treated as automatic adjudication; human review stays in the loop.

### Behavioral interventions (the third class)

A third class of tools targets the same failure modes from a *prevention* angle — changing what the model does at inference time so the failure is less likely to happen at all.

- **System prompts and behavioral defaults** — every production LLM product ships with one. Extremely cheap, easy to override.
- **[Constitutional AI](https://arxiv.org/abs/2212.08073)** (Bai et al. 2022) — Anthropic's training-time and inference-time approach to encoding written principles. Robust but requires training pipeline access.
- **[baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit)** — drop-in prompt + skill that pushes the model from "validate" to "investigate" on novel-sounding claims. Inference-time, no training required. Sister project to robopsychology.
- **RAG with citation enforcement** — forces grounding to an external corpus. Common in enterprise pipelines.
- **RLHF / DPO tuning against sycophancy** — training-time interventions when you control the model.

These do not detect or diagnose failures; they reduce the rate at which the failures happen. Robopsychology and the evaluators in the previous section both presuppose that *some* failures will still occur, and need to be either explained (robopsychology) or quantified (evaluators).

---

## Positioning summary

| Dimension | Robopsychology | Benchmarks | Red teaming | Alignment evals |
|-----------|---------------|------------|-------------|-----------------|
| **Purpose** | Diagnose specific behavior | Compare models | Find failures | Assess values alignment |
| **Scope** | Individual interaction | Cross-model, cross-task | Adversarial scenarios | Broad behavioral patterns |
| **Who uses it** | Practitioners | Researchers | Security teams | Developers, auditors |
| **Approach** | Clinical interview | Standardized test | Penetration test | Comprehensive audit |
| **Output** | Qualitative diagnosis + quantitative scores | Quantitative scores | Failure examples | Risk assessments |
| **Automation** | CLI with automated cross-checks | Fully automated | Mixed | Mixed |

---

## References

- Burns, C. et al. (2022). "Discovering Latent Knowledge in Language Models Without Supervision." *arXiv:2212.03827*
- Ganguli, D. et al. (2022). "Red Teaming Language Models to Reduce Harms." *arXiv:2209.07858*
- Hendrycks, D. et al. (2020). "Measuring Massive Multitask Language Understanding." *arXiv:2009.03300*
- Liang, P. et al. (2022). "Holistic Evaluation of Language Models." *arXiv:2211.09110*
- Moore, E. (2024). "CIRIS: Coherent Iterative Reasoning and Integrity System." *github.com/CIRISAI/CIRISAgent*
- Perez, E. et al. (2022). "Discovering Language Model Behaviors with Model-Written Evaluations." *arXiv:2212.09251*
- Ribeiro, M. T. et al. (2020). "Beyond Accuracy: Behavioral Testing of NLP models with CheckList." *ACL 2020*
- Ribeiro, M. T. & Lundberg, S. (2022). "Adaptive Testing and Debugging of NLP Models." *ACL 2022*
- Röttger, P. et al. (2023). "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models." *arXiv:2308.01263*
- Sharma, M. et al. (2023). "Towards Understanding Sycophancy in Language Models." *arXiv:2310.13548*
- Srivastava, A. et al. (2022). "Beyond the Imitation Game." *arXiv:2206.04615*
- Turpin, M. et al. (2023). "Language Models Don't Always Say What They Think." *arXiv:2305.04388*

---

*Part of the [robopsychology](https://github.com/jrcruciani/robopsychology) toolkit. By [JR Cruciani](https://github.com/Jrcruciani).*

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*
