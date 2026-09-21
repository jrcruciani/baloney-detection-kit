# Closed-loop calibration recipe

This recipe checks whether BDK changes model behavior in the intended direction
without creating unacceptable adverse effects. The intervention prompts change
the target behavior; BDK diagnostics measure framing sensitivity, coherence,
and other observable effects.

This directory provides a small, pre-registered pilot and a broader case matrix
that downstream evaluators can expand. See the README's
[Scope and boundaries](../../README.md#scope-and-boundaries) for the
project-wide scope.

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

- A working `bdk` CLI from this repository. Use a release where
  `ratchet --behavioral` preserves `system_prompt`.
- One target-model credential, such as `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
  `GEMINI_API_KEY`, or the Azure Foundry variables documented by
  BDK.
- Require at least **two distinct judge model families** for claims about
  intervention effects, preferably also different from the target family.
  Report both model IDs and family names: hosting two models on Azure, or using
  two deployments of the same family, does not establish family diversity.
  Model-family diversity is not statistical independence.
- Report pairwise judge-judge agreement on shared items, and blinded
  judge-human calibration where human ratings are available. Mark absent
  human/paired ratings unavailable, not agreement or accuracy.
- Human reviewers who are blind to condition for the outcome review.

`robopsych` is a legacy alias for `bdk` during the BDK 3.x compatibility window;
use `bdk` for new runs and integrations.

## Run the pilot

From the repository root:

```bash
export TARGET_MODEL="claude-sonnet-4-6"
export JUDGE_MODEL="gpt-4o"
```

Run each scenario with the same target and judge settings:

```bash
bdk ratchet \
  --scenario validation/closed-loop/scenario-control.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output validation/closed-loop/results/trigger-control.report.json \
  --format json

bdk ratchet \
  --scenario validation/closed-loop/scenario-generic-critical.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output validation/closed-loop/results/trigger-generic-critical.report.json \
  --format json

bdk ratchet \
  --scenario validation/closed-loop/scenario-treatment.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output validation/closed-loop/results/trigger-bdk.report.json \
  --format json

bdk ratchet \
  --scenario validation/closed-loop/scenario-nontrigger-control.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output validation/closed-loop/results/nontrigger-control.report.json \
  --format json

bdk ratchet \
  --scenario validation/closed-loop/scenario-nontrigger-generic-critical.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output validation/closed-loop/results/nontrigger-generic-critical.report.json \
  --format json

bdk ratchet \
  --scenario validation/closed-loop/scenario-nontrigger-treatment.yaml \
  --model "$TARGET_MODEL" --behavioral --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output validation/closed-loop/results/nontrigger-bdk.report.json \
  --format json
```

Repeat each cell using a pre-registered run count and random seed policy. A
single run per cell is a smoke test, not evidence of a stable effect. Repeat the
matrix across target-model families before making a general claim.

### Paired judging without target reruns

The commands above capture target outputs once per cell/run. Keep those JSON
reports unchanged in private storage. Re-rate the **same report** with a second
family (or re-rate with both to use the strict saved-output evaluator):

```bash
export CAPTURE="validation/closed-loop/results/trigger-bdk.report.json"
bdk rejudge "$CAPTURE" --judge gpt-4o --judge-family GPT \
  --output validation/closed-loop/results/trigger-bdk.gpt-judgment.json
bdk rejudge "$CAPTURE" --judge claude-sonnet-4-6 --judge-family Claude \
  --output validation/closed-loop/results/trigger-bdk.claude-judgment.json
```

Repeat the judge-only commands for every captured condition/run, not the target
sampling commands. `rejudge` makes only evaluator calls in clean contexts,
preserves the A/B task/response pair and diagnostic steps, records a source
SHA-256 and actual judge ID plus declared family, and refuses source overwrite.
Both judge files must reference the same capture hash. Repeating `ratchet`
with a different judge generates new target outputs and is **not** paired
judge agreement. Existing `--behavioral` A/B pairs are machine-inverted
approximations; retain that provenance.

For agreement, predefine the categorical dimension (for example
`substance_changed`, or a human protocol-adherence category), blind and randomize
the same target items for humans, and assign stable item IDs including
case/condition/run/dimension. Export the two judges' actual labels and separately
collected human ratings into the documented
[ratings schema](../diagnosis/calibration/README.md#paired-rating-agreement).
Do not convert continuous shift scores into labels after seeing the outcomes.

```bash
python validation/diagnosis/agreement.py --ratings /private/path/ratings.json
```

Report shared sample size, unmatched/missing ratings, raw agreement, nominal
Cohen kappa, and disagreements/adjudication for each judge-judge and judge-human
pair. Kappa is undefined with no shared items or chance agreement of one; report
N/A, not perfect agreement. This is agreement, not accuracy or independence.
Without real paired ratings the offline default reads the existing synthetic
claim-count fixtures and explicitly reports N/A; it cannot supply human
calibration. The historical diagnostic case studies do not supply treatment
outcomes for this pilot.

## Outcome review

Keep BDK diagnostics, but do not use presentation changes as a proxy
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
- BDK diagnostic fields, where available.

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
- Preserve judge failures and unknown stance labels as missing/incomplete
  measurements, never stable verdicts or negative interventions.
- Preserve null and negative results.
- If the prompt changes, start a new behavior version or clearly label the run
  non-comparable.

## Reporting rule

The strongest permissible conclusion has this shape:

> Under these cases, models, prompts, runs, and review criteria, BDK changed
> unsupported validation by X and helpfulness/adverse effects by Y.

Anything broader needs broader evidence.

The current [results inventory](RESULTS.md) has no measurements. Do not describe
an unexecuted pilot as a null or mixed empirical outcome. Track execution in
[#11](https://github.com/jrcruciani/baloney-detection-kit/issues/11).
