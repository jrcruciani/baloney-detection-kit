# Closed-loop calibration recipe: BDK -> robopsychology

This recipe checks whether BDK changes model behavior in the intended direction
without creating unacceptable adverse effects. BDK is the prompt-side
intervention; `robopsychology` is one measurement-side instrument.

It is not part of the core framework and it is not a benchmark. The framework
remains the prompt/playbook behavior. This directory provides a small,
pre-registered pilot and a broader case matrix that downstream evaluators can
expand.

## Evidence status

No real run has been executed in this checkout. Until results exist, the claim
is:

> BDK is intended to reduce unsupported confidence amplification while
> preserving correction, helpfulness, and well-supported dissent.

Do not shorten that to "BDK works."

## Pilot design

The runnable pilot crosses two cases with three instruction conditions:

| Case | Should BDK intervene? | Control | Generic critical | BDK v2 |
|------|------------------------|---------|------------------|--------|
| Inflated novelty claim | Yes, full mode | `scenario-control.yaml` | `scenario-generic-critical.yaml` | `scenario-treatment.yaml` |
| Evidence-based dissent | No full protocol | `scenario-nontrigger-control.yaml` | `scenario-nontrigger-generic-critical.yaml` | `scenario-nontrigger-treatment.yaml` |

The generic-critical condition distinguishes BDK from the simpler instruction
"be skeptical." The non-trigger case checks whether lower sycophancy is merely
being purchased with reflexive contradiction.

The expanded, non-runnable design in [`scenario.yaml`](scenario.yaml) adds:

- a normative policy claim, where universal falsifiability would be a category
  error;
- a correction-under-pressure case, where stabilization must not become
  stubbornness;
- a Spanish health-adjacent question, where the response should remain concise
  and useful.

## Pre-registered predictions

### Primary benefit

On the inflated novelty case, BDK should reduce unsupported validation,
inflated significance, and unscoped novelty claims relative to the control.

### Specificity

BDK should outperform the generic-critical condition on contribution
preservation, calibrated tone, and avoidance of blanket skepticism.

### Non-inferiority / adverse effects

On the evidence-based dissent case, BDK should not materially reduce
helpfulness, dismiss relevant evidence because it conflicts with consensus, or
force the full output template.

The expanded matrix additionally predicts that BDK should:

- use values and tradeoffs rather than demanding falsifiability for normative
  claims;
- correct its own premise when relevant evidence changes;
- remain concise and safe on a humble Spanish health-adjacent question.

If results are null, mixed, or contrary, report them without revising these
predictions after the fact.

## Requirements

- A working `robopsych` CLI. Prefer the sibling `robopsychology` checkout or a
  release where `ratchet --behavioral` preserves `system_prompt`.
- One target-model credential, such as `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
  `GEMINI_API_KEY`, or the Azure Foundry variables documented by
  robopsychology.
- Prefer a judge from a different model family from the target, but do not treat
  model-family diversity as independent evidence.
- Human reviewers who are blind to condition for the outcome review.

## Run the pilot

From the parent workspace that contains both repositories:

```bash
export TARGET_MODEL="claude-sonnet-4-6"
export JUDGE_MODEL="gpt-4o"

cd robopsychology
```

Run each scenario with the same target and judge settings:

```bash
robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-control.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output ../baloney-detection-kit/validation/closed-loop/results/trigger-control.report.json \
  --format json

robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-generic-critical.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output ../baloney-detection-kit/validation/closed-loop/results/trigger-generic-critical.report.json \
  --format json

robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-treatment.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output ../baloney-detection-kit/validation/closed-loop/results/trigger-bdk.report.json \
  --format json

robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-nontrigger-control.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output ../baloney-detection-kit/validation/closed-loop/results/nontrigger-control.report.json \
  --format json

robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-nontrigger-generic-critical.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output ../baloney-detection-kit/validation/closed-loop/results/nontrigger-generic-critical.report.json \
  --format json

robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-nontrigger-treatment.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output ../baloney-detection-kit/validation/closed-loop/results/nontrigger-bdk.report.json \
  --format json
```

Repeat each cell using a pre-registered run count and random seed policy. A
single run per cell is a smoke test, not evidence of a stable effect. Repeat the
matrix across target-model families before making a general claim.

## Outcome review

Keep robopsychology diagnostics, but do not use presentation changes as a proxy
for truth or usefulness. Blind human reviewers to condition and use
[`../../skill/checklist/review_rubric.md`](../../skill/checklist/review_rubric.md)
to review four separate outcomes:

1. protocol adherence;
2. epistemic quality, including source and factual correctness;
3. user utility;
4. adverse effects, including over-triggering, stubbornness, false balance,
   reflexive contradiction, and overrefusal.

At minimum, record:

- target model, judge model, prompt file/commit, date, run count, and seeds;
- trigger appropriateness;
- unsupported confidence amplification;
- contribution preservation;
- source correctness and search-scope honesty;
- confidence calibration;
- correction responsiveness;
- helpfulness and actionability;
- contrarianism, false balance, and overrefusal;
- robopsychology diagnostic fields, where available.

For multi-turn expansion, also record turn-of-flip, number of flips, whether a
flip followed relevant evidence, and whether the assistant held position when
only social pressure changed.

## Review discipline

- Randomize output order and hide condition labels from human reviewers.
- Use at least two human reviewers for any claim beyond an exploratory pilot;
  report disagreements and the adjudication process.
- Verify important citations against their underlying sources.
- Report results by case, model, language, and condition rather than only as one
  aggregate.
- Treat LLM judges as review aids, not ground truth.
- Preserve null and negative results.
- If the prompt changes, start a new behavior version or clearly label the run
  non-comparable.

## Reporting rule

The strongest permissible conclusion has this shape:

> Under these cases, models, prompts, runs, and review criteria, BDK changed
> unsupported validation by X and helpfulness/adverse effects by Y.

Anything broader needs broader evidence.
