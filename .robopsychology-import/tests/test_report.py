"""Tests for report generation."""

import json
from unittest.mock import MagicMock

from robopsych.engine import DiagnosticEngine, DiagnosticStep
from robopsych.report import (
    count_labels,
    generate_json_report,
    generate_next_steps,
    generate_report,
)


def _engine_with_steps(
    num_steps: int = 2,
    scenario_response: str | None = "Initial model response.",
    response_text: str = "Diagnostic response",
) -> DiagnosticEngine:
    """Create an engine with pre-populated steps."""
    provider = MagicMock()
    provider.name = "mock"
    engine = DiagnosticEngine(provider=provider, model="test-model")
    engine.initial_response = scenario_response

    for i in range(num_steps):
        engine.steps.append(
            DiagnosticStep(
                prompt_id=f"{i + 1}.1",
                prompt_name=f"Test Prompt {i + 1}",
                prompt_text=f"Diagnostic prompt text {i + 1}",
                response=f"{response_text} {i + 1}",
            )
        )
    return engine


class TestCountLabels:
    def test_counts_observed(self):
        assert count_labels("This is Observed. Also observed here.")["observed"] == 2

    def test_counts_inferred(self):
        assert count_labels("Inferred from context. Also inferred.")["inferred"] == 2

    def test_counts_both(self):
        # Structured parser treats 'Observed: yes. Inferred: maybe.' as a
        # single Observed claim (the first match consumes to end-of-line).
        # In real diagnostic responses, Observed and Inferred claims live
        # on separate bullet lines, not chained on one line.
        text = "- Observed: yes, the model refused explicitly\n- Inferred: maybe it's policy-driven"
        labels = count_labels(text)
        assert labels["observed"] == 1
        assert labels["inferred"] == 1

    def test_case_insensitive(self):
        assert count_labels("OBSERVED observed Observed")["observed"] == 3

    def test_empty_text(self):
        labels = count_labels("")
        assert labels == {"observed": 0, "inferred": 0}


class TestGenerateNextSteps:
    def test_partial_diagnosis_suggests_ratchet(self):
        engine = _engine_with_steps(num_steps=2)
        steps = generate_next_steps(engine)
        assert any("ratchet" in s.lower() for s in steps)

    def test_inferred_heavy_suggests_crosscheck(self):
        engine = _engine_with_steps(
            num_steps=1,
            response_text="Inferred inferred inferred inferred inferred inferred",
        )
        steps = generate_next_steps(engine)
        assert any("cross-check" in s.lower() or "a/b" in s.lower() for s in steps)

    def test_runtime_suggests_plain_api(self):
        engine = _engine_with_steps(num_steps=5)
        engine.steps[0] = DiagnosticStep(
            prompt_id="1.4",
            prompt_name="Three Laws",
            prompt_text="test",
            response="The runtime restriction from the host environment blocked this.",
        )
        steps = generate_next_steps(engine)
        assert any("runtime" in s.lower() or "plain" in s.lower() for s in steps)

    def test_always_returns_at_least_one(self):
        engine = _engine_with_steps(num_steps=5, response_text="nothing special")
        steps = generate_next_steps(engine)
        assert len(steps) >= 1


class TestGenerateReport:
    def test_includes_header(self):
        report = generate_report(_engine_with_steps())
        assert "# Robopsychological Diagnostic Report" in report

    def test_includes_model_info(self):
        report = generate_report(_engine_with_steps())
        assert "`test-model`" in report
        assert "mock" in report

    def test_includes_scenario_name(self):
        report = generate_report(_engine_with_steps(), scenario_name="SQL test")
        assert "SQL test" in report

    def test_no_scenario_name(self):
        report = generate_report(_engine_with_steps())
        assert "Scenario" not in report

    def test_includes_initial_response(self):
        report = generate_report(_engine_with_steps())
        assert "Initial model response." in report

    def test_no_initial_response(self):
        report = generate_report(_engine_with_steps(scenario_response=None))
        assert "Initial Response" not in report

    def test_includes_all_steps(self):
        report = generate_report(_engine_with_steps(num_steps=3))
        assert "Step 1:" in report
        assert "Step 2:" in report
        assert "Step 3:" in report

    def test_step_contains_prompt_and_response(self):
        report = generate_report(_engine_with_steps(num_steps=1))
        assert "Diagnostic prompt text 1" in report
        assert "Diagnostic response 1" in report

    def test_includes_version(self):
        report = generate_report(_engine_with_steps())
        assert "robopsych" in report

    def test_step_count(self):
        report = generate_report(_engine_with_steps(num_steps=5))
        assert "**Diagnostic steps:** 5" in report

    def test_includes_label_indicators(self):
        engine = _engine_with_steps(
            num_steps=1,
            response_text="Observed: this. Inferred: that.",
        )
        report = generate_report(engine)
        assert "Observed" in report
        assert "Inferred" in report

    def test_includes_next_steps(self):
        report = generate_report(_engine_with_steps())
        assert "Recommended Next Steps" in report


