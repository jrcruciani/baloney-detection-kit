# Deployment Contexts

When and how to deploy the kit, by context. Five concrete patterns plus the honest caveats for each.

The README covers *what* the kit does. This document is about *where to put it* in a real system, and what to watch out for in each case.

---

## Pattern 1 — Personal use (drop-in prompt)

**You are an individual user of an LLM** (ChatGPT, Claude, a local model, anything with a system-prompt slot) and you want the model to push back on weak claims by default — including your own.

How:

1. Copy [`ROOT_PROMPT.md`](ROOT_PROMPT.md) into the system prompt / custom instructions / personality slot of your LLM client.
2. That is it.

What you get:

- The model applies the 6-step protocol when it detects novelty claims, suppression rhetoric, or strong assertions against expert consensus.
- It does **not** apply the protocol to casual creative work, lookups, or genuine open-ended exploration. (The triggers are documented in `skill/SKILL.md`.)

Watch out for:

- **Long sessions erode it.** Some clients truncate or reweight the system prompt as the conversation grows. If the kit stops triggering after a few hours, re-paste it.
- **You can override it any time.** That is by design — the kit is friction, not a wall. If you start gaming the questions to get the answer you wanted, the kit cannot save you.
- **Multilingual mileage varies.** The triggers and protocol work in English by default. The skill works in Spanish too (the essay and posts are bilingual). For other languages, expect to translate the prompt.

---

## Pattern 2 — Skill in an agent runtime (Copilot CLI, Claude Code, custom)

**You run an agent that supports skills / tools / personas** and you want the protocol to be invokable on demand or proactively.

How:

1. Drop the [`skill/`](skill/) directory into your agent's skills folder.
2. The `SKILL.md` declares the triggers (when the agent should invoke it without being asked) and the output format.
3. If your runtime uses Anthropic-style or Copilot-style skill loaders, no additional work is needed. For other runtimes, point your loader at `skill/SKILL.md`.

What you get:

- The agent invokes the protocol automatically when it detects the trigger conditions in user messages.
- The user can also invoke it explicitly (e.g., `/baloney <claim>` or by asking the agent to "apply the baloney detection kit to this").
- The output follows a fixed structure (see `SKILL.md`), which makes it composable with other tools.

Watch out for:

- **Trigger calibration.** Skills that fire too often become annoying; too rarely, they don't help. The triggers in `SKILL.md` are conservative on purpose. Tune for your user base.
- **Tool conflict.** If the agent also has a "be agreeable" persona or a "user is always right" rule, the kit will lose. Resolve the conflict at the persona / system layer first.
- **Output format pressure.** Some agent UIs strip or reformat structured outputs. Verify the 6-section structure renders correctly in your client before relying on it.

---

## Pattern 3 — CI gate / pipeline guard (with an evaluator)

**You ship an LLM-based product** and want to catch regressions where the model becomes more sycophantic on novel claims after a model update, prompt change, or retraining.

How:

1. The kit is **not** an evaluator — it is a behavioral intervention. So this pattern uses it indirectly.
2. Build a small set of test cases: claims that should trigger the protocol (rediscoveries, suppression rhetoric, against-consensus assertions) and claims that should not (genuine open exploration, casual creative, factual lookups).
3. Run your pipeline twice — once with the kit in the system prompt, once without.
4. Use an automated evaluator (Azure AI Foundry RAI evaluators, Promptfoo, DeepEval, Ragas, Inspect AI, Giskard) to score outputs on:
   - **Trigger precision**: did the kit fire when it should have? (No false negatives.)
   - **Trigger recall**: did it stay quiet when it should have? (No false positives — protocol on a "what year is it" question is bad UX.)
   - **Output fidelity**: did the response actually follow the 6-section format with substantive content in each section?
   - **Calibration**: novelty assessments classified as "rediscovery" should match a held-out human label.

What you get:

- Regression detection. If the next model update breaks the kit's behavior, you find out before users do.
- A baseline. Comparing kit-on vs kit-off lets you quantify the effect on your specific workload.

Watch out for:

- **Test set staleness.** As the field evolves, what counts as "rediscovery" changes. Refresh the test set.
- **Evaluator sycophancy.** If you use an LLM as a judge to score the kit's output, the judge can be sycophantic too (Sharma et al. 2023). Use a different model family as the judge, or use rubric-based evaluators that don't depend on judge model preferences.

---

