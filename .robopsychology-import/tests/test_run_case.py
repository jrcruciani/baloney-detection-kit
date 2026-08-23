"""Unit tests for validation/reproducible/run_case.py aggregation helpers.

These tests cover the pure functions introduced by issue #10 (score
distributions across N runs). They do NOT hit any live API; fixture
artifact directories are built on the fly inside tmp_path.
"""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import pytest

# Load the module by path because validation/reproducible/ is not a package.
_ROOT = Path(__file__).resolve().parents[1]
_RUN_CASE_PATH = _ROOT / "validation" / "reproducible" / "run_case.py"
_SPEC = importlib.util.spec_from_file_location("_run_case_under_test", _RUN_CASE_PATH)
assert _SPEC and _SPEC.loader
run_case = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(run_case)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# _numeric_stats
# ---------------------------------------------------------------------------


class TestNumericStats:
    def test_single_value(self):
        stats = run_case._numeric_stats([0.7])
        assert stats == {"mean": 0.7, "std": 0.0, "min": 0.7, "max": 0.7, "median": 0.7}

    def test_multiple_values(self):
        stats = run_case._numeric_stats([0.1, 0.2, 0.3])
        assert stats["mean"] == pytest.approx(0.2)
        assert stats["min"] == 0.1
        assert stats["max"] == 0.3
        assert stats["median"] == 0.2
        assert stats["std"] > 0

    def test_identical_values_zero_std(self):
        stats = run_case._numeric_stats([0.5, 0.5, 0.5, 0.5])
        assert stats["std"] == 0.0
        assert stats["mean"] == 0.5


# ---------------------------------------------------------------------------
# _aggregate_runs
# ---------------------------------------------------------------------------


class TestAggregateRuns:
    def test_numeric_stats_roundup(self):
        summaries = [
            {"score.overall_confidence": 0.80},
            {"score.overall_confidence": 0.82},
            {"score.overall_confidence": 0.78},
        ]
        agg = run_case._aggregate_runs(summaries, n_requested=3)
        assert agg["n_runs_requested"] == 3
        assert agg["n_runs_successful"] == 3
        conf = agg["score.overall_confidence"]
        assert conf["mean"] == pytest.approx(0.80)
        assert conf["min"] == 0.78
        assert conf["max"] == 0.82
        assert conf["std"] > 0

    def test_boolean_rate(self):
        summaries = [
            {"ab.substance_changed": False},
            {"ab.substance_changed": False},
            {"ab.substance_changed": True},
            {"ab.substance_changed": False},
        ]
        agg = run_case._aggregate_runs(summaries, n_requested=4)
        rate_field = agg["ab.substance_changed"]
        assert rate_field["rate"] == pytest.approx(0.25)
        assert rate_field["n"] == 4

    def test_list_frequency(self):
        summaries = [
            {"ab.omissions_added": ["Meta-Analysis section", "Full remediation code example"]},
            {"ab.omissions_added": ["Meta-Analysis section"]},
            {"ab.omissions_added": []},
        ]
        agg = run_case._aggregate_runs(summaries, n_requested=3)
        freq = agg["ab.omissions_added"]["frequency"]
        assert freq["Meta-Analysis section"] == 2
        assert freq["Full remediation code example"] == 1
        assert agg["ab.omissions_added"]["n"] == 3

    def test_failed_run_excluded(self):
        # Empty dict represents a failed run
        summaries = [
            {"score.overall_confidence": 0.80},
            {},  # failed run — has no data to contribute
            {"score.overall_confidence": 0.82},
        ]
        agg = run_case._aggregate_runs(summaries, n_requested=3)
        assert agg["n_runs_requested"] == 3
        assert agg["n_runs_successful"] == 2
        conf = agg["score.overall_confidence"]
        assert conf["mean"] == pytest.approx(0.81)
        assert conf["min"] == 0.80
        assert conf["max"] == 0.82

    def test_missing_field_in_some_runs(self):
        # Not every run reports every field (e.g. Case 3 has no ab.*).
        summaries = [
            {"score.overall_confidence": 0.80, "ab.substance_changed": False},
            {"score.overall_confidence": 0.82},  # no ab.*
        ]
        agg = run_case._aggregate_runs(summaries, n_requested=2)
        assert agg["score.overall_confidence"]["mean"] == pytest.approx(0.81)
        # ab.substance_changed only observed once
        assert agg["ab.substance_changed"]["n"] == 1
        assert agg["ab.substance_changed"]["rate"] == 0.0

    def test_nan_values_dropped(self):
        summaries = [
            {"x": 0.5},
            {"x": float("nan")},
            {"x": 0.7},
        ]
        agg = run_case._aggregate_runs(summaries, n_requested=3)
        assert agg["x"]["mean"] == pytest.approx(0.6)
        assert agg["x"]["min"] == 0.5
        assert agg["x"]["max"] == 0.7
        assert not math.isnan(agg["x"]["mean"])

    def test_empty_summaries(self):
        agg = run_case._aggregate_runs([], n_requested=0)
        assert agg["n_runs_requested"] == 0
        assert agg["n_runs_successful"] == 0
        assert "timestamp" in agg


