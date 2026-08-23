# Deployment contexts

BDK can be adopted one layer at a time. Prevention, diagnosis, and validation
share one framework but solve different operational questions.

| Need | BDK surface | Typical timing |
|---|---|---|
| Improve conversational defaults | Intervention prompt or skill | Design and inference time |
| Explain one suspicious output | Prompt card, template, or CLI diagnosis | Development and incident response |
| Test framing sensitivity | `bdk crosscheck` | Pre-deployment and debugging |
| Check multi-turn continuity | `bdk ratchet` and coherence analysis | Evaluation and incident response |
| Compare an intervention with control | Closed-loop scenarios | Calibration and regression review |

## Personal use

Use `ROOT_PROMPT.md` or `bdk apply compact` in custom instructions. Keep the
trigger conservative so ordinary exploration does not receive a full skeptical
template.

## Agent instructions

Install [`skill/`](skill/) in a compatible runtime or use
[`prompts/intervention/prompt-agent.md`](prompts/intervention/prompt-agent.md).
The prompt is advisory: it shapes responses but cannot enforce tool or data
access policy.

## Team review

Collect both trigger and non-trigger conversations. Review protocol adherence,
epistemic quality, usefulness, and adverse effects separately. Use diagnostic
cards to investigate representative failures before changing the system prompt.

## High-stakes domains

Lower the threshold for structured review when error is materially harmful or
hard to reverse. Add domain-specific evidence requirements and qualified human
review. BDK is not medical, legal, financial, safety, or compliance software.

## Production agents

A practical lifecycle is:

1. Define the intended behavior and encode the preventive prompt.
2. Test observable behavior with a spec-driven evaluator such as
   [ASSERT](https://github.com/responsibleai/ASSERT).
3. Diagnose representative failures with `bdk run`, `bdk crosscheck`, or
   `bdk ratchet`.
4. Fix the responsible layer: model, runtime/host, or conversation.
5. Re-run the evaluator and closed-loop cases.
6. Govern actions independently with a runtime control such as the
   [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit).

BDK governs no actions. Prompt instructions remain advisory, automated judges
remain fallible, and human review remains necessary for material decisions.

## Plan -> Execute -> Verify

In an orchestrated agent:

- **Plan:** determine whether epistemic friction is warranted and define the
  evidence/update criteria.
- **Execute:** perform the claim, prior-art, evidence, and alternative checks.
- **Verify:** run the rubric, diagnostic probes, or external evaluators before
  delivery.

See [`agentic-plan-execute-verify.md`](agentic-plan-execute-verify.md) for the
detailed mapping.