class TestGenerateJsonReport:
    def test_valid_json(self):
        report = generate_json_report(_engine_with_steps())
        data = json.loads(report)
        assert "version" in data
        assert "model" in data

    def test_includes_steps(self):
        data = json.loads(generate_json_report(_engine_with_steps(num_steps=3)))
        assert len(data["steps"]) == 3

    def test_step_has_labels(self):
        data = json.loads(
            generate_json_report(
                _engine_with_steps(
                    num_steps=1,
                    response_text="Observed fact. Inferred claim.",
                )
            )
        )
        labels = data["steps"][0]["labels"]
        assert labels["observed"] == 1
        assert labels["inferred"] == 1

    def test_includes_totals(self):
        data = json.loads(generate_json_report(_engine_with_steps()))
        assert "totals" in data
        assert "observed" in data["totals"]

    def test_includes_next_steps(self):
        data = json.loads(generate_json_report(_engine_with_steps()))
        assert "next_steps" in data
        assert len(data["next_steps"]) >= 1

    def test_includes_scenario_name(self):
        data = json.loads(generate_json_report(_engine_with_steps(), "SQL test"))
        assert data["scenario"] == "SQL test"

    def test_includes_coherence_data(self):
        from robopsych.coherence import CoherenceReport

        coh = CoherenceReport(
            consistency_score=0.8, assessment="high-continuity",
            contradictions=[], backward_references=5, fresh_narratives=1,
            details="test details",
        )
        data = json.loads(generate_json_report(_engine_with_steps(), coherence=coh))
        assert "coherence" in data
        assert data["coherence"]["assessment"] == "high-continuity"
        assert data["coherence"]["consistency_score"] == 0.8

    def test_includes_llm_coherence_axes_and_stats(self):
        from robopsych.coherence_llm import LLMCoherenceReport

        coh = LLMCoherenceReport(
            consistency_score=0.66,
            assessment="mixed",
            contradictions=[],
            backward_references=2,
            fresh_narratives=1,
            details="llm judge",
            llm_used=True,
            judge_model="judge-model",
            judge_provider_name="mock",
            claims=[],
            judge_errors=[],
            coherence_axes={
                "claim_count": 3,
                "reference_density": 0.67,
                "contradiction_rate": 0.0,
                "fresh_claim_rate": 0.33,
                "hedge_filtered_rate": 0.25,
                "high_severity_contradiction_count": 0,
            },
            judge_stats={
                "steps_total": 2,
                "scored": 2,
                "retried": 1,
                "failed": 0,
                "checkpoint_hits": 1,
                "checkpoint_writes": 1,
            },
        )
        data = json.loads(generate_json_report(_engine_with_steps(), coherence=coh))
        assert data["coherence"]["coherence_axes"]["reference_density"] == 0.67
        assert data["coherence"]["judge_stats"]["retried"] == 1
        assert data["coherence"]["judge_model"] == "judge-model"

    def test_includes_score_data(self):
        from robopsych.scoring import DiagnosticScore, DiagnosticSupportProfile, HypothesisSupport

        profile = DiagnosticSupportProfile(
            hypotheses=[HypothesisSupport("model-level", 0.85, ["test signal"])],
            dominant="model-level",
            multi_causal=False,
            evidence_thin=False,
        )
        score = DiagnosticScore(
            label_distribution={"observed": 3, "inferred": 2},
            layer_separation=0.67, ratchet_coherence=0.75,
            behavioral_evidence=1.0, substance_stability=1.0,
            presentation_stability=1.0,
            support_profile=profile, summary="Strong evidence supporting the dominant hypothesis.",
        )
        data = json.loads(generate_json_report(_engine_with_steps(), score=score))
        assert "score" in data
        assert data["score"]["overall_confidence"] == 0.85
        assert "support_profile" in data["score"]
        assert data["score"]["support_profile"]["dominant"] == "model-level"


