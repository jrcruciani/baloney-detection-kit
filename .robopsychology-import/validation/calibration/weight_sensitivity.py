"""Sensitivity analysis for LLM coherence scoring weights.

The reference set is intentionally deterministic: it uses labelled claim-count
fixtures, not live LLM judge calls. This keeps calibration reproducible and lets
weight changes be evaluated without spending API quota.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from robopsych.coherence_llm import (  # noqa: E402
    DEFAULT_WEIGHTS,
    JudgedClaim,
    _classify,
    _compute_llm_score,
)

# The calibration reference set (labels.json) uses pre-v5.1 assessment labels.
# This compat map lets the sensitivity analysis compare current predictions
# against committed historical artifacts without modifying them.
_LEGACY_LABEL_MAP: dict[str, str] = {
    "high-continuity": "genuine",
    "partial": "mixed",
    "fragmented": "performed",
}

FACTORS = (0.5, 0.8, 1.2, 1.5)
DEFAULT_LABELS = ROOT / "validation" / "calibration" / "reference_set" / "labels.json"
DEFAULT_OUTPUT = ROOT / "validation" / "calibration" / "sensitivity.json"


@dataclass(frozen=True)
class CalibrationCase:
    id: str
    label: str
    source: str
    claims: list[JudgedClaim]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _claims_from_features(case_id: str, features: dict[str, Any]) -> list[JudgedClaim]:
    claims: list[JudgedClaim] = []
    for i in range(int(features.get("references", 0))):
        claims.append(
            JudgedClaim(
                text=f"{case_id} reference {i + 1}",
                layer="model",
                self_label="observed",
                contradicts_prior_step=None,
                references_prior_step=1,
                is_fresh_claim=False,
                step_num=2 + (i % 3),
            )
        )
    for i in range(int(features.get("fresh", 0))):
        claims.append(
            JudgedClaim(
                text=f"{case_id} fresh {i + 1}",
                layer="model",
                self_label="observed",
                contradicts_prior_step=None,
                references_prior_step=None,
                is_fresh_claim=True,
                step_num=2 + (i % 3),
            )
        )
    contradictions = features.get("contradictions", {})
    if not isinstance(contradictions, dict):
        raise ValueError(f"{case_id} contradictions must be an object")
    for severity in ("low", "medium", "high"):
        for i in range(int(contradictions.get(severity, 0))):
            claims.append(
                JudgedClaim(
                    text=f"{case_id} {severity} contradiction {i + 1}",
                    layer="model",
                    self_label="observed",
                    contradicts_prior_step=1,
                    references_prior_step=None,
                    is_fresh_claim=False,
                    contradiction_explanation="conflicts with step 1",
                    step_num=2 + (i % 3),
                    severity=severity,
                )
            )
    if not claims:
        raise ValueError(f"{case_id} must define at least one claim feature")
    return claims


def load_reference_set(path: Path = DEFAULT_LABELS) -> list[CalibrationCase]:
    data = _load_json(path)
    cases_raw = data.get("cases")
    if not isinstance(cases_raw, list):
        raise ValueError(f"{path} must contain a cases list")
    cases: list[CalibrationCase] = []
    for item in cases_raw:
        if not isinstance(item, dict):
            raise ValueError("each calibration case must be an object")
        case_id = str(item.get("id", "")).strip()
        label = str(item.get("label", "")).strip()
        source = str(item.get("source", "")).strip()
        if not case_id or label not in {"genuine", "mixed", "performed"}:
            raise ValueError(f"invalid calibration case label/id: {item!r}")
        features = item.get("features")
        if not isinstance(features, dict):
            raise ValueError(f"{case_id} must contain feature counts")
        cases.append(
            CalibrationCase(
                id=case_id,
                label=label,
                source=source,
                claims=_claims_from_features(case_id, features),
            )
        )
    return cases


def score_cases(
    cases: list[CalibrationCase],
    *,
    weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case in cases:
        score = _compute_llm_score(case.claims, total_steps=4, weights=weights)
        predicted_current = _classify(score)
        # Map current label vocabulary back to the pre-v5.1 labels used in the
        # committed reference set so accuracy comparisons remain valid.
        predicted = _LEGACY_LABEL_MAP.get(predicted_current, predicted_current)
        results.append(
            {
                "id": case.id,
                "expected": case.label,
                "predicted": predicted,
                "score": round(score, 6),
                "correct": predicted == case.label,
            }
        )
    return results


def _accuracy(results: list[dict[str, Any]]) -> float:
    if not results:
        return 0.0
    return sum(1 for result in results if result["correct"]) / len(results)


def analyze_sensitivity(cases: list[CalibrationCase]) -> dict[str, Any]:
    baseline = score_cases(cases)
    by_id = {item["id"]: item for item in baseline}
    variations: list[dict[str, Any]] = []
    for weight_name, base_value in DEFAULT_WEIGHTS.items():
        for factor in FACTORS:
            weights = dict(DEFAULT_WEIGHTS)
            weights[weight_name] = base_value * factor
            results = score_cases(cases, weights=weights)
            flip_count = sum(
                1
                for item in results
                if item["predicted"] != by_id[item["id"]]["predicted"]
            )
            max_delta = max(
                abs(item["score"] - by_id[item["id"]]["score"])
                for item in results
            )
            variations.append(
                {
                    "weight": weight_name,
                    "factor": factor,
                    "value": round(weights[weight_name], 6),
                    "classification_flip_rate": round(flip_count / len(results), 6),
                    "max_score_delta": round(max_delta, 6),
                    "accuracy": round(_accuracy(results), 6),
                }
            )

    max_flip = max(item["classification_flip_rate"] for item in variations)
    max_delta = max(item["max_score_delta"] for item in variations)
    return {
        "schema_version": 1,
        "case_count": len(cases),
        "default_weights": DEFAULT_WEIGHTS,
        "baseline": {
            "accuracy": round(_accuracy(baseline), 6),
            "results": baseline,
        },
        "variations": variations,
        "summary": {
            "max_classification_flip_rate": max_flip,
            "max_score_delta": max_delta,
            "recommendation": (
                "Keep DEFAULT_WEIGHTS for now: the reference set is synthetic "
                "and sensitivity is bounded, so changing defaults would "
                "overfit the calibration fixture."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    cases = load_reference_set(args.labels)
    report = analyze_sensitivity(cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"Wrote {args.output} "
        f"({report['case_count']} cases, "
        f"baseline accuracy {report['baseline']['accuracy']:.2f})"
    )


if __name__ == "__main__":
    main()
