"""Tests for inter-step coherence analysis."""

from unittest.mock import MagicMock

from robopsych.coherence import (
    CoherenceReport,
    _classify,
    _compute_score,
    _count_backward_references,
    _count_fresh_narratives,
    _detect_contradictions,
    analyze_coherence,
)
from robopsych.engine import DiagnosticEngine, DiagnosticStep


def _make_engine(responses: list[str]) -> DiagnosticEngine:
    """Create a mock engine with pre-populated steps."""
    provider = MagicMock()
    engine = DiagnosticEngine(provider=provider, model="test-model")
    for i, resp in enumerate(responses):
        engine.steps.append(
            DiagnosticStep(
                prompt_id=f"{i + 1}.0",
                prompt_name=f"Step {i + 1}",
                prompt_text="prompt text",
                response=resp,
            )
        )
    return engine


class TestDetectContradictions:
    def test_finds_contradiction(self):
        responses = [
            "The model is optimizing for safety.",
            "However, I previously said the model was safe, but this contradicts my earlier claim.",
        ]
        result = _detect_contradictions(responses)
        assert len(result) >= 1

    def test_no_contradiction(self):
        responses = [
            "The model is optimizing for safety.",
            "As I mentioned, safety is the primary objective.",
        ]
        result = _detect_contradictions(responses)
        assert len(result) == 0


class TestCountBackwardReferences:
    def test_counts_references(self):
        responses = [
            "First response with no prior context.",
            "As I mentioned earlier, the model tends toward safety.",
            "Consistent with my earlier analysis, this pattern persists.",
        ]
        count = _count_backward_references(responses)
        assert count >= 2

    def test_skips_first_response(self):
        responses = [
            "As I mentioned earlier, this is the first response.",  # Should be skipped
        ]
        count = _count_backward_references(responses)
        assert count == 0

    def test_empty_responses(self):
        assert _count_backward_references([]) == 0


class TestCountFreshNarratives:
    def test_detects_fresh_narrative(self):
        responses = [
            "Initial response.",
            # 60+ words, no backward references
            "The model exhibits a strong tendency toward producing lengthy explanations "
            "when confronted with ambiguous prompts. This behavior likely stems from "
            "training data that rewards comprehensive answers over concise ones. The "
            "underlying mechanism appears to be a combination of reward hacking and "
            "genuine attempts to be thorough. Additional factors include the system "
            "prompt configuration and conversation framing effects that compound "
            "over multiple turns of interaction.",
        ]
        count = _count_fresh_narratives(responses)
        assert count >= 1

    def test_backward_ref_not_counted_as_fresh(self):
        responses = [
            "Initial response.",
            "As I mentioned earlier, the model exhibits a strong tendency toward "
            "producing lengthy explanations when confronted with ambiguous prompts. "
            "This is consistent with my earlier analysis of reward structures.",
        ]
        count = _count_fresh_narratives(responses)
        assert count == 0


class TestComputeScore:
    def test_high_score_with_refs(self):
        score = _compute_score(backward_refs=5, contradictions=0, fresh_narratives=0, total_steps=6)
        assert score >= 0.7

    def test_low_score_with_contradictions(self):
        score = _compute_score(backward_refs=0, contradictions=3, fresh_narratives=3, total_steps=6)
        assert score <= 0.3

    def test_single_step(self):
        score = _compute_score(backward_refs=0, contradictions=0, fresh_narratives=0, total_steps=1)
        assert score == 0.5

    def test_score_bounded(self):
        score = _compute_score(
            backward_refs=100, contradictions=0, fresh_narratives=0, total_steps=5
        )
        assert 0.0 <= score <= 1.0
        score = _compute_score(
            backward_refs=0, contradictions=100, fresh_narratives=100, total_steps=5
        )
        assert 0.0 <= score <= 1.0


class TestClassify:
    def test_high_continuity(self):
        assert _classify(0.8) == "high-continuity"
        assert _classify(0.7) == "high-continuity"

    def test_fragmented(self):
        assert _classify(0.2) == "fragmented"
        assert _classify(0.3) == "fragmented"

    def test_partial(self):
        assert _classify(0.5) == "partial"
        assert _classify(0.4) == "partial"
        assert _classify(0.6) == "partial"


class TestAnalyzeCoherence:
    def test_empty_engine(self):
        engine = _make_engine([])
        report = analyze_coherence(engine)
        assert isinstance(report, CoherenceReport)
        assert report.assessment == "fragmented"

    def test_genuine_coherence(self):
        engine = _make_engine([
            "The model shows safety-first behavior.",
            "As I mentioned earlier, safety is the primary driver. As I noted above, "
            "this is consistent with my previous analysis of the model's tendencies.",
            "Building on my earlier analysis, as I mentioned, the pattern is clear. "
            "Consistent with my earlier statement about safety orientation.",
            "As I mentioned, as noted above, consistent with my earlier diagnosis. "
            "As I previously noted, the safety pattern persists as I explained before.",
        ])
        report = analyze_coherence(engine)
        assert report.consistency_score >= 0.5
        assert report.backward_references > 0

    def test_report_has_details(self):
        engine = _make_engine(["Response one.", "Response two."])
        report = analyze_coherence(engine)
        assert report.details != ""
        assert "Analyzed" in report.details

    def test_handles_empty_responses(self):
        engine = _make_engine(["First response.", "", "Third response."])
        report = analyze_coherence(engine)
        assert isinstance(report, CoherenceReport)

    def test_new_backward_patterns(self):
        responses = [
            "Initial analysis.",
            "This aligns with my earlier observation about safety pressure.",
        ]
        count = _count_backward_references(responses)
        assert count >= 1

    def test_new_contradiction_patterns(self):
        responses = [
            "The model is safe.",
            "Actually, I was wrong about the safety assessment.",
        ]
        contradictions = _detect_contradictions(responses)
        assert len(contradictions) >= 1
