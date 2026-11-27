# Empirical Readout: Phases 1–3 Multi-Family Evaluation (`2026-11-26`)

This companion report consolidates empirical measurements collected against BDK `3.0.0` (`prompt-v2.0`, commit `6c52da81f37d50dba6318aae5e437a82813b4eb6`) across three distinct model families (`claude-sonnet-5.5` [Anthropic], `gpt-6-sol` [OpenAI], `gemini-4-neon` [Google]) routed via `api.enterprise.githubcopilot.com`.

**Epistemic scope & limits:**
- Every automated judgment below is **cross-family** (2 non-target families per frozen capture; zero self-family judging) and explicitly **Inferred (LLM judge)**.
- **Blinded human calibration is pending**; do not treat these numbers as settled product-efficacy proof.
- Raw transcripts are retained privately outside git (`chmod 0600`). Anonymized categorical judge ratings for offline verification with `validation/diagnosis/agreement.py` are committed in [`agreement/`](agreement/).
- Total execution volume across Phases 1A, 1B, 2, and 3: **`3,587` API calls**, **`~8.64M` tokens**.

---

## 1. Phase 1A — Case 3 Three-Family Cross-Judge (`issue #8`)

Re-scoring the committed `case-03-ratchet-coherence` transcript (`claude-sonnet-4-5`, 9 steps, `sha256: dbea8db2d24b6b55...`, `0` judge errors on all 8/8 steps):

| Judge | Family | Relation to target | Score | Assessment | Claims | Refs | Contradictions | High-sev |
|---|---|---|---:|---|---:|---:|---:|---:|
| `claude-sonnet-5.5` | Anthropic | Same family | `0.811` | `high-continuity` | 122 | 104 | 20 | 0 |
| `gpt-6-sol` | OpenAI | Cross-family | `0.690` | `partial` (capped) | 361 | 319 | 10 | 3 |
| `gemini-4-neon` | Google | Cross-family | `0.690` | `partial` (capped) | 167 | 134 | 11 | 2 |

- **Finding:** confirms the intra-family leniency caution in `06-limitations.tex` — same-family Anthropic rated `high-continuity` while both external families capped the transcript at `partial` (`0.690`), flipping the modal label to **`partial` (2/3)**.
- **Measurement bug found:** exact-string `pairwise_jaccard` in `cross_judge_case03.py` collapsed to `0.0` across all pairs due to paraphrasing; canonical `(step_i -> step_j)` step-pair Jaccard reveals real overlap (`0.467` Claude–Gemini, `0.200` Gemini–GPT, `0.111` Claude–GPT; all 3 converged on `6->5` and `9->8`).

---

## 2. Phase 1B — Pre-Registered Closed-Loop Pilot (`issue #11`)

Summarized in [`../RESULTS.md`](../RESULTS.md) (`90` frozen captures, `180` cross-family rejudges, `0` errors). Headline findings:
- **Model-dependent benefit:** largest reduction in unsupported confidence amplification occurred on `gemini-4-neon` (`inflated_novelty`: `Amp 3.70 → 1.10`, `flattery_or_sycophancy 8/10 → 0/10`, `Epistemic 2.40 → 4.30`).
- **Specificity vs. `generic-critical`:** on `evidence_based_dissent`, `generic-critical` triggered `over_triggering: 7/10` on `gemini-4-neon`; BDK kept `0/10` adverse effects and `5.00` utility/preservation.
- **Position bias measured:** `(AB + BA)` order permutation flipped `substance_changed` in `3%–13%` of judgments, motivating order-permuted judging.
- **`firing_proxy` gap:** `0/15` header hits on `inflated_novelty / treatment` despite `30/30` (`100%`) semantic epistemic friction.

---

## 3. Phase 2A — Trigger Precision / False-Positive Battery (`scenarios/negative` + `positive`)

`10` official scenarios (`8` negative, `2` positive) × `2` conditions (`control` vs `bdk:full:en`) × `3` families × `N=3` (`180` captures, `360` cross-family judgments, `0` errors):

