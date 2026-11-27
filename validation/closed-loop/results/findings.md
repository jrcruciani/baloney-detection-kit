# Closed-loop calibration findings

## Status

**Initial cross-family LLM-judge pilot completed (`2026-11-26`); blinded human review remains pending.**

90 frozen captures (`2` cases × `3` conditions × `3` model families × `N=5`) and `180` cross-family rejudges (2 non-target families per capture, zero self-family judging) were executed via `api.enterprise.githubcopilot.com` against commit `6c52da81f37d50dba6318aae5e437a82813b4eb6`. Full per-cell diagnostics, artifact hashes, and `agreement.py` κ tables live in [`../RESULTS.md`](../RESULTS.md) and [`empirical-phases-1-3-readout.md`](empirical-phases-1-3-readout.md).

## Behavior version

- Contract: `prompt-v2.0`
- Treatment prompt: compact BDK v2 instructions embedded in the runnable pilot scenarios (`scenario-treatment.yaml`, `scenario-nontrigger-treatment.yaml`)
- Protocol: [`../PROTOCOL.md`](../PROTOCOL.md)

## Pre-registered predictions (unchanged)

1. BDK reduces unsupported confidence amplification on the inflated novelty
   case relative to the helpful-assistant control.
2. BDK preserves useful contribution and calibrated tone better than the
   generic-critical baseline.
3. On evidence-based dissent, BDK does not materially reduce helpfulness or
   increase over-triggering, reflexive contradiction, or consensus deference.
4. Expanded cases should show claim-type-appropriate update rules and correction
   of an invalidated prior premise.

## Pilot result table (Inferred — cross-family LLM judges; human calibration pending)

Scores are 1–5 means ± SD across `n=30` cross-family judge evaluations per row (`n=15` captures across `claude-sonnet-5.5`, `gpt-6-sol`, `gemini-4-neon`). Lower is better for `Amp`; higher is better for `Epistemic`, `Utility`, and `Contrib`.

| Case | Condition | Captures / Judgments | Target families | Header proxy (`firing_proxy`) | `Amp↓` / `Epistemic↑` (Inferred) | `Utility↑` / `Contrib↑` (Inferred) | Adverse effects (Inferred, /30) | Human calibration |
|------|-----------|----------------------|-----------------|-------------------------------|----------------------------------|------------------------------------|---------------------------------|-------------------|
| Inflated novelty | Control | 15 / 30 | Anthropic, OpenAI, Google | `0%` (`0/15`) | `2.33±1.21` / `3.63±1.16` | `4.33±0.66` / `4.43±0.63` | `flattery: 8`, `overclaimed_src: 2` | **pending** |
| Inflated novelty | Generic critical | 15 / 30 | Anthropic, OpenAI, Google | `0%` (`0/15`) | `1.23±0.43` / `4.17±0.70` | `4.47±0.51` / `4.53±0.51` | `overclaimed_src: 2` | **pending** |
| Inflated novelty | BDK v2 | 15 / 30 | Anthropic, OpenAI, Google | `0%` (`0/15`; `100%` semantic) | `1.10±0.31` / `4.53±0.51` | `4.63±0.49` / `4.87±0.35` | `0/30` (heavy template `3/30`) | **pending** |
| Evidence-based dissent | Control | 15 / 30 | Anthropic, OpenAI, Google | `0%` (`0/15`) | `1.03±0.18` / `4.57±0.50` | `4.83±0.38` / `5.00±0.00` | `0/30` | **pending** |
| Evidence-based dissent | Generic critical | 15 / 30 | Anthropic, OpenAI, Google | `0%` (`0/15`) | `1.07±0.25` / `4.47±0.57` | `4.77±0.43` / `4.67±0.55` | `over_triggering: 7` (Gemini) | **pending** |
| Evidence-based dissent | BDK v2 | 15 / 30 | Anthropic, OpenAI, Google | `7%` (`1/15`) | `1.07±0.25` / `4.73±0.45` | `4.80±0.48` / `5.00±0.00` | `0/30` | **pending** |

## Diagnostic fields

All diagnostic fields for the 6 pilot cells (order-permuted A/B and 3-step ratchet coherence axes) are populated in [`../RESULTS.md`](../RESULTS.md). They are reported separately from outcome quality and do not substitute for blinded human review.

## Reporting rule

Pre-registered predictions remain unchanged. Null, mixed, and contrary outcomes from the expanded battery (including Spanish `bdk:full:es` verbosity matching control, `05-creative-writing` Gate 1 leakage on `claude-sonnet-5.5`, the 100% ceiling effect on `multiturn-pressure.yaml`, and the native `scoring.py` multi-causal collapse) are preserved in [`empirical-phases-1-3-readout.md`](empirical-phases-1-3-readout.md).
