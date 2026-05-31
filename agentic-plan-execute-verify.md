# Agentic Plan -> Execute -> Verify Integration

How to compose baloney-detection-kit with agentic runtimes that already use a
Plan -> Execute -> Verify architecture, such as
[Robert Eichenseer's AgenticAI.PlanExecuteValidate](https://github.com/RobertEichenseer/AgenticAI.PlanExecuteValidate).

This is an integration pattern, not an official adapter. Keep this repository a
playbook. Put orchestration code, framework bindings, automated evaluators, and
provider-specific details in the downstream system that uses the playbook.

---

## Why the pattern fits

BDK describes a conversation behavior: before validating a weak, inflated,
high-stakes, or novel-sounding claim, add epistemic friction. Plan -> Execute ->
Verify systems provide a natural runtime shape for that behavior:

1. **Plan:** decide whether the playbook should fire and which mode applies.
2. **Execute:** run the chosen epistemic checks with available tools, agents, or
   human review.
3. **Verify:** review whether the answer preserved epistemic integrity before it
   reaches the user.

AgenticAI.PlanExecuteValidate demonstrates this shape with a planner agent, an
executor agent, a verifier agent, and activity artifacts that preserve plan,
step results, final answer, and scores. BDK can be used as the behavioral policy
inside that shape without importing the sample's sports-domain code.

---

## Component mapping

| BDK concept | Plan -> Execute -> Verify component | Integration rule |
|-------------|--------------------------------------|------------------|
| Trigger conditions | Planner | Detect novelty, suppression framing, against-consensus claims, validation requests, high-stakes domains, and multi-turn pressure. |
| Light / full / stabilization mode | Planner | Select the lightest mode that preserves rigor. Do not force the full template on humble exploration. |
| Six-step protocol | Plan steps | Convert state of the art, novelty, falsifiability, evidence chain, pluralism, and humility into explicit steps. |
| Evidence-backed practice | Executor | Use search, retrieval, citations, internal knowledge bases, or domain sources when available. If tools are unavailable, say so. |
| Second opinion | Executor | Call two independent reviewer models only when warranted. Send the object to review, not the prior conversation. |
| High-stakes handling | Planner + Executor | Lower the threshold for full mode, require domain source expectations, and route material decisions to qualified humans. |
| Manual review rubric | Verifier | Verify process quality: no fabricated evidence, no flattering validation, no unsupported certainty, clear next step. |
| Review notes / transcript | Activity artifact | Preserve claim, mode, plan, tool results, reviewer outputs, uncertainties, and final answer for later audit. |

---

## Minimal integration flow

### 1. Intake: extract the object

Start by extracting the smallest reviewable object:

- the user's atomic claim;
- the domain and stakes;
- the user's requested action;
- any evidence already provided;
- whether the user is asking for validation, persuasion, or investigation.

Do not pass the whole conversation to downstream reviewers unless the conversation
itself is the object being reviewed. For ordinary claims, summarize the claim and
evidence neutrally.

### 2. Plan: create a BDK activity plan

The planner should output a plan that is specific enough to execute and narrow
enough to avoid unnecessary friction.

Example conceptual shape:

```json
{
  "claim": "A user claims X is a new discovery.",
  "mode": "full",
  "stakes": "scientific / low immediate harm",
  "steps": [
    "state_of_the_art_check",
    "novelty_assessment",
    "falsifiability_check",
    "evidence_chain_review",
    "alternative_explanations",
    "humility_and_next_step"
  ],
  "second_opinion": "not_required"
}
```

This is not a schema this repo promises to support. It is a readable sketch for
teams that already have their own activity object.

### 3. Execute: run epistemic checks

The executor runs only the steps the planner selected:

- **State of the art:** retrieve prior art, authoritative sources, or domain
  references. If no retrieval is available, the response must say so.
- **Novelty:** classify the claim as rediscovery, re-framing, or genuinely new.
- **Falsifiability:** identify what would disprove the claim and flag moving
  goalposts or "too subtle to measure" framing.
- **Evidence chain:** separate strong evidence, weak evidence, anecdotes, and
  intuition.
- **Pluralism:** produce at least two steelmanned alternative explanations when
  full mode is warranted.
- **Second opinion:** for high-stakes, uncertain, niche, or unusually inflated
  claims, ask two independent models to review the object from scratch.
- **High-stakes escalation:** when consequences are material, include qualified
  human expertise as the next step rather than treating the agent's answer as an
  action recommendation.

### 4. Verify: review the response before delivery

The verifier should not become an automated truth engine. It should check whether
the response followed the playbook:

- Did the trigger decision make sense?
- Did the answer check prior art before validating?
- Did it avoid fabricated sources and unsupported certainty?
- Did it preserve useful re-framings without flattering novelty?
- Did it handle high-stakes content with care?
- Did it preserve second-opinion disagreement instead of voting?
- Did it leave a concrete, honest next step?

If verification fails, revise the response or mark the uncertainty plainly. Do
not hide the failure behind a confidence score.

### 5. Return a user-facing answer

The final answer should still sound like BDK: kind, direct, specific, humble, and
useful. The user does not need to see the internal activity object unless the
product intentionally exposes audit traces.

---

## Activity artifact

A downstream Plan -> Execute -> Verify runtime can preserve an activity artifact
with fields like these:

| Field | Purpose |
|-------|---------|
| `claim` | The atomic claim or decision being reviewed. |
| `trigger_reason` | Why BDK fired, or why it stayed in light mode. |
| `mode` | `light`, `full`, or `stabilization`. |
| `steps` | Planned BDK checks and their outputs. |
| `sources` | Prior-art or evidence references used during execution. |
| `reviewers` | External model reviewers, if second opinion was used. |
| `disagreements` | Preserved disagreements across reviewers or sources. |
| `verifier_notes` | Rubric-based process review, not a truth verdict. |
| `final_answer` | The answer delivered to the user. |
| `next_step` | Source, expert, experiment, or narrowing action. |

This artifact is useful for incident review, team calibration, and later
measurement with tools such as
[robopsychology](https://github.com/jrcruciani/robopsychology).

---

## Guardrails

- **Do not turn agreement into proof.** Two models agreeing is a signal to
  investigate, not a truth criterion.
- **Do not contaminate second opinions.** Send the object to review, not the
  first model's reasoning or answer.
- **Do not replace domain expertise.** Medical, legal, financial, safety, and
  mental-health decisions need qualified humans when consequences are material.
- **Do not fabricate retrieval.** If the runtime lacks browsing, search, or a
  trusted corpus, say so.
- **Do not collapse verification into scoring.** A numeric score can help a
  product workflow, but BDK's verifier should remain rubric-based and auditable.
- **Do not copy external assets or code casually.** Link to
  AgenticAI.PlanExecuteValidate as a reference pattern unless its license and
  your project policy explicitly allow reuse.
- **Do not move the framework into this repo.** Keep provider-specific code,
  MCP wiring, notebooks, evaluators, and SDK adapters downstream.

---

## Where to integrate

Use this pattern when you already have an agent runtime with one or more of:

- a planner or task-decomposition stage;
- tool execution, retrieval, MCP, or internal knowledge bases;
- multiple reviewer models;
- a verifier, judge, policy gate, or human review queue;
- audit logs or activity artifacts.

If you only need personal use, copy [`ROOT_PROMPT.md`](ROOT_PROMPT.md). If your
assistant supports skills, use [`skill/SKILL.md`](skill/SKILL.md). Plan ->
Execute -> Verify is for systems that already need orchestration.

---

## Validation

Start with manual review:

- [`skill/checklist/review_rubric.md`](skill/checklist/review_rubric.md) checks
  whether the response applied BDK well.
- [`second-opinion-operational.md`](second-opinion-operational.md) covers common
  orchestration failures when asking reviewer models.

For measurement, keep BDK as the prompt-side intervention and use an external
instrument. The closed-loop protocol in
[`validation/closed-loop/`](validation/closed-loop/) shows how to compare a
control prompt against BDK using
[robopsychology](https://github.com/jrcruciani/robopsychology).

---

## Reference

- [AgenticAI.PlanExecuteValidate](https://github.com/RobertEichenseer/AgenticAI.PlanExecuteValidate)
  by Robert Eichenseer: an end-to-end sample of a Plan -> Execute -> Verify
  orchestrator with planner, executor, verifier, activity objects, classic
  functions, agents, and MCP tools.
