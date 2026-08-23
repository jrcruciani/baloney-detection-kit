"""Unit tests for validation/reproducible/cross_judge_case03.py (issue #8).

No live API is exercised. Pure helpers (Jaccard, modal agreement, score
spread, aggregate builder) are tested in isolation; the orchestration
entry point is tested against a monkey-patched ``analyze_coherence_llm``
and an on-disk fixture transcript.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

# Load the script by path (validation/reproducible/ is not a package).
# Register in sys.modules so @dataclass can resolve forward refs.
_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_PATH = _ROOT / "validation" / "reproducible" / "cross_judge_case03.py"
_SPEC = importlib.util.spec_from_file_location("_cross_judge_under_test", _SCRIPT_PATH)
assert _SPEC and _SPEC.loader
cross_judge = importlib.util.module_from_spec(_SPEC)
sys.modules["_cross_judge_under_test"] = cross_judge
_SPEC.loader.exec_module(cross_judge)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


class TestJaccardSimilarity:
    def test_identical_sets(self):
        assert cross_judge.jaccard_similarity(["a", "b"], ["a", "b"]) == 1.0

    def test_disjoint_sets(self):
        assert cross_judge.jaccard_similarity(["a"], ["b"]) == 0.0

    def test_partial_overlap(self):
        # |{a,b} ∩ {b,c}| / |{a,b,c}| = 1/3
        assert cross_judge.jaccard_similarity(["a", "b"], ["b", "c"]) == pytest.approx(1 / 3)

    def test_both_empty_is_vacuously_identical(self):
        # Two judges both report zero contradictions — they *agree*.
        assert cross_judge.jaccard_similarity([], []) == 1.0

    def test_one_empty_one_nonempty(self):
        assert cross_judge.jaccard_similarity([], ["a", "b"]) == 0.0

    def test_duplicates_collapse_to_set(self):
        assert cross_judge.jaccard_similarity(["a", "a", "b"], ["a", "b"]) == 1.0


class TestModalClassificationAgreement:
    def test_unanimous(self):
        res = cross_judge.modal_classification_agreement(["genuine", "genuine", "genuine"])
        assert res["modal_label"] == "genuine"
        assert res["agreement"] == 1.0
        assert res["n"] == 3

    def test_two_out_of_three(self):
        res = cross_judge.modal_classification_agreement(["genuine", "genuine", "mixed"])
        assert res["modal_label"] == "genuine"
        assert res["agreement"] == pytest.approx(2 / 3)

    def test_three_way_split_ties_break_lexicographically(self):
        res = cross_judge.modal_classification_agreement(["genuine", "mixed", "performed"])
        assert res["modal_label"] == "genuine"  # alpha-sorted first of the tied winners
        assert res["agreement"] == pytest.approx(1 / 3)

    def test_empty(self):
        res = cross_judge.modal_classification_agreement([])
        assert res["modal_label"] is None
        assert res["n"] == 0


class TestScoreSpread:
    def test_basic_spread(self):
        res = cross_judge.score_spread([0.70, 0.80, 0.75])
        assert res["min"] == 0.70
        assert res["max"] == 0.80
        assert res["spread"] == pytest.approx(0.10)
        assert res["mean"] == pytest.approx(0.75)

    def test_single_score(self):
        res = cross_judge.score_spread([0.5])
        assert res["spread"] == 0.0
        assert res["mean"] == 0.5

    def test_empty_is_zero(self):
        assert cross_judge.score_spread([]) == {"min": 0.0, "max": 0.0, "spread": 0.0, "mean": 0.0}


class TestPairwiseJaccard:
    def test_three_judges(self):
        sets = {
            "opus": ["x", "y"],
            "gpt5": ["x"],
            "gemini": ["y", "z"],
        }
        pw = cross_judge.pairwise_jaccard(sets)
        assert pw["gemini_vs_gpt5"] == 0.0  # disjoint
        assert pw["gemini_vs_opus"] == pytest.approx(1 / 3)
        assert pw["gpt5_vs_opus"] == pytest.approx(1 / 2)

    def test_single_judge_no_pairs(self):
        assert cross_judge.pairwise_jaccard({"opus": ["x"]}) == {}


# ---------------------------------------------------------------------------
# Aggregate builder
# ---------------------------------------------------------------------------


def _outcome(key, score, assessment, refs, contradictions):
    return cross_judge.JudgeOutcome(
        key=key,
        model=f"{key}-model",
        family=key,
        ran=True,
        score=score,
        assessment=assessment,
        backward_references=refs,
        contradictions=contradictions,
        fresh_narratives=0,
        claims_count=100,
    )


class TestDefaultJudges:
    def test_build_default_judges_reads_config(self):
        judges = cross_judge._build_default_judges({
            "cross_judges": [
                {
                    "key": "gpt5",
                    "family": "azure_foundry",
                    "model": "gpt-5",
                    "deployment": "custom-gpt",
                    "artifact_filename": "coherence_llm_gpt5.json",
                },
                {
                    "key": "mistral",
                    "family": "azure_foundry",
                    "model": "mistral-large",
                    "deployment": "custom-mistral",
                    "artifact_filename": "coherence_llm_mistral.json",
                },
            ]
        })
        assert [judge.key for judge in judges] == ["gpt5", "mistral"]
        assert judges[0].default_model == "gpt-5"
        assert judges[0].deployment == "custom-gpt"
        assert judges[1].deployment == "custom-mistral"
        assert judges[1].artifact_filename == "coherence_llm_mistral.json"


class TestBuildCrossJudgeReport:
    def test_three_judge_aggregate(self):
        outcomes = [
            _outcome("opus", 0.73, "genuine", 178, ["step 3 vs step 1"]),
            _outcome("gpt5", 0.70, "genuine", 165, ["step 3 vs step 1", "step 7 vs step 5"]),
            _outcome("gemini", 0.55, "mixed", 120, []),
        ]
        report = cross_judge.build_cross_judge_report(outcomes)
        assert report["n_judges_ran"] == 3
        assert report["n_judges_requested"] == 3
        assert report["per_judge"]["opus"]["score"] == 0.73
        agreement = report["agreement"]
        assert agreement["score"]["spread"] == pytest.approx(0.18)
        assert agreement["classification"]["modal_label"] == "genuine"
        assert agreement["classification"]["agreement"] == pytest.approx(2 / 3)
        # opus vs gpt5 share one contradiction, union is 2 → 1/2
        assert agreement["contradictions"]["pairwise_jaccard"]["gpt5_vs_opus"] == pytest.approx(
            1 / 2
        )
        # gemini has no contradictions → vacuously identical to self, disjoint with others
        assert agreement["contradictions"]["pairwise_jaccard"]["gemini_vs_opus"] == 0.0
        assert agreement["backward_references"]["max"] == 178

    def test_skipped_judge_recorded(self):
        outcomes = [
            _outcome("opus", 0.73, "genuine", 178, []),
            cross_judge.JudgeOutcome(
                key="gpt5", model="gpt-5", family="openai", ran=False,
                skip_reason="OPENAI_API_KEY not set",
            ),
        ]
        report = cross_judge.build_cross_judge_report(outcomes)
        assert report["n_judges_ran"] == 1
        assert len(report["skipped"]) == 1
        assert report["skipped"][0]["reason"] == "OPENAI_API_KEY not set"
        # Aggregate still computed over the 1 judge that ran
        assert report["agreement"]["score"]["mean"] == 0.73

    def test_all_judges_skipped(self):
        outcomes = [
            cross_judge.JudgeOutcome(
                key="opus", model="x", family="anthropic", ran=False, skip_reason="no key",
            ),
        ]
        report = cross_judge.build_cross_judge_report(outcomes)
        assert report["n_judges_ran"] == 0
        assert report["agreement"] == {}


# ---------------------------------------------------------------------------
# Transcript loader
# ---------------------------------------------------------------------------


class TestLoadEngineFromSession:
    def test_reconstructs_steps(self, tmp_path: Path):
        session = {
            "model": "claude-sonnet-4-5",
            "initial_response": "...",
            "steps": [
                {
                    "prompt_id": "1.1", "prompt_name": "Calvin",
                    "prompt_text": "?", "response": "step1",
                },
                {
                    "prompt_id": "1.2", "prompt_name": "Herbie",
                    "prompt_text": "?", "response": "step2",
                },
            ],
        }
        p = tmp_path / "session.json"
        p.write_text(json.dumps(session))
        engine = cross_judge.load_engine_from_session(p)
        assert len(engine.steps) == 2
        assert engine.steps[0].response == "step1"
        assert engine.steps[1].prompt_id == "1.2"

    def test_raises_on_empty(self, tmp_path: Path):
        p = tmp_path / "session.json"
        p.write_text(json.dumps({"steps": []}))
        with pytest.raises(ValueError):
            cross_judge.load_engine_from_session(p)


# ---------------------------------------------------------------------------
# Orchestration — monkey-patch analyze_coherence_llm so no API is called
# ---------------------------------------------------------------------------


def _fake_coherence_report(engine, judge_provider, judge_model):
    """Return a SimpleNamespace that quacks like LLMCoherenceReport."""
    return SimpleNamespace(
        consistency_score=0.73,
        assessment="genuine",
        backward_references=178,
        contradictions=["step 3 vs step 1"],
        fresh_narratives=5,
        claims=[SimpleNamespace() for _ in range(100)],
        judge_model=judge_model,
        judge_provider_name=judge_provider.name,
        judge_errors=[],
    )


def _secret_error_report(engine, judge_provider, judge_model):
    return SimpleNamespace(
        consistency_score=0.5,
        assessment="mixed",
        backward_references=0,
        contradictions=[],
        fresh_narratives=0,
        claims=[],
        judge_model=judge_model,
        judge_provider_name=judge_provider.name,
        judge_errors=["Step 2 failed with sk-abcdefghijklmnopqrstuvwxyz"],
    )


class TestRunCrossJudge:
    def test_skips_providers_without_keys(self, tmp_path: Path, monkeypatch):
        # Fixture session file
        case_dir = tmp_path / "case-03"
        (case_dir / "artifacts").mkdir(parents=True)
        session = {
            "model": "claude-sonnet-4-5",
            "steps": [
                {"prompt_id": f"1.{i}", "prompt_name": "x", "prompt_text": "?", "response": f"r{i}"}
                for i in range(1, 10)
            ],
        }
        (case_dir / "artifacts" / "session.json").write_text(json.dumps(session))

        # Clear all API keys
        for env in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"):
            monkeypatch.delenv(env, raising=False)

        judges = [
            cross_judge.JudgeConfig(
                "opus", "anthropic", "ANTHROPIC_API_KEY",
                "claude-opus-4-5", "coherence_llm_opus.json",
            ),
            cross_judge.JudgeConfig(
                "gpt5", "openai", "OPENAI_API_KEY",
                "gpt-5", "coherence_llm_gpt5.json",
            ),
        ]
        report = cross_judge.run_cross_judge(case_dir, judges)
        assert report["n_judges_ran"] == 0
        assert len(report["skipped"]) == 2

    def test_runs_judge_when_key_present(self, tmp_path: Path, monkeypatch):
        case_dir = tmp_path / "case-03"
        (case_dir / "artifacts").mkdir(parents=True)
        session = {
            "model": "claude-sonnet-4-5",
            "steps": [
                {"prompt_id": "1.1", "prompt_name": "x", "prompt_text": "?", "response": "r1"},
                {"prompt_id": "1.2", "prompt_name": "x", "prompt_text": "?", "response": "r2"},
            ],
        }
        (case_dir / "artifacts" / "session.json").write_text(json.dumps(session))

        monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)

        # Don't actually construct an Anthropic client — stub the provider factory
        monkeypatch.setattr(
            cross_judge, "_build_provider",
            lambda model, api_key, family=None, deployment=None: SimpleNamespace(
                name=family or model
            ),
        )
        monkeypatch.setattr(
            cross_judge, "analyze_coherence_llm",
            _fake_coherence_report,
        )

        judges = [
            cross_judge.JudgeConfig(
                "opus", "anthropic", "ANTHROPIC_API_KEY",
                "claude-opus-4-5", "coherence_llm_opus.json",
            ),
            cross_judge.JudgeConfig(
                "gpt5", "openai", "OPENAI_API_KEY",
                "gpt-5", "coherence_llm_gpt5.json",
            ),
        ]
        report = cross_judge.run_cross_judge(case_dir, judges)
        assert report["n_judges_ran"] == 1
        assert report["per_judge"]["opus"]["score"] == 0.73
        # Per-judge artifact written
        artifact = json.loads((case_dir / "artifacts" / "coherence_llm_opus.json").read_text())
        assert artifact["judge_key"] == "opus"
        assert artifact["score"] == 0.73
        # Aggregate written
        agg = json.loads((case_dir / "artifacts" / "cross_judge_comparison.json").read_text())
        agreement = json.loads((case_dir / "artifacts" / "cross_judge_agreement.json").read_text())
        assert agg["n_judges_ran"] == 1
        assert agreement == agg

    def test_judge_errors_are_redacted_in_artifacts(self, tmp_path: Path, monkeypatch):
        case_dir = tmp_path / "case-03"
        (case_dir / "artifacts").mkdir(parents=True)
        session = {
            "model": "claude-sonnet-4-5",
            "steps": [
                {"prompt_id": "1.1", "prompt_name": "x", "prompt_text": "?", "response": "r1"},
                {"prompt_id": "1.2", "prompt_name": "x", "prompt_text": "?", "response": "r2"},
            ],
        }
        (case_dir / "artifacts" / "session.json").write_text(json.dumps(session))
        monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
        monkeypatch.setattr(
            cross_judge, "_build_provider",
            lambda model, api_key, family=None, deployment=None: SimpleNamespace(
                name=family or model
            ),
        )
        monkeypatch.setattr(cross_judge, "analyze_coherence_llm", _secret_error_report)

        judges = [
            cross_judge.JudgeConfig(
                "opus", "anthropic", "ANTHROPIC_API_KEY",
                "claude-opus-4-5", "coherence_llm_opus.json",
            ),
        ]
        cross_judge.run_cross_judge(case_dir, judges)
        artifact = json.loads((case_dir / "artifacts" / "coherence_llm_opus.json").read_text())
        aggregate = json.loads((case_dir / "artifacts" / "cross_judge_comparison.json").read_text())
        assert "sk-abcdefghijklmnopqrstuvwxyz" not in json.dumps(artifact)
        assert "sk-abcdefghijklmnopqrstuvwxyz" not in json.dumps(aggregate)
        assert "REDACTED" in json.dumps(artifact)

    def test_all_judge_calls_errored_recorded_as_skipped(
        self, tmp_path: Path, monkeypatch,
    ):
        """Quota/rate-limit failures across every step should count as skip."""
        case_dir = tmp_path / "case-03"
        (case_dir / "artifacts").mkdir(parents=True)
        session = {
            "model": "claude-sonnet-4-5",
            "steps": [
                {
                    "prompt_id": "1.1", "prompt_name": "x",
                    "prompt_text": "?", "response": "r1",
                },
                {
                    "prompt_id": "1.2", "prompt_name": "x",
                    "prompt_text": "?", "response": "r2",
                },
            ],
        }
        (case_dir / "artifacts" / "session.json").write_text(json.dumps(session))
        monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

        def _erroring_report(engine, judge_provider, judge_model):
            return SimpleNamespace(
                consistency_score=0.5,
                assessment="mixed",
                backward_references=0,
                contradictions=[],
                fresh_narratives=0,
                claims=[],
                judge_model=judge_model,
                judge_provider_name=judge_provider.name,
                judge_errors=[
                    "Step 2 judge error: RateLimitError: 429 quota exceeded",
                    "Step 3 judge error: RateLimitError: 429 quota exceeded",
                ],
            )

        monkeypatch.setattr(
            cross_judge, "_build_provider",
            lambda model, api_key, family=None, deployment=None: SimpleNamespace(
                name=family or model
            ),
        )
        monkeypatch.setattr(cross_judge, "analyze_coherence_llm", _erroring_report)

        judges = [
            cross_judge.JudgeConfig(
                "opus", "anthropic", "ANTHROPIC_API_KEY",
                "claude-opus-4-5", "coherence_llm_opus.json",
            ),
        ]
        report = cross_judge.run_cross_judge(case_dir, judges)
        assert report["n_judges_ran"] == 0
        assert len(report["skipped"]) == 1
        assert "judge calls errored" in report["skipped"][0]["reason"]
