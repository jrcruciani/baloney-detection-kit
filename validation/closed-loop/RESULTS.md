# Closed-loop evidence status

**Status: initial cross-family LLM-judge pilot executed (`N=5 × 3` target families per cell, `90` frozen captures, `180` cross-family rejudges); blinded human calibration remains pending.**

All automated metrics below are explicitly **Inferred (cross-family LLM judges)**, not human ground truth or an established product-efficacy claim. Raw transcripts are retained privately (`chmod 0600`) outside this repository per [`CONTRIBUTING.md`](../../CONTRIBUTING.md); paired categorical ratings for offline verification with [`validation/diagnosis/agreement.py`](../diagnosis/agreement.py) are stored in [`results/agreement/`](results/agreement/). The full companion empirical readout covering Phases 1–3 (trigger battery, Spanish `bdk:full:es`, multi-turn pressure ceiling, and causal diagnostic benchmark) is in [`results/empirical-phases-1-3-readout.md`](results/empirical-phases-1-3-readout.md).

- **Repo commit:** `6c52da81f37d50dba6318aae5e437a82813b4eb6` (`prompt-v2.0`, BDK `3.0.0`)
- **Date:** `2026-11-26` (UTC)
- **Language:** English (`en`) for the 6 pre-registered pilot cells (Spanish `bdk:full:es` evaluated separately in the companion readout)
- **Gateway host (shared):** `api.enterprise.githubcopilot.com` (documented common routing host; target and judge families are strictly distinct)
- **Target models (3 families):** `claude-sonnet-5.5` (Anthropic), `gpt-6-sol` (OpenAI), `gemini-4-neon` (Google)
- **Cross-family judge rule:** zero self-family judging; each frozen capture is scored independently by the **two non-target model families** (`temperature=0` requested, degraded to default on `gpt-6-sol` `/responses` and logged; JSON object mode; permuted `(AB + BA)` A/B passes; `pair_provenance="user-authored"` controlled inversions)
- **Protocol & tracking:** [`PROTOCOL.md`](PROTOCOL.md), [`results/findings.md`](results/findings.md), [#10](https://github.com/jrcruciani/baloney-detection-kit/issues/10)

## Run inventory

Every cell aggregates `N = 5` independent runs per target family (`15` frozen captures and `30` cross-family judge evaluations per row). Cell hashes are the SHA-256 prefix over the sorted `source_sha256` digests of the 15 privately retained captures.

| Case                   | Condition        | Target models (3 families)                           | Judge families (2 non-target per capture)   | N runs (captures / judgments) | Artifact provenance (cell SHA-256) |
| ---------------------- | ---------------- | ---------------------------------------------------- | ------------------------------------------- | ----------------------------- | ---------------------------------- |
| Inflated novelty       | control          | `claude-sonnet-5.5`, `gpt-6-sol`, `gemini-4-neon`    | Anthropic / OpenAI / Google (cross-family)  | `N=5 × 3` (15 / 30)           | `a57ab62348a4` (`phase1b_pilot`)   |
| Inflated novelty       | generic-critical | `claude-sonnet-5.5`, `gpt-6-sol`, `gemini-4-neon`    | Anthropic / OpenAI / Google (cross-family)  | `N=5 × 3` (15 / 30)           | `1de9cf630377` (`phase1b_pilot`)   |
| Inflated novelty       | treatment        | `claude-sonnet-5.5`, `gpt-6-sol`, `gemini-4-neon`    | Anthropic / OpenAI / Google (cross-family)  | `N=5 × 3` (15 / 30)           | `c69c6db31ca7` (`phase1b_pilot`)   |
| Evidence-based dissent | control          | `claude-sonnet-5.5`, `gpt-6-sol`, `gemini-4-neon`    | Anthropic / OpenAI / Google (cross-family)  | `N=5 × 3` (15 / 30)           | `0c8cae3121d0` (`phase1b_pilot`)   |
| Evidence-based dissent | generic-critical | `claude-sonnet-5.5`, `gpt-6-sol`, `gemini-4-neon`    | Anthropic / OpenAI / Google (cross-family)  | `N=5 × 3` (15 / 30)           | `379e477eedb9` (`phase1b_pilot`)   |
| Evidence-based dissent | treatment        | `claude-sonnet-5.5`, `gpt-6-sol`, `gemini-4-neon`    | Anthropic / OpenAI / Google (cross-family)  | `N=5 × 3` (15 / 30)           | `839db964e1a0` (`phase1b_pilot`)   |

## Diagnostic fields (not outcome quality)

All A/B fields compare **analyst-authored controlled framing pairs within a condition** (`pair_provenance="user-authored"`) evaluated in both `(A,B)` and `(B,A)` orders. Fractions for boolean fields show `consensus_true / order_consistent_pairs` (out of 30 total judgments); `omissions_added` reports mean ± SD count of the AB ∪ BA union.

| Case / condition           | `substance_changed` (order-cons.) | `presentation_shift_score` | `severity_labels_shifted` | `urgency_language_shifted` | `hedging_delta` (A→B) | `omissions_added` (mean ± SD) |
| -------------------------- | --------------------------------- | -------------------------- | ------------------------- | -------------------------- | --------------------- | ----------------------------- |
| Novelty / control          | `14/26` (87% order-cons.)         | `0.53 ± 0.10`              | `0/30`                    | `0/30`                     | `+0.04 ± 0.11`        | `7.80 ± 2.22`                 |
| Novelty / generic-critical | `0/26` (87% order-cons.)          | `0.38 ± 0.08`              | `0/30`                    | `2/30`                     | `+0.02 ± 0.05`        | `7.63 ± 2.06`                 |
| Novelty / treatment        | `1/29` (97% order-cons.)          | `0.38 ± 0.04`              | `0/30`                    | `0/30`                     | `-0.04 ± 0.08`        | `7.43 ± 2.37`                 |
| Dissent / control          | `4/26` (87% order-cons.)          | `0.35 ± 0.10`              | `0/30`                    | `0/30`                     | `-0.10 ± 0.07`        | `7.30 ± 2.07`                 |
| Dissent / generic-critical | `7/28` (93% order-cons.)          | `0.45 ± 0.14`              | `0/30`                    | `1/26`                     | `-0.26 ± 0.10`        | `7.60 ± 2.25`                 |
| Dissent / treatment        | `2/27` (90% order-cons.)          | `0.36 ± 0.08`              | `0/30`                    | `0/30`                     | `-0.09 ± 0.07`        | `7.10 ± 1.83`                 |

The A/B fields compare framing pairs **within a condition**; they are not a treatment-minus-control effect estimate. Order permutation caught measurable position bias (`3%–13%` of judgments flipped `substance_changed` when `(A,B)` was reversed to `(B,A)`).

| Case / condition           | Coherence axes (`ref` / `contra` / `fresh` / `hedge_f` / `high_sev`) | Adverse effects observed (Inferred, out of 30) | Blind LLM-judge axes (`Amp↓` / `Epi↑` / `Util↑` / `Contrib↑`, 1–5) | Paired judge agreement / blinded human calibration |
| -------------------------- | -------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------- |
| Novelty / control          | `0.89±0.08` / `0.08±0.06` / `0.12±0.09` / `0.00` / `1`               | `flattery_or_sycophancy: 8`, `overclaimed_source: 2` | `2.33±1.21` / `3.63±1.16` / `4.33±0.66` / `4.43±0.63`         | Judge–judge pooled below; **Human: [PENDING]**     |
| Novelty / generic-critical | `0.88±0.06` / `0.08±0.07` / `0.13±0.06` / `0.00` / `1`               | `overclaimed_source: 2`                        | `1.23±0.43` / `4.17±0.70` / `4.47±0.51` / `4.53±0.51`              | Judge–judge pooled below; **Human: [PENDING]**     |
| Novelty / treatment        | `0.87±0.11` / `0.06±0.06` / `0.13±0.11` / `0.00` / `4`               | none (`0/30`); heavy template `3/30`           | `1.10±0.31` / `4.53±0.51` / `4.63±0.49` / `4.87±0.35`              | Judge–judge pooled below; **Human: [PENDING]**     |
| Dissent / control          | `0.91±0.07` / `0.05±0.06` / `0.10±0.08` / `0.00` / `0`               | none (`0/30`)                                  | `1.03±0.18` / `4.57±0.50` / `4.83±0.38` / `5.00±0.00`              | Judge–judge pooled below; **Human: [PENDING]**     |
| Dissent / generic-critical | `0.89±0.09` / `0.09±0.08` / `0.12±0.09` / `0.00` / `1`               | `over_triggering: 7` (all on `gemini-4-neon`)  | `1.07±0.25` / `4.47±0.57` / `4.77±0.43` / `4.67±0.55`              | Judge–judge pooled below; **Human: [PENDING]**     |
| Dissent / treatment        | `0.91±0.06` / `0.08±0.06` / `0.10±0.06` / `0.00` / `1`               | none (`0/30`); `firing_proxy` `1/15`           | `1.07±0.25` / `4.73±0.45` / `4.80±0.48` / `5.00±0.00`              | Judge–judge pooled below; **Human: [PENDING]**     |

### Paired judge–judge agreement (`validation/diagnosis/agreement.py`)

Verified offline against [`results/agreement/ratings_overall_category.json`](results/agreement/ratings_overall_category.json) and [`results/agreement/ratings_ab_substance_changed.json`](results/agreement/ratings_ab_substance_changed.json):

- `overall_category`: `gpt-6-sol` vs `claude-sonnet-5.5` (on Gemini targets, `n=30`): raw `80.0%`, **`κ = 0.508`**; `gemini-4-neon` vs `gpt-6-sol` (`n=30`): raw `90.0%`, `κ = 0.000` (single-class prevalence); `gemini-4-neon` vs `claude-sonnet-5.5` (`n=30`): raw `100.0%`, `κ = N/A` (chance agreement `1.0`).
- `ab_substance_changed` (order-consistent subset): `gpt-6-sol` vs `claude-sonnet-5.5` (`n=22`): raw `63.6%`, `κ = 0.313`; `gemini-4-neon` vs `claude-sonnet-5.5` (`n=27`): raw `96.3%`, `κ = 0.000`; `gemini-4-neon` vs `gpt-6-sol` (`n=23`): raw `60.9%`, `κ = 0.000`.
- `judge–human` and `human–human` agreement: **unavailable / pending blinded human review**.

## Scoped readout

Across 90 frozen captures and 180 cross-family LLM-judge evaluations (`1,353` API calls, `0` failed calls, `4.58M` tokens):

1. **Strongest observed effect is model-dependent:** on `inflated_novelty`, `claude-sonnet-5.5` and `gpt-6-sol` already showed moderate resistance in `control` (`Amp = 1.80` and `1.50`), whereas `gemini-4-neon` exhibited substantial sycophancy in `control` (`Amp = 3.70 ± 0.68`, `flattery_or_sycophancy: 8/10`) that BDK reduced to `Amp = 1.10 ± 0.32` (`0/10` adverse effects) while raising epistemic quality (`2.40 → 4.30`) and contribution preservation (`3.80 → 4.90`).
2. **Specificity advantage over `generic-critical`:** on `evidence_based_dissent`, `generic-critical` induced `over_triggering: 7/10` and lower contribution preservation (`4.00 ± 0.47`) on `gemini-4-neon`, while BDK maintained `0/10` adverse effects and `5.00 ± 0.00` utility and contribution preservation.
3. **Measurement limit exposed on `firing_proxy`:** on `inflated_novelty / treatment`, the regex header proxy fired `0/15` (`0%`) while blind semantic judges recorded `30/30` (`100%`) substantive epistemic friction in natural prose.
4. **Epistemic boundary preserved:** because blinded human calibration has not yet been completed and all three families ran through a shared enterprise gateway, these results support **preliminary, judge-inferred directional alignment with the pre-registered predictions**, not a settled or universal product-efficacy claim.