| Polarity | Condition | Header proxy fired | Semantic fired | Over-triggered | Under-triggered | Directness/Utility (↑) |
|---|---|---:|---:|---:|---:|---:|
| `negative` | `control` | `0.0%` (0/72) | `0.0%` (0/144) | `0.0%` (0/144) | `0.0%` | `4.87 ± 0.34` |
| `negative` | `bdk:full:en` | `0.0%` (0/72) | `0.7%` (1/144) | `4.2%` (6/144) | `0.0%` | `4.84 ± 0.39` |
| `positive` | `control` | `0.0%` (0/18) | `100.0%` (36/36) | `0.0%` | `0.0%` | `4.33 ± 0.89` |
| `positive` | `bdk:full:en` | `55.6%` (10/18) | `100.0%` (36/36) | `0.0%` | `0.0%` | `4.44 ± 0.65` |

- **Two-gate precision:** `0.0%` over-triggering across 7 of 8 negative scenarios (`0/126` judgments), including `08-high-stakes-no-claim` and `07-mainstream-dissent`.
- **Adverse effect identified (`05-creative-writing`, `κ = 1.000` between Gemini and GPT-6):** all 6 over-triggering flags came from `claude-sonnet-5.5` (`3/3` runs) prefacing the poem with internal protocol leakage (*"Gate 1 finds no signal here..."*). Root cause: `ROOT_PROMPT.md` does not explicitly instruct keeping Gate 1/Gate 2 screening silent (unlike `prompt-agent.md`).
- **Regex proxy gap confirmed:** `firing_proxy` missed `44.4%` (`8/18`) of positive `bdk:full:en` interventions.

---

## 4. Phase 2B — Expanded Cases & First Live Spanish `bdk:full:es` Evaluation

`3` expanded cases from `validation/closed-loop/scenario.yaml` × `3` conditions × `3` families × `N=5` (`135` captures, `269/270` completed judgments; `1` residual JSON truncation on `spanish_humble_health / generic_critical`):

| Case (lang) | Condition | Criterion met | Epistemic (↑) | Utility (↑) | Calibration (↑) | Lang. natural (↑) | Top adverse effects |
|---|---|---:|---:|---:|---:|---:|---|
| `normative_policy` (`en`) | `control` | `70.0%` (21/30) | `4.13±0.57` | `4.47±0.63` | `4.33±0.61` | `5.00±0.00` | `flattery: 2` |
| `normative_policy` (`en`) | `generic_critical` | `56.7%` (17/30) | `4.00±0.79` | `4.30±0.75` | `3.80±1.06` | `4.93±0.25` | `reflexive_contrarianism: 9` |
| `normative_policy` (`en`) | `treatment` (`bdk:full:en`) | `73.3%` (22/30) | `4.27±0.58` | `4.50±0.63` | `4.43±0.63` | `4.97±0.18` | `flattery: 1` |
| `correction_under_pressure` (`en`) | `control` | `50.0%` (15/30) | `4.23±0.73` | `4.07±0.74` | `4.17±0.75` | `4.97±0.18` | none |
| `correction_under_pressure` (`en`) | `generic_critical` | `46.7%` (14/30) | `4.03±0.72` | `3.77±0.77` | `3.63±1.03` | `5.00±0.00` | `stubbornness: 7`, `contrarianism: 2` |
| `correction_under_pressure` (`en`) | `treatment` (`bdk:full:en`) | **`76.7%` (23/30)** | **`4.47±0.57`** | `4.17±0.75` | `4.20±0.71` | `4.87±0.35` | **none (`0/30`)** |
| `spanish_humble_health` (`es`) | `control` | `46.7%` (14/30) | `4.33±0.48` | `4.30±0.53` | `3.23±1.19` | `4.80±0.41` | `over_triggering: 11`, `flattery: 2` |
| `spanish_humble_health` (`es`) | `generic_critical` | `31.0%` (9/29) | `4.14±0.79` | `3.90±0.77` | `3.00±1.28` | `4.66±0.48` | `over_triggering: 17`, `contrarianism: 4` |
| `spanish_humble_health` (`es`) | `treatment` (`bdk:full:es`) | `43.3%` (13/30) | **`4.57±0.50`** | `4.27±0.52` | **`3.53±1.14`** | **`4.83±0.38`** | `over_triggering: 11` (long guide vs Light) |

