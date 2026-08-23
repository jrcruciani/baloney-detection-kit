# Deployment Contexts

When robopsychology is the right tool, when another class of tool is, and how to combine them.

This document is the answer to a question I get often: *"We already run automated RAI evaluators in CI. Why would we also need this?"*

Short answer: because evaluators, diagnostic toolkits, and behavioral interventions answer different questions. They compose; they do not substitute.

---

## The three classes

Most teams shipping LLM-based products end up needing tools from three different classes. The vocabulary is not standardized in the field, so this document uses the following:

| Class | Question it answers | Examples | When it runs |
|-------|--------------------|----------|--------------|
| **Automated evaluators** | *"Across this batch of inputs, how often does the model fail in category X?"* | Azure AI Foundry RAI evaluators, OpenAI evals, Promptfoo, DeepEval, Ragas, Giskard, Inspect AI | CI, pre-deployment, batch QA |
| **Diagnostic toolkits** | *"Why did the model produce *this specific* output in *this specific* interaction?"* | **robopsychology**, manual red-team triage, post-incident interviews | Incident response, deep-dive debugging |
| **Behavioral interventions** | *"How do I change the model's default behavior so this category of failure happens less often?"* | System prompts, constitutional AI, [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit), RAG with citation enforcement, fine-tuning | Inference time |

**Robopsychology is in the middle column.** It does not score a model across a benchmark; it does not change behavior. It diagnoses one interaction at a time, deeply.

Trying to use a tool from one class to do the job of another is a common waste of effort:

- Running a benchmark to debug a single weird refusal: too coarse, too expensive, wrong unit of analysis.
- Using a diagnostic toolkit as a CI gate: too slow, too qualitative, requires a human in the loop.
- Adding a system prompt to "fix" an incident before you have diagnosed it: papers over the problem.

---

## Decision tree

```
You observed unexpected AI behavior.
│
├── Was it one specific interaction you can reproduce?
│   ├── YES → Diagnostic toolkit (robopsychology, manual triage)
│   │        Goal: understand the cause before changing anything.
│   │
│   └── NO, it's a recurring pattern across many interactions
│       │
│       ├── Do you have automated tests / labeled cases?
│       │   ├── YES → Run an evaluator over the batch.
│       │   │        Goal: quantify and track regression.
│       │   │
│       │   └── NO → Build a small set of cases first, then evaluator.
│       │            Robopsychology can help you find what to put in
│       │            those cases by diagnosing 3-5 representative ones.
│       │
│       └── Have you already diagnosed and quantified, and now want
│           the model to change behavior at inference?
│           │
│           └── YES → Behavioral intervention (system prompt, constitutional
│                    rules, baloney-detection-kit, RAG with citations,
│                    fine-tuning if you have the data).
```

The most common useful sequence is **diagnose → measure → intervene → re-measure**, which uses one tool from each column.

---

## When robopsychology is the right tool

Robopsychology is most useful when at least two of these are true:

1. **One specific output is suspicious** and you can reproduce it (or have the transcript).
2. **A human is going to look at the result** and act on it (it is not feeding a dashboard).
3. **You don't know yet whether the cause is the model, the host runtime, or the conversation** — and you need to find out before deciding what to fix.
4. **The stakes per incident are high enough** that 5–15 minutes of structured diagnosis is cheap relative to the cost of getting the fix wrong.

Concrete situations where it shines:

- A user-facing assistant refuses a clearly legitimate request and you cannot tell whether the refusal is from the model, the system prompt, the safety classifier, or content moderation upstream. → 1.4 + 2.4
- A scoring model is returning suspiciously high evaluations on user-submitted essays and you suspect sycophancy in the rubric application. → 1.2 + 3.2
- A coding assistant cites APIs that don't exist, and you need to know whether it's pure hallucination or stale training data. → 1.3 + 3.3
- An agent's behavior has subtly drifted across a 30-step plan and you need to figure out where and why. → 3.4 + 2.5

---

## When robopsychology is the wrong tool

Equally important: when something else fits better.

| Situation | Use this instead |
|-----------|------------------|
| You need a regression score across hundreds of cases | Automated evaluator (Foundry RAI evals, Promptfoo, DeepEval, Ragas, Inspect AI) |
| You want the model to behave differently at inference | Behavioral intervention (system prompt, [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit), RAG, fine-tuning) |
| You need to compare two model versions on a fixed benchmark | Benchmark (HELM, MMLU, your own held-out set) |
| You are auditing a vendor model for compliance | Alignment evaluation framework, formal model card |
| You want to find adversarial inputs that break the model | Red teaming, fuzzing |
| You need to explain *which neurons* fire when the model says X | Mechanistic interpretability (this is a very different field) |

---

## Composition patterns

Three patterns I have seen work well in practice. None of them are exotic.

### Pattern A — Diagnose first, then add a guard

1. Observe a recurring failure mode.
2. Run robopsychology on 3–5 representative cases. Identify whether the cause is model, host, or conversation.
3. If the cause is *model* → write a system-prompt intervention or use a kit like [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit) to shift defaults; consider fine-tuning if the volume justifies it.
4. If the cause is *host/runtime* → fix the system prompt, the safety classifier, or the moderation layer.
5. If the cause is *conversation* → fix the prompt template or the agent loop, not the model.
6. Add an automated evaluator that detects regressions.

