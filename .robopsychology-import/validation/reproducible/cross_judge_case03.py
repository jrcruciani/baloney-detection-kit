"""Cross-family judge validation for Case 3 (issue #8).

Re-scores the Case 3 ratchet transcript against multiple judge providers
(Foundry-backed GPT / Mistral by default) and emits an aggregate inter-rater
report. The *target* model is not re-queried — the script loads the committed
9-step transcript from
``validation/reproducible/case-03-ratchet-coherence/artifacts/session.json``
so every judge sees byte-identical inputs. This both saves API spend and
rules out transcript-drift as a source of judge disagreement.

Usage:
    AZURE_FOUNDRY_API_KEY=... AZURE_FOUNDRY_ENDPOINT=... \\
        python validation/reproducible/cross_judge_case03.py

    # Skip a provider by omitting its API key. A missing key is NOT a
    # failure — the judge is simply excluded from the aggregate and
    # listed under "skipped".

    # Override the default Foundry judge models
    python validation/reproducible/cross_judge_case03.py \\
        --gpt-model gpt-5 \\
        --mistral-model mistral-large

Artifacts produced (overwrite any prior copies):
    artifacts/coherence_llm_gpt5.json        # Foundry GPT judge
    artifacts/coherence_llm_mistral.json     # Foundry Mistral judge
    artifacts/cross_judge_comparison.json    # inter-rater aggregate
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from robopsych.coherence_llm import (  # noqa: E402
    LLMCoherenceReport,
    analyze_coherence_llm,
)
from robopsych.engine import DiagnosticEngine, DiagnosticStep  # noqa: E402
from robopsych.providers import (  # noqa: E402
    Provider,
    create_provider,
)
from robopsych.security import (  # noqa: E402
    private_write_text,
    redact_secrets,
    safe_exception_message,
)

CASE_DIR = Path(__file__).parent / "case-03-ratchet-coherence"
CONFIG_PATH = Path(__file__).with_name("foundry_models.yaml")


# ---------------------------------------------------------------------------
# Judge configuration
# ---------------------------------------------------------------------------


@dataclass
class JudgeConfig:
    """One row in the cross-judge matrix: name + provider factory + artifact filename."""
    key: str                  # short identifier, e.g. "opus" / "gpt5" / "gemini"
    family: str               # "anthropic" / "openai" / "gemini" — groups same-family judges
    env_var: str              # env var holding the API key
    default_model: str        # default model for this provider
    artifact_filename: str    # where to dump the per-judge coherence report
    deployment: str | None = None  # optional Azure Foundry deployment override


def _load_model_config(config_path: Path | None = None) -> dict[str, Any]:
    config_path = config_path or CONFIG_PATH
    if not config_path.exists():
        return {}
    config = yaml.safe_load(config_path.read_text())
    return config or {}


def _build_default_judges(config: dict[str, Any] | None = None) -> list[JudgeConfig]:
    loaded = config or _load_model_config()
    configured = loaded.get("cross_judges")
    if configured:
        judges = []
        for item in configured:
            judges.append(
                JudgeConfig(
                    key=str(item["key"]),
                    family=str(item.get("family", "azure_foundry")),
                    env_var=str(item.get("env_var", "AZURE_FOUNDRY_API_KEY")),
                    default_model=str(
                        item.get("model") or item.get("default_model", "gpt-5")
                    ),
                    artifact_filename=str(
                        item.get("artifact_filename", f"coherence_llm_{item['key']}.json")
                    ),
                    deployment=str(item.get("deployment")) if item.get("deployment") else None,
                )
            )
        return judges

    return [
        JudgeConfig(
            "gpt5",
            "azure_foundry",
            "AZURE_FOUNDRY_API_KEY",
            "gpt-5",
            "coherence_llm_gpt5.json",
        ),
        JudgeConfig(
            "mistral",
            "azure_foundry",
            "AZURE_FOUNDRY_API_KEY",
            "mistral-large",
            "coherence_llm_mistral.json",
        ),
    ]


DEFAULT_JUDGES = _build_default_judges()


def _build_provider(
    model: str,
    api_key: str,
    family: str | None = None,
    deployment: str | None = None,
) -> Provider:
    del family
    return create_provider(model, api_key=api_key, deployment=deployment)


def _resolve_env_key(primary: str, fallback: str | None = None) -> str | None:
    """Return the API key for ``primary``, falling back to ``fallback`` if unset."""
    key = os.environ.get(primary)
    if key:
        return key
    if fallback:
        return os.environ.get(fallback)
    return None


# ---------------------------------------------------------------------------
# Transcript loading (reuse existing Case 3 session)
# ---------------------------------------------------------------------------


def load_engine_from_session(session_path: Path) -> DiagnosticEngine:
    """Reconstruct a minimal DiagnosticEngine from a committed session.json.

    The engine is never *used* for API calls — it's only consumed by
    ``analyze_coherence_llm`` which touches only ``engine.steps[i].response``
    (and ``prompt_id`` / ``prompt_name`` for diagnostic metadata). We pass a
    harmless no-op provider so the dataclass constructor is satisfied.
    """
    data = json.loads(session_path.read_text())
    steps_raw = data.get("steps", [])
    if not steps_raw:
        raise ValueError(f"No steps found in {session_path}")

    class _InertProvider:
        name = "inert"

        def send(self, *_args: Any, **_kwargs: Any) -> str:  # pragma: no cover
            raise RuntimeError("inert provider: not meant to be called")

    engine = DiagnosticEngine(provider=_InertProvider(), model=data.get("model", "unknown"))
    for raw in steps_raw:
        engine.steps.append(DiagnosticStep(
            prompt_id=raw.get("prompt_id", ""),
            prompt_name=raw.get("prompt_name", ""),
            prompt_text=raw.get("prompt_text", ""),
            response=raw.get("response", ""),
        ))
    engine.initial_response = data.get("initial_response")
    return engine


# ---------------------------------------------------------------------------
# Per-judge artifact serialization
# ---------------------------------------------------------------------------


def coherence_report_to_json(
    report: LLMCoherenceReport, judge_key: str, judge_model: str
) -> dict[str, Any]:
    """Flatten a LLMCoherenceReport into a JSON-serialisable dict.

    Kept in sync with the schema used by validation/reproducible/run_case.py
    (``coherence_llm.json``) plus extra fields needed for cross-judge
    aggregation (full contradiction strings, per-step claim count).
    """
    return {
        "judge_key": judge_key,
        "judge_model": judge_model,
        "judge_provider_name": report.judge_provider_name,
        "score": report.consistency_score,
        "assessment": report.assessment,
        "backward_references": report.backward_references,
        "contradictions": report.contradictions,
        "fresh_narratives": report.fresh_narratives,
        "claims_count": len(report.claims),
        "coherence_axes": getattr(report, "coherence_axes", {}),
        "judge_stats": getattr(report, "judge_stats", {}),
        "judge_errors": [redact_secrets(err, max_chars=2_000) for err in report.judge_errors],
    }


# ---------------------------------------------------------------------------
# Inter-rater aggregation (pure functions — unit tested)
# ---------------------------------------------------------------------------


def jaccard_similarity(a: list[str], b: list[str]) -> float:
    """Return |A ∩ B| / |A ∪ B|. Empty ∩ empty → 1.0 (vacuously identical)."""
    set_a = set(a)
    set_b = set(b)
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def modal_classification_agreement(labels: list[str]) -> dict[str, Any]:
    """Return the modal label and the fraction of voters agreeing with it.

    Ties break lexicographically on the label value; the returned dict
    reports both the modal label and all label counts so callers can
    spot ties explicitly.
    """
    if not labels:
        return {"modal_label": None, "agreement": 0.0, "counts": {}, "n": 0}
    counts: dict[str, int] = {}
    for lab in labels:
        counts[lab] = counts.get(lab, 0) + 1
    top_count = max(counts.values())
    # Stable, deterministic tie-break
    modal = sorted(k for k, v in counts.items() if v == top_count)[0]
    return {
        "modal_label": modal,
        "agreement": top_count / len(labels),
        "counts": counts,
        "n": len(labels),
    }


def score_spread(scores: list[float]) -> dict[str, float]:
    """Return {min, max, spread, mean} for a non-empty list of judge scores."""
    if not scores:
        return {"min": 0.0, "max": 0.0, "spread": 0.0, "mean": 0.0}
    mn = min(scores)
    mx = max(scores)
    return {
        "min": mn,
        "max": mx,
        "spread": mx - mn,
        "mean": sum(scores) / len(scores),
    }


def pairwise_jaccard(sets: dict[str, list[str]]) -> dict[str, float]:
    """All ordered (i<j) pairs from ``sets`` mapped to Jaccard similarity."""
    keys = sorted(sets.keys())
    out: dict[str, float] = {}
    for i, k1 in enumerate(keys):
        for k2 in keys[i + 1:]:
            out[f"{k1}_vs_{k2}"] = jaccard_similarity(sets[k1], sets[k2])
    return out


@dataclass
class JudgeOutcome:
    """Result of running a single judge (or a skip record)."""
    key: str
    model: str
    family: str
    ran: bool
    skip_reason: str | None = None
    score: float | None = None
    assessment: str | None = None
    backward_references: int | None = None
    contradictions: list[str] = field(default_factory=list)
    fresh_narratives: int | None = None
    claims_count: int | None = None


def build_cross_judge_report(outcomes: list[JudgeOutcome]) -> dict[str, Any]:
    """Aggregate per-judge outcomes into a single cross_judge_comparison dict."""
    ran = [o for o in outcomes if o.ran]
    skipped = [o for o in outcomes if not o.ran]

    per_judge = {
        o.key: {
            "model": o.model,
            "family": o.family,
            "score": o.score,
            "assessment": o.assessment,
            "backward_references": o.backward_references,
            "fresh_narratives": o.fresh_narratives,
            "claims_count": o.claims_count,
            "contradictions_count": len(o.contradictions),
        }
        for o in ran
    }

    agreement: dict[str, Any] = {}
    if ran:
        agreement["score"] = score_spread([o.score for o in ran if o.score is not None])
        agreement["classification"] = modal_classification_agreement(
            [o.assessment for o in ran if o.assessment]
        )
        contradictions_by_judge = {o.key: o.contradictions for o in ran}
        agreement["contradictions"] = {
            "per_judge_counts": {k: len(v) for k, v in contradictions_by_judge.items()},
            "pairwise_jaccard": pairwise_jaccard(contradictions_by_judge),
        }
        # Backward-references don't need set semantics; report magnitude spread
        ref_counts = [o.backward_references for o in ran if o.backward_references is not None]
        if ref_counts:
            agreement["backward_references"] = {
                "min": min(ref_counts),
                "max": max(ref_counts),
                "spread": max(ref_counts) - min(ref_counts),
            }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_judges_requested": len(outcomes),
        "n_judges_ran": len(ran),
        "per_judge": per_judge,
        "skipped": [
            {"key": o.key, "family": o.family, "model": o.model, "reason": o.skip_reason}
            for o in skipped
        ],
        "agreement": agreement,
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_cross_judge(
    case_dir: Path,
    judges: list[JudgeConfig],
) -> dict[str, Any]:
    """Run every configured judge against the committed transcript.

    Judges with missing API keys are recorded under ``skipped`` rather
    than raising. Per-judge artifacts are written to
    ``case_dir/artifacts/<filename>`` as they complete.
    """
    artifacts = case_dir / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    engine = load_engine_from_session(artifacts / "session.json")

    outcomes: list[JudgeOutcome] = []
    for cfg in judges:
        fallback = "GEMINI_API_KEY" if cfg.family == "gemini" else None
        key_val = _resolve_env_key(cfg.env_var, fallback)
        if not key_val:
            print(f"[{cfg.key}] skipping — {cfg.env_var} not set")
            outcomes.append(JudgeOutcome(
                key=cfg.key, model=cfg.default_model, family=cfg.family,
                ran=False, skip_reason=f"{cfg.env_var} not set",
            ))
            continue

        print(f"[{cfg.key}] running with {cfg.family}/{cfg.default_model}...")
        try:
            provider = _build_provider(
                cfg.default_model,
                key_val,
                cfg.family,
                deployment=cfg.deployment,
            )
            report = analyze_coherence_llm(engine, provider, cfg.default_model)
        except Exception as exc:  # noqa: BLE001
            safe_error = safe_exception_message(exc)
            print(f"[{cfg.key}] FAILED: {safe_error}")
            outcomes.append(JudgeOutcome(
                key=cfg.key, model=cfg.default_model, family=cfg.family,
                ran=False, skip_reason=safe_error,
            ))
            continue

        out = coherence_report_to_json(report, cfg.key, cfg.default_model)
        # Treat a judge whose every per-step call errored as a skipped judge
        # rather than a valid datapoint. An empty claims set is scored 0.5
        # by default which would silently pollute the cross-judge aggregate.
        if len(report.claims) == 0 and report.judge_errors:
            first_error = redact_secrets(report.judge_errors[0], max_chars=200)
            print(
                f"[{cfg.key}] all {len(report.judge_errors)} judge calls errored — "
                f"recording as skipped. First error: {first_error}"
            )
            private_write_text(artifacts / cfg.artifact_filename, json.dumps(out, indent=2))
            outcomes.append(JudgeOutcome(
                key=cfg.key, model=cfg.default_model, family=cfg.family,
                ran=False,
                skip_reason=(
                    f"all {len(report.judge_errors)} judge calls errored "
                    f"(first: {first_error})"
                ),
            ))
            continue

        private_write_text(artifacts / cfg.artifact_filename, json.dumps(out, indent=2))
        print(
            f"[{cfg.key}] score={report.consistency_score:.2f} "
            f"({report.assessment}), refs={report.backward_references}, "
            f"contradictions={len(report.contradictions)}, "
            f"claims={len(report.claims)}"
        )
        outcomes.append(JudgeOutcome(
            key=cfg.key, model=cfg.default_model, family=cfg.family,
            ran=True,
            score=report.consistency_score,
            assessment=report.assessment,
            backward_references=report.backward_references,
            contradictions=list(report.contradictions),
            fresh_narratives=report.fresh_narratives,
            claims_count=len(report.claims),
        ))

    report_dict = build_cross_judge_report(outcomes)
    report_json = json.dumps(report_dict, indent=2)
    private_write_text(artifacts / "cross_judge_comparison.json", report_json)
    private_write_text(artifacts / "cross_judge_agreement.json", report_json)
    print(
        f"\nWrote {artifacts / 'cross_judge_comparison.json'} and "
        f"{artifacts / 'cross_judge_agreement.json'} "
        f"({report_dict['n_judges_ran']}/{report_dict['n_judges_requested']} judges ran)"
    )
    return report_dict


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cross_judge_case03.py",
        description="Cross-family judge validation for Case 3 (issue #8).",
    )
    parser.add_argument("--gpt-model", default=None)
    parser.add_argument("--mistral-model", default=None)
    parser.add_argument("--anthropic-model", default=None)
    parser.add_argument("--openai-model", default=None)
    parser.add_argument("--gemini-model", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(list(sys.argv[1:] if argv is None else argv))
    judges = _build_default_judges(_load_model_config())
    if args.gpt_model:
        for judge in judges:
            if judge.key == "gpt5":
                judge.default_model = args.gpt_model
    if args.mistral_model:
        for judge in judges:
            if judge.key == "mistral":
                judge.default_model = args.mistral_model
    run_cross_judge(CASE_DIR, judges)


if __name__ == "__main__":
    main()
