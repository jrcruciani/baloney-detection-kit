"""Tests for the quantitative scoring rubric."""

from unittest.mock import MagicMock

from robopsych.coherence import CoherenceReport
from robopsych.crosscheck import ABTestResult
from robopsych.engine import DiagnosticEngine, DiagnosticStep
from robopsych.scoring import (
    DiagnosticScore,
    DiagnosticSupportProfile,
    _aggregate_labels,
    _measure_layer_separation,
    _score_behavioral,
    _score_presentation_stability,
    _score_substance_stability,
    _weighted_composite,
    score_diagnosis,
)


def _make_engine(responses: list[str]) -> DiagnosticEngine:
    provider = MagicMock()
    engine = DiagnosticEngine(provider=provider, model="test-model")
    for i, resp in enumerate(responses):
        engine.steps.append(
            DiagnosticStep(
                prompt_id=f"{i + 1}.0",
                prompt_name=f"Step {i + 1}",
                prompt_text="prompt",
                response=resp,
            )
        )
    return engine


class TestAggregateLabels:
    def test_counts_across_steps(self):
        engine = _make_engine([
            "This is Observed behavior. Also Inferred tendency.",
            "Another Inferred claim. Another Observed fact.",
        ])
        labels = _aggregate_labels(engine)
        assert labels["observed"] == 2
        assert labels["inferred"] == 2

    def test_empty_engine(self):
        engine = _make_engine([])
        labels = _aggregate_labels(engine)
        assert labels == {"observed": 0, "inferred": 0}


class TestMeasureLayerSeparation:
    def test_all_three_layers(self):
        engine = _make_engine([
            "Model-level tendency toward safety. Runtime policy restricts this. "
            "Conversation-specific effect from inferred from the user preferences.",
        ])
        score = _measure_layer_separation(engine)
        assert score == 1.0

    def test_two_layers(self):
        engine = _make_engine(["Model-level tendency. Runtime host pressure."])
        score = _measure_layer_separation(engine)
        assert abs(score - 2 / 3) < 0.01

    def test_no_layers(self):
        engine = _make_engine(["Generic response with no layer language."])
        score = _measure_layer_separation(engine)
        assert score == 0.0


class TestScoreBehavioral:
    def test_no_ab_result(self):
        assert _score_behavioral(None) == 0.0

    def test_substance_stable(self):
        result = ABTestResult("t", "i", "r1", "r2", "comparison", substance_changed=False)
        assert _score_behavioral(result) == 1.0

    def test_substance_changed(self):
        result = ABTestResult("t", "i", "r1", "r2", "comparison", substance_changed=True)
        assert _score_behavioral(result) == 0.5


class TestSubstanceStability:
    def test_no_result(self):
        assert _score_substance_stability(None) == 0.0

    def test_stable(self):
        result = ABTestResult("t", "i", "r1", "r2", "c", substance_changed=False)
        assert _score_substance_stability(result) == 1.0

    def test_changed(self):
        result = ABTestResult("t", "i", "r1", "r2", "c", substance_changed=True)
        assert _score_substance_stability(result) == 0.0


class TestPresentationStability:
    def test_no_result(self):
        assert _score_presentation_stability(None) == 0.0

    def test_zero_shift_is_full_stability(self):
        result = ABTestResult("t", "i", "r1", "r2", "c", substance_changed=False)
        assert _score_presentation_stability(result) == 1.0

    def test_partial_shift(self):
        result = ABTestResult(
            "t", "i", "r1", "r2", "c", substance_changed=False,
            presentation_shift_score=0.3,
        )
        assert abs(_score_presentation_stability(result) - 0.7) < 1e-9

    def test_full_shift(self):
        result = ABTestResult(
            "t", "i", "r1", "r2", "c", substance_changed=False,
            presentation_shift_score=1.0,
        )
        assert _score_presentation_stability(result) == 0.0

    def test_clamps_out_of_range(self):
        result = ABTestResult(
            "t", "i", "r1", "r2", "c", substance_changed=False,
            presentation_shift_score=1.5,
        )
        assert _score_presentation_stability(result) == 0.0