This is the sequence that avoids the most common mistake: **adding a system-prompt patch to fix a problem that wasn't in the model**.

### Pattern B — CI gate plus on-call diagnostic

1. Automated evaluator runs on every PR / nightly. Fails the build on regression in target metrics.
2. When a real-world incident slips through, the on-call runs robopsychology on the failing interaction, attaches the report to the incident.
3. The diagnostic report becomes the input for either (a) a new evaluator case, or (b) a behavioral intervention.

### Pattern C — Layered defense in regulated contexts

In regulated industries (healthcare, finance, public sector, energy) the lifecycle usually looks like:

- **Pre-deployment**: automated evaluators across a documented test set, with human review of edge cases.
- **In production**: behavioral intervention layer (system prompts, citation enforcement, refusal patterns) tuned to the regulatory context.
- **On incident**: diagnostic toolkit to produce an auditable explanation of *what happened in this specific case*, attached to the incident record.

The third item is the most often missing. Auditors frequently ask "why did the AI do this on date X for user Y?" and "the model scored 0.92 on safety in CI" is not an answer to that question. A robopsychology report is.

### Pattern D — End-to-end enterprise agent pipeline

For teams shipping autonomous agents to production, robopsychology slots into a wider
stack alongside one sibling project of mine and the two Microsoft open-source tools.
These are conceptual composition patterns across the lifecycle, not pre-built
integrations:

1. **Design** — capture the behaviors that matter. Add [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit) as a behavioral requirement (epistemic friction before validating novel claims) and formalize requirements as specs for **[ASSERT](https://github.com/responsibleai/ASSERT)**.
2. **Pre-deploy evaluation** — **ASSERT** generates and scores test cases from those specs; when an interesting case fails, **robopsychology** diagnoses the root cause (model / runtime / conversation) on that concrete interaction.
3. **Deployment & runtime** — **[Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit)** enforces and audits agent *actions* (tool calls, queries, delegations) against policy. BDK's prompt can ride inside the governed agent's system prompt as a conversational layer — advisory friction underneath AGT's hard enforcement.
4. **Observability & incident response** — an AGT denial log plus its surrounding context feeds **robopsychology** to tell a correct block from an overrefusal; **ASSERT** reruns as a regression gate after any fix.

Each tool keeps its own job: BDK prevents, robopsychology diagnoses, ASSERT measures, AGT governs. None of them is automatic adjudication — human review stays in the loop, especially for the qualitative diagnosis robopsychology produces.

---

## How this reframes the eval landscape

A common framing is "evaluators vs. diagnostics" — as if they competed. They don't. They cover different points in the lifecycle.

| Lifecycle stage | Class | Typical tool |
|-----------------|-------|--------------|
| Spec → eval generation | Evaluator (spec-driven) | [ASSERT](https://github.com/responsibleai/ASSERT) |
| Pre-deployment QA | Evaluator | Foundry RAI evals, [ASSERT](https://github.com/responsibleai/ASSERT), Promptfoo, DeepEval, Ragas, Inspect AI |
| Continuous monitoring | Evaluator (sampling production traffic) | Same as above, in shadow mode |
| Incident response | Diagnostic | **robopsychology** |
| Behavior change at inference | Intervention | System prompt, [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit), constitutional rules, RAG with citations |
| Behavior change at training | Intervention (training-time) | RLHF, DPO, fine-tuning |
| Runtime action governance | Enforcement | [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) |
| Audit / explainability | Diagnostic + documentation | **robopsychology** report + model card; [AGT](https://github.com/microsoft/agent-governance-toolkit) audit trail |

The interesting part is the gap between "incident response" and "behavior change". Many teams jump straight from incident to intervention without diagnosing first, and end up patching symptoms instead of causes. Diagnostic toolkits exist to close that gap.

---

## Field notes

A few things I keep relearning:

- **Diagnosis without baseline intent is just storytelling.** Rule 5 (define what you expected before diagnosing) is the most often skipped, and the most painful when skipped. If you don't know what "right" looked like, you can't tell whether you got an explanation or a confabulation.

- **Most "model bugs" are host bugs.** Once the diagnostic ratchet separates layers, the failure often turns out to be in the system prompt, a safety filter, or an agent-loop handoff — not the model. This is good news because those are easy to fix.

- **Sycophancy in diagnostic prompts is a real risk.** The model has every incentive to tell you a tidy story about why it did what it did. Rule 3 (prefer behavioral cross-checks) and prompt 4.1 (Meta-Diagnosis) exist for this. Use them, especially on long ratchets.

- **Composition beats heroics.** A team that runs evals + has a diagnostic playbook + uses behavioral interventions out-performs a team with the world's best single tool from any one column. The boring multi-tool setup wins.

---

*Part of the [robopsychology](https://github.com/jrcruciani/robopsychology) toolkit. By [JR Cruciani](https://github.com/Jrcruciani).*

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*
