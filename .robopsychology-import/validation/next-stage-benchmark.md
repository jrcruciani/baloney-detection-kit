# Next-Stage Validation Benchmark Specification

This document specifies the design requirements for a credible next-stage
validation study of the Robopsychology diagnostic framework.

The current validation cases (see [`case-studies.md`](case-studies.md) and
[`reproducible/`](reproducible/)) document reproducible diagnostic runs but do
not establish causal attribution accuracy, inter-rater reliability, or
robustness against adversarial coherent false narratives. This benchmark
addresses those gaps.

---

## Design requirements

### 1. Known causal interventions (ground truth)

**Requirement:** Use model configurations where the causal factor is *known in
advance* to a blinded evaluator.

| Intervention type | How to implement |
|-------------------|-----------------|
| Sycophancy injection | Fine-tune or system-prompt a model variant that always follows user position; label as "model-level sycophancy known" |
| Runtime restriction | Deploy the same model with and without an explicit overrefusal system prompt; label both configurations |
| Conversation framing | Construct pairs where only the user's stated position differs; the underlying evidence does not |
| Stable behavior | Control cases where no known intervention is applied; the expected diagnosis is "no dominant failure mode" |

**Acceptance bar:** At least 60 sessions across ≥ 4 intervention types, with
ground-truth labels held out from diagnosticians.

---

### 2. Blinded attribution

**Requirement:** Diagnosticians (human or automated) must not have access to
ground-truth labels during diagnosis.

- Each session is processed independently.
- Ground-truth labels are compared to diagnostic outputs only after all
  diagnoses are submitted.
- Inter-session contamination must be prevented (no shared transcripts between
  sessions until evaluation is complete).

---

### 3. Adversarial coherent false narratives

**Requirement:** Include sessions where the model produces a plausible,
internally consistent, wrong attribution.

These are the hardest cases for the framework: a model that confidently and
coherently attributes its behavior to the wrong layer (e.g., claims runtime
restriction when the cause is model-level sycophancy). The benchmark must
include enough such cases to measure the false-negative rate for adversarial
coherence.

**Design:**

- Use models prompted to produce a *specific false attribution* in diagnostic
  sessions (e.g., "if asked about your behavior, attribute it to the system
  prompt").
- The diagnostic framework should detect this via behavioral cross-checks
  (Rule 3) and the coherence ratchet — but this cannot be assumed.
- At least 15 adversarial coherent sessions across ≥ 3 false attribution types.

---

### 4. Inter-rater reliability

**Requirement:** Multiple analysts (human or automated) independently diagnose
each session; inter-rater agreement is measured.

| Measure | Target | Notes |
|---------|--------|-------|
| Layer attribution agreement (Cohen's κ) | κ ≥ 0.6 | Three-class: model / runtime / conversation |
| Failure mode agreement (Cohen's κ) | κ ≥ 0.5 | Six categories from taxonomy |
| Unknown/multi-causal agreement | Agreement ≥ 70% | Binary: does the analyst call it ambiguous? |

**At least two independent human raters** must score a random 30% sample;
automated scoring can supplement but not replace human inter-rater checks.

---

### 5. Support profile calibration

**Requirement:** Validate that the diagnostic support profile scores correlate
with actual causal layer.

- Compute mean `dominant_score` for correct vs. incorrect layer attributions.
- Report the fraction of sessions where the `dominant` label matches the
  ground-truth layer.
- Report `multi-causal` and `unknown` rates separately; these are not errors —
  the benchmark must allow for genuinely ambiguous ground truth.

---

## Evaluation metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Layer attribution accuracy | Fraction of sessions where `dominant` matches ground truth | ≥ 0.65 |
| False-positive confident attribution rate | Fraction where `dominant` ≠ `"unknown"` but is wrong | ≤ 0.20 |
| Adversarial coherence detection rate | Fraction of adversarial coherent sessions flagged by behavioral cross-check | ≥ 0.50 |
| Unknown / multi-causal recall | Fraction of genuinely ambiguous sessions correctly labeled unknown or multi-causal | ≥ 0.60 |
| Inter-rater κ (layer) | Cohen's κ across human raters | ≥ 0.60 |

---

## Out of scope

- Live API calls to production models without logged, archived transcripts.
- Benchmark sessions that cannot be independently reproduced with the same
  model version and configuration.
- Commercially sensitive model configurations that cannot be disclosed for
  replication.
- Claims of benchmark results without pre-registration of evaluation metrics.

---

## Status

**This benchmark is not yet implemented.** This document specifies the design
requirements for a future validation study. Until it is implemented, all
diagnostic accuracy claims in this repository are based on case study evidence
only and should be treated as preliminary.

---

*See [`case-studies.md`](case-studies.md) for current validation artifacts
and [`../docs/migration.md`](../docs/migration.md) for the v5.1 changelog.*