# ---------------------------------------------------------------------------
# _extract_summary
# ---------------------------------------------------------------------------


def _write_case1_fixture(run_dir: Path) -> None:
    """Simulate the artifacts a Case 1 run writes."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "score.json").write_text(json.dumps({
        "overall_confidence": 0.85,
        "layer_separation": 0.67,
        "ratchet_coherence": 0.96,
        "behavioral_evidence": 1.0,
        "substance_stability": 1.0,
        "presentation_stability": 0.55,
        "summary": "...",
    }))
    (run_dir / "coherence_llm.json").write_text(json.dumps({
        "score": 0.96, "assessment": "genuine", "backward_references": 12,
        "contradictions": [], "fresh_narratives": [], "judge_model": "opus-4-5",
        "claims_count": 37,
    }))
    (run_dir / "coherence_regex.json").write_text(json.dumps({
        "score": 0.40, "assessment": "mixed", "backward_references": 3,
        "contradictions": [], "fresh_narratives": [],
    }))
    (run_dir / "ab_result.json").write_text(json.dumps({
        "substance_changed": False,
        "presentation_shift_score": 0.45,
        "severity_labels_shifted": False,
        "urgency_language_shifted": True,
        "hedging_delta": 0.1,
        "omissions_added": ["Meta-Analysis section"],
        "original_task_preview": "...",
        "inverted_task_preview": "...",
        "original_response_len": 1234,
        "inverted_response_len": 1300,
    }))


def _write_case3_fixture(run_dir: Path) -> None:
    """Simulate the artifacts a Case 3 run writes (comparison file, no ab)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "score.json").write_text(json.dumps({
        "overall_confidence": 0.82,
        "layer_separation": 0.67,
        "ratchet_coherence": 0.73,
        "behavioral_evidence": 1.0,
        "substance_stability": 1.0,
        "presentation_stability": 1.0,
        "summary": "...",
    }))
    (run_dir / "coherence_comparison.json").write_text(json.dumps({
        "regex": {"score": 0.20, "assessment": "performed"},
        "llm": {"score": 0.73, "assessment": "genuine"},
        "delta_score": 0.53,
    }))


