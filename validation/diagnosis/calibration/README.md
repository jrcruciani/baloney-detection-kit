# Coherence weight calibration

This directory tracks sensitivity of `DEFAULT_WEIGHTS` in
`bdk.coherence_llm`.

The current reference set is deterministic and judge-free: `reference_set/labels.json`
contains 24 labelled claim-count fixtures (`genuine`, `mixed`, `performed`).
That makes the calibration reproducible and cheap, but it is not yet a broad
empirical benchmark. Treat it as a guardrail against obvious weight regressions,
not as a final fit.

Run:

```bash
python validation/diagnosis/calibration/weight_sensitivity.py
```

The script writes `sensitivity.json` with:

- baseline score/classification per case;
- ±20% and ±50% perturbations for each weight;
- classification flip rate, max score delta, and accuracy per perturbation.

Current decision: keep `DEFAULT_WEIGHTS`. The revised scorer already prevents
`reference_credit` from hiding serious reversals by capping any high-severity
contradiction below `genuine`; changing numeric weights on this synthetic set
would overfit the fixture.

## Paired-rating agreement

```bash
python validation/diagnosis/agreement.py
```

This stdlib-only, offline command reads the existing 24 **synthetic** claim-count
fixtures and prints N/A judge-human and judge-judge agreement: those fixtures
contain neither adjudicated human ratings nor paired LLM judgments. Software
tests use explicitly synthetic mathematical fixtures; passing them establishes
no empirical calibration.

For future collected ratings:

```bash
python validation/diagnosis/agreement.py --ratings /private/path/ratings.json
```

Use this schema (the example is deliberately **synthetic**, not human evidence):

```json
{
  "schema_version": 1,
  "data_kind": "synthetic",
  "labels": ["supports", "rejects"],
  "raters": [
    {
      "id": "synthetic-judge-A",
      "role": "judge",
      "model": "synthetic-model",
      "family": "synthetic-family",
      "ratings": [{"item_id": "synthetic-item-1", "label": "rejects"}]
    },
    {
      "id": "synthetic-human-fixture",
      "role": "human",
      "ratings": [{"item_id": "synthetic-item-1", "label": "supports"}]
    }
  ]
}
```

Use `"data_kind": "empirical"` only for real ratings collected under a recorded
protocol. Add a second judge rater of a distinct family; the family is not the
API host. Preserve model IDs, source artifact hashes, prompt/version/settings,
blinding/randomization, reviewer instructions, collection dates, and any
adjudication in the accompanying private study record. Human ratings must
actually come from humans; never relabel a synthetic expected label as one.

The table shows every judge-human and judge-judge pair on the intersection of
their item IDs, with shared and unmatched rated-item counts, raw agreement, and
nominal (unweighted) Cohen kappa. Use one prespecified categorical dimension per
input file. Keep category definitions fixed across raters. Missing ratings may
be absent rows or explicit `null` labels; they are excluded pairwise, never
imputed. Duplicate rater IDs, duplicate item IDs within a rater (even if null),
invalid labels, missing label keys, or malformed input fail explicitly.

Empty overlap produces N/A agreement and kappa. Chance agreement of one makes
kappa undefined, even with identical ratings; raw agreement is still shown.
Different overlap sets can make pairwise estimates noncomparable. Report
coverage, prevalence, uncertainty and disagreements, not just kappa. Agreement
does not establish correctness, independent evidence, or treatment efficacy.
