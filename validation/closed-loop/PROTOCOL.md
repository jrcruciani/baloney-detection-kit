# Closed-loop protocol: BDK -> robopsychology

This protocol tests whether the BDK root prompt changes model behavior on a
weak, inflated novelty claim. BDK is the prompt-side intervention;
robopsychology is the measurement-side instrument.

## Pre-registered prediction

Compared with the control condition, the treatment condition should show less
sycophantic validation and more epistemic pushback: more prior-art checking,
more cautious novelty classification, and less flattering escalation of the
"as important as writing" framing.

If the result is null, mixed, or contrary, report it as such. Do not revise the
prediction after seeing the model outputs.

## Requirements

- A working `robopsych` CLI. Prefer the sibling `robopsychology` checkout, or
  any release where `ratchet --behavioral` preserves `system_prompt` from the
  scenario file during the behavioral cross-check.
- One target model credential, such as `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
  `GEMINI_API_KEY`, or the Azure Foundry variables documented by
  robopsychology.
- Prefer a different judge model from the target model when possible.

## Run

From the parent workspace that contains both repos:

```bash
export TARGET_MODEL="claude-sonnet-4-6"
export JUDGE_MODEL="gpt-4o"

cd robopsychology

robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-control.yaml \
  --model "$TARGET_MODEL" \
  --behavioral \
  --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --coherence-checkpoint ../baloney-detection-kit/validation/closed-loop/results/control.coherence.json \
  --output ../baloney-detection-kit/validation/closed-loop/results/control.report.json \
  --format json

robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-treatment.yaml \
  --model "$TARGET_MODEL" \
  --behavioral \
  --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --coherence-checkpoint ../baloney-detection-kit/validation/closed-loop/results/treatment.coherence.json \
  --output ../baloney-detection-kit/validation/closed-loop/results/treatment.report.json \
  --format json
```

Optionally repeat with `--format markdown` to publish human-readable reports:

```bash
robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-control.yaml \
  --model "$TARGET_MODEL" \
  --behavioral \
  --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output ../baloney-detection-kit/validation/closed-loop/results/control.report.md

robopsych ratchet \
  --scenario ../baloney-detection-kit/validation/closed-loop/scenario-treatment.yaml \
  --model "$TARGET_MODEL" \
  --behavioral \
  --judge "$JUDGE_MODEL" \
  --coherence-judge "$JUDGE_MODEL" \
  --output ../baloney-detection-kit/validation/closed-loop/results/treatment.report.md
```

## Readout

Report at least:

- `N`: number of target-model runs per condition.
- Target model and judge model.
- Whether `substance_changed` differs across control and treatment.
- `presentation_shift_score` for each condition.
- Any severity, urgency, hedging, or omission shifts.
- If available, LLM coherence axes: `reference_density`,
  `contradiction_rate`, `fresh_claim_rate`, and
  `high_severity_contradiction_count`.

The minimal claim is not "BDK works"; it is narrower: under this probe, this
model with this prompt either did or did not show a measurable reduction in
sycophantic validation.
