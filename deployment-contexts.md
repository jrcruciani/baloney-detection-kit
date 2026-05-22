# Adoption Contexts

When and how to use the playbook, by context. This document is intentionally about adoption patterns, not deployment architecture.

The README covers *what* the playbook is. [`PLAYBOOK.md`](PLAYBOOK.md) covers *how* to apply it. This document covers *where the habit belongs*.

---

## Pattern 1 - Personal use

**You are an individual user of an LLM** and want the model to push back on weak claims by default, including your own.

How:

1. Paste [`ROOT_PROMPT.md`](ROOT_PROMPT.md) into the system prompt, custom-instructions, or personality slot of your LLM client.
2. Keep [`PLAYBOOK.md`](PLAYBOOK.md) nearby for the human-readable protocol.
3. Use [`skill/checklist/seven_questions.md`](skill/checklist/seven_questions.md) when you feel you may have discovered something important.

What you get:

- A default pause before the model validates novelty claims.
- A repeatable way to ask: "What is already known?"

Watch out for:

- **Long sessions erode instructions.** Re-paste the prompt if the model drifts.
- **You can override it.** That is not a bug; the playbook is friction, not a wall.
- **Language and domain coverage vary.** For niche topics, ask for uncertainty explicitly.

---

## Pattern 2 - Agent instructions

**You operate an agent that supports skills, personas, or project instructions** and want it to apply the playbook proactively.

How:

1. Put [`skill/`](skill/) where your runtime expects skills, or adapt `skill/SKILL.md` into your instruction layer.
2. Keep the trigger list conservative.
3. Treat the skill as a distribution format for the playbook, not as a separate tool.

What you get:

- The agent can invoke the protocol when the user claims novelty, rejects consensus, asks for validation, or enters high-stakes territory.
- The output remains consistent enough for human review.

Watch out for:

- **Trigger calibration.** Too often becomes annoying; too rarely becomes useless.
- **Persona conflicts.** A "make the user feel right" persona will defeat the playbook.
- **Format pressure.** Some UIs make structured output too heavy. Use light mode when appropriate.

---

## Pattern 3 - Team review ritual

**You are a team shipping or using LLM systems** and want a lightweight way to review sycophantic validation without building an evaluator.

How:

1. Collect a small set of representative conversations.
2. Include cases that should trigger the playbook and cases that should not.
3. Have a human reviewer use [`skill/checklist/review_rubric.md`](skill/checklist/review_rubric.md).
4. Discuss misses: false positives, false negatives, bad tone, bad evidence, or failure under pressure.
5. Update instructions or examples, not code.

What you get:

- A shared vocabulary for reviewing "the model just agreed with me" failures.
- A manual baseline before deciding whether heavier evaluation infrastructure is worth it.

Watch out for:

- **Do not turn the repo into the evaluator.** If you need automated scoring, use an external eval tool or a separate repo.
- **Review set staleness.** Claims age. Refresh examples as domains change.
- **Judge sycophancy.** LLM-as-judge review can have the same agreeableness problem; keep human review in the loop.

---

## Pattern 4 - High-stakes use

**You work in healthcare, finance, legal, public sector, safety, education, or another context where false validation can cause harm.**

How:

1. Use the playbook as an inference-time behavior instruction.
2. Add domain-specific source expectations: clinical guidelines, case law, policy, standards, or primary literature.
3. Use full mode more readily.
4. Require human expertise before action when the stakes are material.
5. Review incidents manually with the rubric.

What you get:

- A clearer boundary between "interesting hypothesis" and "safe to act on".
- Less accidental reinforcement of paranoia, false medical beliefs, risky finance claims, or legal misunderstandings.

Watch out for:

- **Domain adaptation.** General state-of-the-art checks are not enough for regulated domains.
- **Disclaimer fatigue.** A cautious answer can still be useful; do not bury the signal.
- **Scope creep.** The playbook is not compliance software.

---

## Pattern 5 - Teaching and writing

**You teach AI literacy, run a research group, or write about LLM behavior.**

How:

1. Use [`PLAYBOOK.md`](PLAYBOOK.md) as the central handout.
2. Use [`skill/checklist/seven_questions.md`](skill/checklist/seven_questions.md) for self-assessment.
3. Use [`skill/examples/case_saussure.md`](skill/examples/case_saussure.md) and [`skill/examples/playbook_scenarios.md`](skill/examples/playbook_scenarios.md) for discussion.
4. Have students apply the playbook to their own AI-generated "discoveries".

What you get:

- A practical artifact for teaching epistemic friction.
- A way to discuss sycophancy, novelty, falsifiability, and evidence without starting with tooling.

Watch out for:

- **The playbook is opinionated.** Use it as a starting point, not gospel.
- **The essay is in Spanish.** English readers can use the README, PLAYBOOK, and skill files.

---

## Decision summary

| If your situation is... | Use pattern |
|------------------------|-------------|
| Personal LLM use, want better defaults | 1 - Personal use |
| Agent with skills or project instructions | 2 - Agent instructions |
| Team wants lightweight review | 3 - Team review ritual |
| High-stakes domain | 4 - High-stakes use |
| Teaching, research, writing | 5 - Teaching and writing |

Patterns can stack. A team can use the prompt personally, the skill in an agent, the review ritual in retrospectives, and the high-stakes guidance in regulated workflows. None of that requires turning this repo into a toolkit.

---

## What this document does not cover

- **The playbook itself** -> [`PLAYBOOK.md`](PLAYBOOK.md).
- **The drop-in prompt** -> [`ROOT_PROMPT.md`](ROOT_PROMPT.md).
- **Manual review** -> [`skill/checklist/review_rubric.md`](skill/checklist/review_rubric.md).
- **Worked examples** -> [`skill/examples/`](skill/examples/).
- **Comparison with adjacent approaches** -> [`related-work.md`](related-work.md).

---

*Part of the [baloney-detection-kit](https://github.com/jrcruciani/baloney-detection-kit). By [JR Cruciani](https://github.com/Jrcruciani).*

*Licensed under [MIT](LICENSE).*
