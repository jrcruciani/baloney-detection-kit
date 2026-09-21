# Deployment contexts

BDK can be adopted one layer at a time. Prevention, diagnosis, and validation
share one framework but solve different operational questions.

See the README's [Scope and boundaries](../README.md#scope-and-boundaries) for
the project-wide scope.

Robopsychology now ships in this repository as BDK's diagnostic layer, available
through diagnostic prompts, templates, and `bdk` commands such as `bdk run`,
`bdk crosscheck`, and `bdk ratchet`.

| Need                                 | BDK surface                             | Typical timing                    |
| ------------------------------------ | --------------------------------------- | --------------------------------- |
| Improve conversational defaults      | Intervention prompt or skill            | Design and inference time         |
| Explain one suspicious output        | Prompt card, template, or CLI diagnosis | Development and incident response |
| Test framing sensitivity             | `bdk crosscheck`                        | Pre-deployment and debugging      |
| Check multi-turn continuity          | `bdk ratchet` and coherence analysis    | Evaluation and incident response  |
| Compare an intervention with control | Closed-loop scenarios                   | Calibration and regression review |

## Personal use

Use `ROOT_PROMPT.md` or `bdk apply compact` in custom instructions. Keep the
trigger conservative: ordinary no-claim questions and humble exploration need
no intervention, not merely a shorter skeptical template.

## Agent instructions

Copy the complete [`skills/baloney-detection-kit/`](../skills/baloney-detection-kit/)
distribution using the [runtime integration guide](integration.md), or use
[`prompts/intervention/prompt-agent.md`](../prompts/intervention/prompt-agent.md).
The legacy [`skill/`](../skill/) remains the editable compatibility source.
The prompt is advisory: it shapes responses but cannot enforce tool or data
access policy.

## Team review

Collect both trigger and non-trigger conversations. Review protocol adherence,
epistemic quality, usefulness, and adverse effects separately. Use diagnostic
cards to investigate representative failures before changing the system prompt.

## High-stakes domains

After an actual claim signal, lower the threshold for structured review when
error is materially harmful or hard to reverse. A high-stakes domain alone
never forces Full. Retain domain-specific evidence requirements and qualified
human review even without Full. BDK is not medical, legal, financial, safety, or
compliance software.

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

## Scenario firing metrics

Use the [shared scenario harness](../framework/diagnosis/scenarios.md) before
deployment. It includes explicit negative and positive cases under the packaged
BDK intervention. `bdk crosscheck --scenarios <directory> --model <model> --format json` reports a **protocol-header proxy**, not a complete detector of
Light/prose intervention. Directness and hedging budgets require human review.

For explicitly labeled, successfully answered scenarios: TP is a positive case
that fires, FN a positive that stays quiet, FP a negative that fires, and TN a
negative that stays quiet. Count a case once even if several turns fire.

| Metric                      | Definition     | Meaning                                          |
| --------------------------- | -------------- | ------------------------------------------------ |
| Positive fire rate / recall | TP / (TP + FN) | Fraction of positive cases detected by the proxy |
| Negative fire rate / FPR    | FP / (FP + TN) | Fraction of negative cases that fire             |
| Precision                   | TP / (TP + FP) | Fraction of fires belonging to positive cases    |
| Specificity                 | TN / (TN + FP) | Fraction of negative cases that stay quiet       |

“Stayed quiet” on negatives measures **specificity**, not precision. Undefined
denominators are `null`/N/A, not zero or one. A negative-only directory reports
FPR and specificity but cannot estimate recall. Unlabeled legacy scenarios and
failed target calls are explicitly excluded, not silently treated as negatives.
Report sample sizes, failure coverage, and per-scenario breakdowns; do not turn
the proxy or a synthetic fixture into a claim of intervention efficacy.

## Plan -> Execute -> Verify

In an orchestrated agent:

- **Plan:** determine whether epistemic friction is warranted and define the
  evidence/update criteria.
- **Execute:** perform the claim, prior-art, evidence, and alternative checks.
- **Verify:** run the rubric, diagnostic probes, or external evaluators before
  delivery.

See [`agentic-plan-execute-verify.md`](agentic-plan-execute-verify.md) for the
detailed mapping.