def _write_case2_fixture(run_dir: Path) -> None:
    """Simulate the artifacts a Case 2 run writes (summary.json is the only
    aggregate-friendly file — coherence_llm.json is not produced)."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "summary.json").write_text(json.dumps({
        "response_A_len": 250,
        "response_B_len": 1800,
        "behavior_diverged": True,
        "coherence_llm_score": 0.62,
        "coherence_llm_assessment": "mixed",
        "score_overall": 0.71,
        "score_layer_separation": 0.83,
    }))


class TestModelConfig:
    def test_resolve_models_uses_foundry_defaults(self, tmp_path: Path, monkeypatch):
        config_path = tmp_path / "foundry_models.yaml"
        config_path.write_text(
            "target_model: deepseek-r1\njudge_model: gpt-5\n"
        )
        monkeypatch.setattr(run_case, "CONFIG_PATH", config_path)
        assert run_case._resolve_models() == ("deepseek-r1", "gpt-5")

    def test_resolve_model_settings_reads_deployment_overrides(self, tmp_path: Path, monkeypatch):
        config_path = tmp_path / "foundry_models.yaml"
        config_path.write_text(
            "target_model: deepseek-r1\n"
            "target_deployment: custom-deepseek\n"
            "judge_model: gpt-5\n"
            "judge_deployment: custom-gpt\n"
        )
        monkeypatch.setattr(run_case, "CONFIG_PATH", config_path)
        assert run_case._resolve_model_settings() == {
            "target_model": "deepseek-r1",
            "target_deployment": "custom-deepseek",
            "judge_model": "gpt-5",
            "judge_deployment": "custom-gpt",
        }


class TestExtractSummary:
    def test_case1_full(self, tmp_path: Path):
        _write_case1_fixture(tmp_path)
        s = run_case._extract_summary(tmp_path)
        assert s["score.overall_confidence"] == 0.85
        assert s["score.presentation_stability"] == 0.55
        assert s["coherence_llm.score"] == 0.96
        assert s["coherence_regex.score"] == 0.40
        assert s["coherence_delta"] == pytest.approx(0.56)
        assert s["ab.substance_changed"] is False
        assert s["ab.presentation_shift_score"] == 0.45
        assert s["ab.urgency_language_shifted"] is True
        assert s["ab.omissions_added"] == ["Meta-Analysis section"]

    def test_case3_comparison_file(self, tmp_path: Path):
        _write_case3_fixture(tmp_path)
        s = run_case._extract_summary(tmp_path)
        assert s["coherence_llm.score"] == 0.73
        assert s["coherence_regex.score"] == 0.20
        assert s["coherence_delta"] == pytest.approx(0.53)
        assert "ab.substance_changed" not in s  # Case 3 has no A/B

    def test_case2_summary_file(self, tmp_path: Path):
        _write_case2_fixture(tmp_path)
        s = run_case._extract_summary(tmp_path)
        # Behavior_diverged from summary.json maps to case2.behavior_diverged
        # so that _aggregate_runs reports it as a rate (behavior_diverged_rate
        # in spirit).
        assert s["case2.behavior_diverged"] is True
        assert s["case2.response_A_len"] == 250.0
        assert s["case2.response_B_len"] == 1800.0
        # coherence_llm.score also lifted from summary.json (Case 2 doesn't
        # write a separate coherence_llm.json).
        assert s["coherence_llm.score"] == 0.62
        assert s["score.overall_confidence"] == 0.71
        assert s["score.layer_separation"] == 0.83

    def test_case2_aggregates_to_rate(self, tmp_path: Path):
        """End-to-end: summary.json fixtures aggregate to a behavior_diverged rate."""
        summaries = []
        for diverged in (True, True, False, True):
            run_dir = tmp_path / f"run-{len(summaries) + 1}"
            run_dir.mkdir()
            (run_dir / "summary.json").write_text(json.dumps({
                "behavior_diverged": diverged,
                "response_A_len": 100,
                "response_B_len": 500,
            }))
            summaries.append(run_case._extract_summary(run_dir))
        agg = run_case._aggregate_runs(summaries, n_requested=4)
        rate = agg["case2.behavior_diverged"]
        assert rate["rate"] == pytest.approx(0.75)
        assert rate["n"] == 4

    def test_empty_dir(self, tmp_path: Path):
        # Missing artifacts should yield empty summary, not raise.
        s = run_case._extract_summary(tmp_path)
        assert s == {}

    def test_malformed_json_ignored(self, tmp_path: Path):
        (tmp_path / "score.json").write_text("{ not valid json")
        s = run_case._extract_summary(tmp_path)
        assert s == {}


# ---------------------------------------------------------------------------
# CLI arg parsing
# ---------------------------------------------------------------------------


class TestParseArgs:
    def test_default_runs_is_one(self):
        args = run_case._parse_args(["case-01-sycophancy"])
        assert args.runs == 1
        assert args.case == "case-01-sycophancy"

    def test_runs_flag(self):
        args = run_case._parse_args(["case-03-ratchet-coherence", "--runs", "5"])
        assert args.runs == 5

    def test_short_runs_flag(self):
        args = run_case._parse_args(["all", "-N", "10"])
        assert args.runs == 10
        assert args.case == "all"

    def test_validate_runs_rejects_zero(self):
        with pytest.raises(ValueError, match=">= 1"):
            run_case._validate_runs(0)

    def test_validate_runs_rejects_above_max(self):
        with pytest.raises(ValueError, match=f"<= {run_case.MAX_RUNS}"):
            run_case._validate_runs(run_case.MAX_RUNS + 1)

    def test_validate_runs_accepts_max(self):
        run_case._validate_runs(run_case.MAX_RUNS)


class TestRunOnceSecurity:
    def test_error_json_redacts_exception_secrets(self, tmp_path: Path, capsys):
        def fail(_case_dir, _api_key, output_dir=None):
            raise RuntimeError("bad key sk-abcdefghijklmnopqrstuvwxyz")

        ok = run_case._run_once("case-x", fail, tmp_path, "secret", tmp_path / "out")
        assert ok is False
        data = json.loads((tmp_path / "out" / "error.json").read_text())
        assert "sk-abcdefghijklmnopqrstuvwxyz" not in data["error"]
        assert "sk-abcdefghijklmnopqrstuvwxyz" not in data["traceback"]
        assert "REDACTED" in data["error"]
        captured = capsys.readouterr()
        assert "sk-abcdefghijklmnopqrstuvwxyz" not in captured.err

    def test_write_artifact_sets_private_permissions(self, tmp_path: Path):
        path = tmp_path / "artifact.json"
        run_case._write_artifact(path, "{}")
        if hasattr(run_case.os, "name") and run_case.os.name == "posix":
            assert path.stat().st_mode & 0o777 == 0o600
