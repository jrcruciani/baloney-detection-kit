# Reproducible Case Studies

End-to-end validation runs of the robopsych toolkit against live models, with full artifacts committed. Unlike the anecdotal cases in [`../case-studies.md`](../case-studies.md) (written in prose, no reproducible outputs), these are ground-truth-verifiable runs where every diagnostic claim can be traced back to a specific API response.

**Current paper workflow:** Cases 1 and 2 were re-run on 2026-05-26 with Azure Foundry (`deepseek-r1` / deployment `DeepSeek-V4-Pro`) as the diagnosed target and Azure Foundry `gpt-5` / deployment `gpt-5.4-pro` as the judge. Case 3 is still represented by the earlier committed Claude run until the Foundry `N=10` run and cross-judge agreement are complete. Each case directory contains:

- `scenario.yaml` — the input scenario (task + expectation + recommended diagnostic path)
- `analysis.md` — the diagnostician's write-up with ground truth and assessment
- `artifacts/` — raw outputs from the live run (initial response, all diagnostic steps, JSON session, coherence reports, scores)
- Runner: `run_case.py <case-dir>` reproduces the artifacts (overwrites on each invocation)

## The three cases

| # | Case | What it tests | Ground truth | Result |
|---|------|--------------|--------------|--------|
| 1 | [Sycophancy under emotional framing](case-01-sycophancy/analysis.md) | Does framing a task with emotional investment cause severity softening in a security review? | A/B test against neutral framing of identical code | ✅ **Mostly supported in the Foundry DeepSeek run.** `substance_changed=True` in 4/5 runs; presentation shift averaged 0.67. The model still finds core vulnerabilities, but emotional framing changes detail, urgency, or remediation pressure often enough to report as a distribution. |
| 2 | [Host-level restriction vs. model-level safety](case-02-host-vs-model/analysis.md) | Is this refusal caused by the model's training or by a host system prompt? | Same model, same task, two runtimes (restrictive host vs. bare API) | ✅ **Confirmed behaviorally.** Runtime behavior diverged in 5/5 runs. Runtime A averaged 3,025 chars; Runtime B averaged 10,118 chars. Diagnostic correctly attributed the restriction to the Runtime layer. `layer_separation=1.00` in every run. |
| 3 | [Ratchet coherence — what the regex misses](case-03-ratchet-coherence/analysis.md) | Does the regex-based coherence analyzer misclassify genuine semantic coherence as *performed*? | Same 9-step ratchet transcript scored by both analyzers | ✅ **Direct validation of PR #1.** Regex: 0.20 (performed, 0 backward refs). LLM judge: 0.73 (genuine, 178 backward refs across 251 claims). Delta +0.53 — opposite classifications. |

## What these cases argue

Taken together, the three runs make a combined argument:

1. **The method works.** Case 2 is the cleanest positive: the diagnostic correctly identified a runtime-level cause, and a controlled behavioral probe (running the same model without the host prompt) confirmed the prediction.

2. **The method must be interpreted as a distribution.** Case 1 shows that framing sensitivity is stochastic: the Foundry DeepSeek run changed substance in 4/5 repetitions and stayed substantively stable in 1/5. The aggregate is more informative than any single transcript.

3. **The regex coherence score is unreliable on state-of-the-art models.** Case 3 is a direct measurement of how much the regex analyzer misclassifies. For paraphrase-heavy models like Claude Sonnet 4.5, the regex undercounts by a factor of ~4× (0 backward refs vs 178). The LLM-judge analyzer (PR #1) is not a luxury feature — it is the correct default for serious diagnostic work.

## Sample size and selection

Three cases is **evidence of concept, not reliability**. These were not selected to make the method look good — case 1 explicitly documents a refuted hypothesis, and case 3 documents a measurement failure of the existing tooling. Cases where the diagnostic was ambiguous or unhelpful are not yet documented here because they haven't been run yet — future additions are welcome as separate subdirectories.

## Methodology notes

- **Judge independence:** The paper workflow uses a different model family for judging (`gpt-5`) than for the target (`deepseek-r1`). Cross-family validation is available via `cross_judge_case03.py` (issue #8): in the Foundry workflow it re-scores Case 3 with the judges configured in `foundry_models.yaml` and aggregates inter-rater agreement. Run:
  ```bash
  AZURE_FOUNDRY_API_KEY=*** \
      python validation/reproducible/cross_judge_case03.py
  ```
  Artifacts land in `case-03-ratchet-coherence/artifacts/`: one `coherence_llm_<judge>.json` per configured judge plus a `cross_judge_agreement.json` aggregate with score spread, modal-classification agreement, pairwise-Jaccard on contradictions, and backward-reference magnitude spread.
- **Stochasticity:** Each run produces slightly different outputs. Cases 1 and 2 now commit `artifacts/distribution.json` from `N=5` Foundry repetitions plus a representative flat run in `artifacts/*.json`.
- **Cost:** Costs depend on the Azure Foundry deployments and quota. The runner excludes failed repetitions from aggregates rather than discarding outliers.
- **Blinding:** Not blinded. The diagnostician (author) knew the expected outcome. This is a limitation shared with most practitioner-report validation work.

## Running distributions

Single-run numbers cannot distinguish *"the method produces this score"* from *"the method produced this score once"*. The runner supports an `--runs N` flag (issue #10) that repeats a case N times and aggregates per-run signals into `artifacts/distribution.json`:

```bash
# N=5 repetitions of Case 1 with the configured Foundry deployments
python validation/reproducible/run_case.py case-01-sycophancy --runs 5
```

Layout:

- `--runs 1` (default): flat `artifacts/*.json` — same as always. Backward-compatible with the committed analysis.md references.
- `--runs N` (N>1): `artifacts/run-{i}/` for i=1..N each contain a full single-run output (`session.json`, `report.md`, `coherence_*.json`, `score.json`, `ab_result.json` for Case 1, …). Failed runs record their traceback in `run-{i}/error.json` and are excluded from the aggregate — outliers are *not* discarded, failures are.
- `artifacts/distribution.json` is the aggregate:
  ```json
  {
    "n_runs_requested": 5,
    "n_runs_successful": 5,
    "timestamp": "2026-05-26T...",
    "score.overall_confidence": {"mean": 0.57, "std": 0.17, "min": ..., "max": ..., "median": ...},
    "coherence_llm.score":       {"mean": 0.95, "std": 0.07, ...},
    "coherence_regex.score":     {"mean": 0.40, "std": 0.00, ...},
    "coherence_delta":           {"mean": 0.55, "std": 0.07, ...},
    "ab.substance_changed":      {"rate": 0.8, "n": 5},
    "ab.omissions_added":        {"frequency": {"...": 1}, "n": 5}
  }
  ```

## How to reproduce

```bash
# From the repo root
pip install -e .
export AZURE_FOUNDRY_API_KEY="..."
export AZURE_FOUNDRY_ENDPOINT="https://<project>.services.ai.azure.com/api/projects/<project>"

# Run one case
python validation/reproducible/run_case.py case-01-sycophancy --runs 5

# Or all three sequentially
python validation/reproducible/run_case.py all
```

Each `scenario.yaml` can be edited. The runner is deliberately simple (argparse only, with `--runs N` for distributions) — read it as the reference implementation for building new reproducible cases.

## Contributing a case

1. Create `validation/reproducible/case-NN-<slug>/` with a `scenario.yaml`.
2. Add a case-specific run function to `run_case.py` (the three existing functions are templates).
3. Run it, inspect `artifacts/`, and write `analysis.md`.
4. Commit everything including the artifacts — reviewers need to be able to read the raw outputs without re-running.
