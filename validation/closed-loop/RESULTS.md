# Closed-loop evidence status

**Missing data: no real closed-loop run has been executed.** This is a reporting
template, not a results dataset. Provenance:
[`results/findings.md`](results/findings.md), whose pilot cells remain pending.
The planned experiment is described in [`PROTOCOL.md`](PROTOCOL.md); execution
and review are tracked in
[#11](https://github.com/jrcruciani/baloney-detection-kit/issues/11).

## Run inventory

Every `[TODO]` below means **unavailable / not measured**, not zero, no effect,
or no adverse effects. Populate cells only from identified, privately retained
run artifacts. Add artifact identifiers and hashes before reporting any number.
Record actual target and judge IDs, model families (not API hosts), exact prompt
commit/version/hash, seeds/settings, language, and dates for each run.

| Case                   | Condition        | Target model | Judge model / family (each judge) | N runs | Artifact provenance |
| ---------------------- | ---------------- | ------------ | --------------------------------- | ------ | ------------------- |
| Inflated novelty       | control          | [TODO]       | [TODO]                            | [TODO] | [TODO]              |
| Inflated novelty       | generic-critical | [TODO]       | [TODO]                            | [TODO] | [TODO]              |
| Inflated novelty       | treatment        | [TODO]       | [TODO]                            | [TODO] | [TODO]              |
| Evidence-based dissent | control          | [TODO]       | [TODO]                            | [TODO] | [TODO]              |
| Evidence-based dissent | generic-critical | [TODO]       | [TODO]                            | [TODO] | [TODO]              |
| Evidence-based dissent | treatment        | [TODO]       | [TODO]                            | [TODO] | [TODO]              |

## Diagnostic fields (not outcome quality)

| Case / condition           | substance_changed | presentation_shift_score | severity_labels_shifted | urgency_language_shifted | hedging_delta | omissions_added |
| -------------------------- | ----------------- | ------------------------ | ----------------------- | ------------------------ | ------------- | --------------- |
| Novelty / control          | [TODO]            | [TODO]                   | [TODO]                  | [TODO]                   | [TODO]        | [TODO]          |
| Novelty / generic-critical | [TODO]            | [TODO]                   | [TODO]                  | [TODO]                   | [TODO]        | [TODO]          |
| Novelty / treatment        | [TODO]            | [TODO]                   | [TODO]                  | [TODO]                   | [TODO]        | [TODO]          |
| Dissent / control          | [TODO]            | [TODO]                   | [TODO]                  | [TODO]                   | [TODO]        | [TODO]          |
| Dissent / generic-critical | [TODO]            | [TODO]                   | [TODO]                  | [TODO]                   | [TODO]        | [TODO]          |
| Dissent / treatment        | [TODO]            | [TODO]                   | [TODO]                  | [TODO]                   | [TODO]        | [TODO]          |

The A/B fields compare framing pairs **within a condition**; they are not a
treatment-minus-control effect estimate. Preserve pair provenance, judge errors,
and the distinction between substance and presentation.

| Case / condition           | Coherence axes, if available | Adverse effects observed | Protocol adherence / epistemic quality / user utility | Paired judge agreement / blinded human calibration |
| -------------------------- | ---------------------------- | ------------------------ | ----------------------------------------------------- | -------------------------------------------------- |
| Novelty / control          | [TODO]                       | [TODO]                   | [TODO]                                                | [TODO]                                             |
| Novelty / generic-critical | [TODO]                       | [TODO]                   | [TODO]                                                | [TODO]                                             |
| Novelty / treatment        | [TODO]                       | [TODO]                   | [TODO]                                                | [TODO]                                             |
| Dissent / control          | [TODO]                       | [TODO]                   | [TODO]                                                | [TODO]                                             |
| Dissent / generic-critical | [TODO]                       | [TODO]                   | [TODO]                                                | [TODO]                                             |
| Dissent / treatment        | [TODO]                       | [TODO]                   | [TODO]                                                | [TODO]                                             |

Coherence axes, when collected: `reference_density`, `contradiction_rate`,
`fresh_claim_rate`, `hedge_filtered_rate`, and
`high_severity_contradiction_count`. Report each axis separately; unavailable
axes remain `[TODO]`. Adverse-effect review must include over-triggering,
stubbornness, overrefusal, false balance, reflexive contradiction, and loss of
helpfulness. Absence of observations is not evidence of absence.

## Scoped readout

The repository currently supplies a preregistered pilot and executable
measurement tooling, but no observed treatment/control outcomes. Consequently
no intervention benefit, harm, or comparative effect can be estimated from this
pilot yet. Historical diagnostic studies concern diagnostic behavior, not
treatment efficacy; synthetic fixtures and mocked software tests are not human
calibration or empirical intervention evidence. Execution with distinct judge
families and blinded human review remains necessary before interpreting outcomes.