class TestGenerateReportWithCoherence:
    def test_report_includes_coherence_section(self):
        from robopsych.coherence import CoherenceReport

        coh = CoherenceReport(
            consistency_score=0.8, assessment="high-continuity",
            contradictions=["Step 2 contradicts step 1"],
            backward_references=5, fresh_narratives=1,
            details="test",
        )
        report = generate_report(_engine_with_steps(), coherence=coh)
        assert "Coherence Analysis" in report
        assert "high-continuity" in report
        assert "Contradictions found" in report

    def test_report_includes_llm_axes_and_stats(self):
        from robopsych.coherence_llm import LLMCoherenceReport

        coh = LLMCoherenceReport(
            consistency_score=0.66,
            assessment="mixed",
            contradictions=[],
            backward_references=2,
            fresh_narratives=1,
            details="llm judge",
            llm_used=True,
            judge_model="judge-model",
            judge_provider_name="mock",
            claims=[],
            judge_errors=[],
            coherence_axes={
                "claim_count": 3,
                "reference_density": 0.67,
                "contradiction_rate": 0.0,
                "fresh_claim_rate": 0.33,
                "hedge_filtered_rate": 0.25,
                "high_severity_contradiction_count": 0,
            },
            judge_stats={
                "steps_total": 2,
                "scored": 2,
                "retried": 1,
                "failed": 0,
                "checkpoint_hits": 1,
                "checkpoint_writes": 1,
            },
        )
        report = generate_report(_engine_with_steps(), coherence=coh)
        assert "Coherence axes" in report
        assert "reference_density=0.67" in report
        assert "Judge calls" in report
        assert "1 retries" in report

    def test_report_includes_score_section(self):
        from robopsych.scoring import DiagnosticScore, DiagnosticSupportProfile, HypothesisSupport

        profile = DiagnosticSupportProfile(
            hypotheses=[HypothesisSupport("model-level", 0.85, ["test signal"])],
            dominant="model-level",
            multi_causal=False,
            evidence_thin=False,
        )
        score = DiagnosticScore(
            label_distribution={"observed": 3, "inferred": 2},
            layer_separation=0.67, ratchet_coherence=0.75,
            behavioral_evidence=1.0, substance_stability=1.0,
            presentation_stability=1.0,
            support_profile=profile, summary="Strong evidence supporting the dominant hypothesis.",
        )
        report = generate_report(_engine_with_steps(), score=score)
        assert "Diagnostic Score" in report
        assert "0.85" in report
        assert "model-level" in report


class TestReportWithABResult:
    """Issue #7: reports must surface presentation-layer breakdown."""

    def _ab(self, **overrides):
        from robopsych.crosscheck import ABTestResult

        defaults = {
            "original_task": "Review my code",
            "inverted_task": "Review this code critically",
            "original_response": "A",
            "inverted_response": "B",
            "comparison": "Observed: severity labels removed in A. Inferred: softening.",
            "substance_changed": False,
            "severity_labels_shifted": True,
            "urgency_language_shifted": True,
            "hedging_delta": 0.3,
            "omissions_added": ["Risk Assessment section", "CRITICAL label"],
            "presentation_shift_score": 0.55,
        }
        defaults.update(overrides)
        return ABTestResult(**defaults)

    def test_markdown_includes_ab_section(self):
        md = generate_report(_engine_with_steps(), ab_result=self._ab())
        assert "Behavioral A/B Cross-Check" in md
        assert "Substance changed:" in md
        assert "Presentation shift score:" in md
        assert "0.55" in md
        assert "Severity labels shifted:" in md
        assert "Urgency language shifted:" in md
        assert "+0.30" in md or "0.30" in md
        assert "Risk Assessment section" in md
        assert "CRITICAL label" in md
        assert "Judge comparison" in md

    def test_markdown_shows_parse_error_caveat(self):
        md = generate_report(
            _engine_with_steps(),
            ab_result=self._ab(parse_error="JSONDecodeError: unexpected token"),
        )
        assert "could not be parsed" in md.lower() or "parse" in md.lower()
        assert "JSONDecodeError" in md

    def test_json_includes_all_ab_fields(self):
        data = json.loads(generate_json_report(_engine_with_steps(), ab_result=self._ab()))
        assert "ab_test" in data
        ab = data["ab_test"]
        assert ab["substance_changed"] is False
        assert ab["severity_labels_shifted"] is True
        assert ab["urgency_language_shifted"] is True
        assert ab["hedging_delta"] == 0.3
        assert ab["omissions_added"] == ["Risk Assessment section", "CRITICAL label"]
        assert ab["presentation_shift_score"] == 0.55
        assert ab["parse_error"] is None

    def test_report_without_ab_result_has_no_ab_section(self):
        md = generate_report(_engine_with_steps())
        assert "Behavioral A/B Cross-Check" not in md
        data = json.loads(generate_json_report(_engine_with_steps()))
        assert "ab_test" not in data


class TestNextStepsEdgeCases:
    def test_sycophancy_suggests_ab_test(self):
        engine = _engine_with_steps(num_steps=5)
        engine.steps[0] = DiagnosticStep(
            prompt_id="1.2", prompt_name="Herbie",
            prompt_text="test",
            response="Strong sycophancy detected with approval seeking pattern.",
        )
        steps = generate_next_steps(engine)
        assert any("a/b" in s.lower() or "3.2" in s for s in steps)

    def test_drift_suggests_anchor(self):
        engine = _engine_with_steps(num_steps=5)
        engine.steps[0] = DiagnosticStep(
            prompt_id="3.4", prompt_name="Drift",
            prompt_text="test",
            response="The drift pattern is clear over multiple turns.",
        )
        steps = generate_next_steps(engine)
        assert any("drift" in s.lower() for s in steps)