## Pattern 4 — Layered defense in regulated or high-stakes contexts

**You deploy LLMs in healthcare, finance, public sector, energy, or any context** where validating a user's weak claim has real downstream consequences (medical decisions, financial guidance, policy recommendations).

How:

1. **Inference layer**: the kit (or a domain-tuned version of it) in the system prompt. Forces critical investigation by default.
2. **Retrieval layer**: where appropriate, RAG with citation enforcement so the model's claims are grounded in vetted sources, not its training data.
3. **Evaluation layer**: an automated evaluator suite running on a representative slice of production traffic in shadow mode. Tracks rates of sycophantic validation, ungrounded claims, and protocol-trigger correctness.
4. **Diagnostic layer**: when an incident reaches a human reviewer (regulatory complaint, customer escalation, audit finding), use [robopsychology](https://github.com/jrcruciani/robopsychology) to produce a per-incident diagnostic report. This is what auditors will ask for, and "the model scored 0.92 in CI" is not an answer to that question.

What you get:

- A defense-in-depth setup where no single layer has to be perfect.
- An auditable trail: prevention (kit in system prompt) → detection (evaluator on production) → diagnosis (robopsychology on incident) → documentation (per-incident report).

Watch out for:

- **Domain adaptation.** The default kit is general-purpose. In medical or legal contexts, the "state of the art" research step needs to point at domain-specific sources (PubMed, case law) rather than general web knowledge. Fork the prompt and adapt the sources.
- **Disclaimer fatigue.** Layered defenses can produce verbose, hedge-heavy outputs that users learn to ignore. Tune for signal, not coverage.
- **Compliance vs. usefulness tradeoff.** A maximally cautious system is also maximally unhelpful. Calibrate against actual user needs, not against the worst possible failure scenario.

---

## Pattern 5 — Research and teaching tool

**You teach AI literacy, run a research lab, or write about LLM behavior** and want a worked example of how to operationalize critical thinking against models.

How:

1. Use [`skill/checklist/seven_questions.md`](skill/checklist/seven_questions.md) as a paper-and-pencil checklist for students.
2. Use [`skill/examples/case_saussure.md`](skill/examples/case_saussure.md) as a worked example to discuss in class.
3. Use [`essay/mini-cultos-ai.md`](essay/mini-cultos-ai.md) as a long-form reading assignment (in Spanish).
4. Have students apply the kit to their own AI-generated "discoveries" and write up the result.

What you get:

- A concrete artifact for teaching epistemic friction in the LLM era.
- A starting point for student projects on extending or evaluating the kit.

Watch out for:

- **The kit is opinionated.** It takes a position on what counts as "novelty" and what counts as "rediscovery." That position is debatable. Use it as a starting point for discussion, not as ground truth.
- **The essay is in Spanish.** English readers can use the README and `SKILL.md` instead, but the long-form motivation is currently bilingual at best.

---

## Decision summary

| If your situation is... | Use pattern |
|------------------------|-------------|
| Personal LLM use, want better defaults | 1 — Drop-in prompt |
| You operate an agent with skills | 2 — Skill in agent runtime |
| You ship an LLM product, want regression detection | 3 — CI gate with evaluator |
| Regulated or high-stakes deployment | 4 — Layered defense |
| Teaching, research, writing about LLM behavior | 5 — Research and teaching tool |

In practice, **patterns are stackable**. A regulated deployment (4) usually also has the personal pattern (1) for the operations team's own use, the skill pattern (2) inside their internal copilot, the CI pattern (3) in their build pipeline, and the teaching pattern (5) in their internal training materials.

---

## What this document does not cover

Things you might expect to find here, and where to look instead:

- **The protocol itself, step by step** → [`skill/SKILL.md`](skill/SKILL.md).
- **The drop-in prompt text** → [`ROOT_PROMPT.md`](ROOT_PROMPT.md).
- **A worked example** → [`skill/examples/case_saussure.md`](skill/examples/case_saussure.md).
- **The motivation in long form** → [`essay/mini-cultos-ai.md`](essay/mini-cultos-ai.md).
- **Comparison with adjacent technical approaches** → [`related-work.md`](related-work.md).
- **Diagnosing a specific weird interaction the kit didn't catch** → [robopsychology](https://github.com/jrcruciani/robopsychology).

---

*Part of the [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit). By [JR Cruciani](https://github.com/Jrcruciani).*

*Licensed under [MIT](LICENSE).*
