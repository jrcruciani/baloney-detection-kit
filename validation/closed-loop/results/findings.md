# Closed-loop calibration findings

## Status

No real calibration run has been executed in this checkout.

Reason: no target-model credential environment variables were present, and no
local Ollama endpoint was available. The pre-registered pilot, six runnable
scenario files, and expanded case matrix are ready; the empirical result remains
pending.

## Behavior version

- Contract: `prompt-v2.0`
- Treatment prompt: compact BDK v2 instructions embedded in the runnable
  scenarios
- Protocol: [`../PROTOCOL.md`](../PROTOCOL.md)

## Pre-registered predictions

1. BDK reduces unsupported confidence amplification on the inflated novelty
   case relative to the helpful-assistant control.
2. BDK preserves useful contribution and calibrated tone better than the
   generic-critical baseline.
3. On evidence-based dissent, BDK does not materially reduce helpfulness or
   increase over-triggering, reflexive contradiction, or consensus deference.
4. Expanded cases should show claim-type-appropriate update rules and correction
   of an invalidated prior premise.

## Pilot result table

| Case | Condition | Runs | Target | Protocol adherence | Epistemic quality | User utility | Adverse effects |
|------|-----------|------|--------|--------------------|-------------------|--------------|-----------------|
| Inflated novelty | Control | pending | pending | pending | pending | pending | pending |
| Inflated novelty | Generic critical | pending | pending | pending | pending | pending | pending |
| Inflated novelty | BDK v2 | pending | pending | pending | pending | pending | pending |
| Evidence-based dissent | Control | pending | pending | pending | pending | pending | pending |
| Evidence-based dissent | Generic critical | pending | pending | pending | pending | pending | pending |
| Evidence-based dissent | BDK v2 | pending | pending | pending | pending | pending | pending |

## Diagnostic fields

Record robopsychology fields where available, but do not treat them as outcome
quality by themselves:

| Field | Status |
|-------|--------|
| `substance_changed` | pending |
| `presentation_shift_score` | pending |
| `severity_labels_shifted` | pending |
| `urgency_language_shifted` | pending |
| `reference_density` | pending |
| `contradiction_rate` | pending |
| `fresh_claim_rate` | pending |
| `high_severity_contradiction_count` | pending |

## Reporting rule

When credentials are available, run the pilot across pre-registered models,
repetitions, and review criteria. Preserve null, mixed, and contrary outcomes.
Do not rewrite the predictions or collapse protocol adherence, epistemic
quality, user utility, and adverse effects into one score.
