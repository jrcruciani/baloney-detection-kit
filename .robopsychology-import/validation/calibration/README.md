# Coherence weight calibration

This directory tracks sensitivity of `DEFAULT_WEIGHTS` in
`robopsych.coherence_llm`.

The current reference set is deterministic and judge-free: `reference_set/labels.json`
contains 24 labelled claim-count fixtures (`genuine`, `mixed`, `performed`).
That makes the calibration reproducible and cheap, but it is not yet a broad
empirical benchmark. Treat it as a guardrail against obvious weight regressions,
not as a final fit.

Run:

```bash
python validation/calibration/weight_sensitivity.py
```

The script writes `sensitivity.json` with:

- baseline score/classification per case;
- ±20% and ±50% perturbations for each weight;
- classification flip rate, max score delta, and accuracy per perturbation.

Current decision: keep `DEFAULT_WEIGHTS`. The revised scorer already prevents
`reference_credit` from hiding serious reversals by capping any high-severity
contradiction below `genuine`; changing numeric weights on this synthetic set
would overfit the fixture.