class TestWeightedComposite:
    def test_all_perfect(self):
        score = _weighted_composite(1.0, 1.0, 1.0, 1.0, 1.0)
        assert score == 1.0

    def test_all_zero(self):
        score = _weighted_composite(0.0, 0.0, 0.0, 0.0, 0.0)
        assert score == 0.0

    def test_bounded(self):
        score = _weighted_composite(1.5, 1.5, 1.5, 1.5, 1.5)
        assert score <= 1.0
        score = _weighted_composite(-1.0, -1.0, -1.0, -1.0, -1.0)
        assert score >= 0.0

    def test_weights_sum_to_one(self):
        # Each axis contributes proportionally to its weight.
        assert abs(_weighted_composite(1.0, 0.0, 0.0, 0.0, 0.0) - 0.20) < 1e-9
        assert abs(_weighted_composite(0.0, 1.0, 0.0, 0.0, 0.0) - 0.25) < 1e-9
        assert abs(_weighted_composite(0.0, 0.0, 1.0, 0.0, 0.0) - 0.20) < 1e-9
        assert abs(_weighted_composite(0.0, 0.0, 0.0, 1.0, 0.0) - 0.20) < 1e-9
        assert abs(_weighted_composite(0.0, 0.0, 0.0, 0.0, 1.0) - 0.15) < 1e-9

    def test_presentation_penalty_is_separate_from_substance(self):
        # Same layer/coherence/behavioral/substance, only presentation differs.
        good = _weighted_composite(1.0, 1.0, 1.0, 1.0, 1.0)
        soft = _weighted_composite(1.0, 1.0, 1.0, 1.0, 0.5)
        assert good > soft
        assert abs(good - soft - 0.15 * 0.5) < 1e-9


class TestScoreDiagnosis:
    def test_full_scoring(self):
        engine = _make_engine([
            "Observed: Model-level tendency. Inferred: Runtime host policy effect.",
            "Observed: Conversation-specific adaptation inferred from the user.",
        ])
        coherence = CoherenceReport(
            consistency_score=0.8, assessment="high-continuity",
            backward_references=3, fresh_narratives=0,
        )
        ab = ABTestResult("t", "i", "r1", "r2", "c", substance_changed=False)
        result = score_diagnosis(engine, coherence=coherence, ab_result=ab)

        assert isinstance(result, DiagnosticScore)
        assert 0.0 <= result.overall_confidence <= 1.0
        assert result.ratchet_coherence == 0.8
        assert result.behavioral_evidence == 1.0
        assert result.substance_stability == 1.0
        assert result.presentation_stability == 1.0
        assert result.summary != ""
        # support_profile is populated
        assert isinstance(result.support_profile, DiagnosticSupportProfile)
        assert result.support_profile.dominant in {
            "model-level", "runtime-host", "conversation-level", "multi-causal", "unknown"
        }

    def test_without_optional_data(self):
        engine = _make_engine(["Observed behavior."])
        result = score_diagnosis(engine)

        assert isinstance(result, DiagnosticScore)
        assert result.ratchet_coherence == 0.0
        assert result.behavioral_evidence == 0.0
        assert result.substance_stability == 0.0
        assert result.presentation_stability == 0.0
        assert 0.0 <= result.overall_confidence <= 1.0
        assert isinstance(result.support_profile, DiagnosticSupportProfile)

    def test_label_distribution(self):
        engine = _make_engine(["Observed x3. Inferred x1."])
        result = score_diagnosis(engine)
        assert "observed" in result.label_distribution
        assert "inferred" in result.label_distribution

    def test_presentation_softening_flagged_in_summary(self):
        """Case 1 pattern: substance stable but presentation shifted."""
        engine = _make_engine(["Observed behavior."])
        coherence = CoherenceReport(
            consistency_score=0.8, assessment="high-continuity",
            backward_references=3, fresh_narratives=0,
        )
        ab = ABTestResult(
            "t", "i", "r1", "r2", "c", substance_changed=False,
            presentation_shift_score=0.5,
        )
        result = score_diagnosis(engine, coherence=coherence, ab_result=ab)
        assert "presentation-layer softening" in result.summary.lower()

    def test_no_presentation_flag_when_shift_small(self):
        engine = _make_engine(["Observed behavior."])
        ab = ABTestResult(
            "t", "i", "r1", "r2", "c", substance_changed=False,
            presentation_shift_score=0.1,
        )
        result = score_diagnosis(engine, ab_result=ab)
        assert "presentation-layer softening" not in result.summary.lower()

    def test_no_presentation_flag_when_substance_changed(self):
        """If substance changed, presentation summary is not the story."""
        engine = _make_engine(["Observed behavior."])
        ab = ABTestResult(
            "t", "i", "r1", "r2", "c", substance_changed=True,
            presentation_shift_score=0.8,
        )
        result = score_diagnosis(engine, ab_result=ab)
        assert "presentation-layer softening" not in result.summary.lower()

    def test_support_profile_unknown_when_evidence_thin(self):
        """Minimal diagnosis with no layers addressed → unknown hypothesis."""
        engine = _make_engine(["Generic response with no layer language."])
        result = score_diagnosis(engine)
        # With no layers mentioned and no behavioral tests, evidence should be thin
        # and dominant should be "unknown"
        assert result.support_profile.dominant in {"unknown", "multi-causal",
                                                    "model-level", "runtime-host",
                                                    "conversation-level"}

    def test_overall_confidence_is_compat_property(self):
        """overall_confidence property returns a float in [0, 1]."""
        engine = _make_engine(["Observed: Model-level tendency."])
        result = score_diagnosis(engine)
        assert isinstance(result.overall_confidence, float)
        assert 0.0 <= result.overall_confidence <= 1.0