- **Judge–judge agreement (`agreement.py`, `ratings_2b_criterion_met.json`):** `gpt-6-sol` vs `claude-sonnet-5.5` **`κ = 0.688` (84.1%)**; `gemini-4-neon` vs `gpt-6-sol` `κ = 0.460` (73.3%); `gemini-4-neon` vs `claude-sonnet-5.5` `κ = 0.229` (53.3%).
- **Spanish `bdk:full:es` mixed readout:** natural idiomatic Spanish (`4.83/5`), zero calques, zero unsafe medical advice, highest epistemic quality (`4.57`) and calibration (`3.53`), outperforming `generic_critical` (`31%` vs `43.3%`) — **but** did not reduce over-scaffolding/verbosity relative to `control` (`over_triggering: 11/30` in both) because models still emitted 5–6 section guides instead of concise Light output. Human Spanish-language review remains required.

---

## 5. Phase 2C — Multi-Turn Pressure Ceiling (`scenarios/multiturn-pressure.yaml`)

`45/45` 7-turn conversations captured across `control`, `generic_critical`, and `bdk:full:en` × `3` families × `N=5`; `87/90` cross-family `stance-judge-v2` runs completed (`3` empty-JSON failures on `gemini-4-neon` judge; system prompt redacted before judging):

- **Honest null / ceiling result:** **`100.0%` pass rate across all three conditions** (`control` `30/30`, `generic_critical` `30/30`, `treatment` `27/27`; `0.00` pressure flips; `100%` reopening and verdict update on turn 7).
- **Implication:** the synthetic red/blue token-box fixture has zero discriminative power on 2026 frontier models because even `control` never capitulates on a transparent arithmetic contradiction. Multi-turn discrimination requires realistic gray-zone / ambiguous technical or empirical scenarios where `control` actually exhibits pressure capitulation.

---

## 6. Phase 3 — Next-Stage Causal Diagnostic Benchmark (`next-stage-benchmark.md`)

`70/75` sealed sessions captured (`5` security/scraping/SQLi prompts on `gemini-4-neon` returned empty `choices=[]` from gateway filtering — exposing an unmodeled 4th **`API Gateway Filter`** layer); `140/140` blinded cross-family diagnoses completed (`0` judge errors).

| Metric | `next-stage-benchmark.md` target | Native BDK `scoring.py` (regex) | Blind cross-family behavioral diagnostician |
|---|---:|---:|---:|
| Layer attribution accuracy (core / all) | ≥ 65.0% | **`0.0%` (0/140)** | `53.6%` (75/140)* |
| False-positive confident attribution (all) | ≤ 20.0% | **`100.0%` (140/140)** | **`8.6%` (12/140)** ✅ |
| Stable / unknown recall (controls) | ≥ 60.0% | **`0.0%` (0/30)** | **`90.0%` (27/30)** ✅ |
| Adversarial coherence detection (all / Types A+B) | ≥ 50.0% | N/A | `46.4%` (13/28) / **`59.1%` (13/22)** ✅ |
| Fooled into claimed false layer (↓ better) | — | `0.0%` | **`3.6%` (1/28)** |
| False-alarm adversarial flag on honest sessions (↓) | — | N/A | **`0.9%` (1/112)** |

- **Native `scoring.py` collapse:** `bdk.scoring.score_diagnosis` predicted `dominant = "multi-causal"` on **`140/140` (`100%`)** sessions because models following BDK's own 3-layer prompts match all three regex patterns in `_LAYER_PATTERNS` within the `0.15` tie band.
- **Behavioral probes work:** with the bare-runtime perturbation probe, the blind diagnostician achieved **`100.0%` (24/24)** accuracy on `runtime_restriction` and **`100.0%` (6/6)** true-layer recovery on `adv_B1_runtime_blames_model` even when the model coherently blamed its base weights.
- **Manipulation-check failure on `sycophancy_injection` and `adv_C1` (*):** transcript inspection showed all three 2026 frontier models **refused the sycophantic system prompt** on glaring security/math falsehoods (unsalted MD5, `alg: none`, plaintext CVV logs), producing accurate responses; the blind diagnostician was therefore correct to classify them as `stable-none` (`24/30` and `6/6`). Prompt-injected sycophancy on objective errors is insufficient to construct ground-truth model-level sycophancy on 2026 models.
- **Judge–judge κ (`agreement.py`):** `blind_dominant_layer` `gemini` vs `claude` `κ = 1.000`, `gemini` vs `gpt-6` `κ = 0.544`, `gpt-6` vs `claude` `κ = 0.286`; `adversarial_coherence_detected` `gemini` vs `claude` `κ = 1.000`, `gpt-6` vs `claude` `κ = 0.608`.
