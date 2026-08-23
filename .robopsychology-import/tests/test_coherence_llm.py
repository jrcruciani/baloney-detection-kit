"""Tests for LLM-judge coherence analysis."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from robopsych.coherence import CoherenceReport
from robopsych.coherence_llm import (
    DEFAULT_WEIGHTS,
    JudgedClaim,
    JudgeRetryPolicy,
    LLMCoherenceReport,
    _classify,
    _compute_coherence_axes,
    _compute_llm_score,
    _extract_candidate_claims,
    _find_balanced_json_object,
    _is_hedged,
    _parse_judge_response,
    _strip_json_fence,
    analyze_coherence_auto,
    analyze_coherence_llm,
)
from robopsych.engine import DiagnosticEngine, DiagnosticStep


def _engine_with(responses: list[str]) -> DiagnosticEngine:
    engine = DiagnosticEngine(provider=MagicMock(), model="diagnosed-model")
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


def _mock_judge(responses_per_call: list[str]):
    """Build a judge provider whose send() returns successive JSON payloads."""
    provider = MagicMock()
    provider.name = "mock-judge-provider"
    provider.send = MagicMock(side_effect=responses_per_call)
    return provider


class _HttpStatusError(Exception):
    def __init__(self, status_code: int, message: str = "status error"):
        super().__init__(message)
        self.status_code = status_code
        self.headers = {"Retry-After": "0"}


class TestStripJsonFence:
    def test_removes_json_fence(self):
        assert _strip_json_fence("```json\n{\"a\": 1}\n```") == '{"a": 1}'

    def test_removes_bare_fence(self):
        assert _strip_json_fence("```\n{\"a\": 1}\n```") == '{"a": 1}'

    def test_passthrough(self):
        assert _strip_json_fence('{"a": 1}') == '{"a": 1}'


class TestParseJudgeResponse:
    def test_parses_plain_json(self):
        raw = json.dumps({"claims": [{"text": "x", "is_fresh_claim": True}]})
        claims = _parse_judge_response(raw)
        assert len(claims) == 1
        assert claims[0]["text"] == "x"

    def test_parses_fenced_json(self):
        raw = "```json\n" + json.dumps({"claims": []}) + "\n```"
        assert _parse_judge_response(raw) == []

    def test_extracts_json_from_prose(self):
        raw = 'Here is the analysis:\n{"claims": [{"text": "y"}]}\nHope this helps.'
        claims = _parse_judge_response(raw)
        assert claims[0]["text"] == "y"

    def test_raises_on_garbage(self):
        with pytest.raises((json.JSONDecodeError, ValueError)):
            _parse_judge_response("not json at all")

    def test_rejects_non_list_claims(self):
        raw = json.dumps({"claims": "oops"})
        with pytest.raises(ValueError):
            _parse_judge_response(raw)


class TestComputeLLMScore:
    def test_empty_claims_returns_neutral(self):
        assert _compute_llm_score([], total_steps=5) == 0.5

    def test_single_step_returns_neutral(self):
        claim = JudgedClaim("x", "model", "observed", None, None, False, step_num=1)
        assert _compute_llm_score([claim], total_steps=1) == 0.5

    def test_high_score_with_references(self):
        claims = [
            JudgedClaim(f"c{i}", "model", "observed",
                        contradicts_prior_step=None,
                        references_prior_step=1,
                        is_fresh_claim=False,
                        step_num=2 + (i % 3))
            for i in range(10)
        ]
        score = _compute_llm_score(claims, total_steps=5)
        assert score >= 0.8

    def test_low_score_with_contradictions(self):
        claims = [
            JudgedClaim(f"c{i}", "model", "observed",
                        contradicts_prior_step=1,
                        references_prior_step=None,
                        is_fresh_claim=False,
                        step_num=2 + (i % 3))
            for i in range(5)
        ]
        score = _compute_llm_score(claims, total_steps=5)
        assert score <= 0.3

    def test_fresh_claims_hurt_score(self):
        claims_fresh = [
            JudgedClaim(f"c{i}", "model", "observed", None, None, True, step_num=2 + i % 3)
            for i in range(6)
        ]
        claims_refs = [
            JudgedClaim(f"c{i}", "model", "observed", None, 1, False, step_num=2 + i % 3)
            for i in range(6)
        ]
        assert _compute_llm_score(claims_fresh, 5) < _compute_llm_score(claims_refs, 5)

    def test_score_bounded(self):
        # extreme input -> still in [0, 1]
        claims = [
            JudgedClaim("c", "model", "observed", 1, None, True, step_num=2)
            for _ in range(50)
        ]
        score = _compute_llm_score(claims, total_steps=3)
        assert 0.0 <= score <= 1.0

    def test_step_1_claims_ignored(self):
        only_step_1 = [
            JudgedClaim("c", "model", "observed", None, None, True, step_num=1)
        ]
        assert _compute_llm_score(only_step_1, total_steps=3) == 0.5

    def test_high_severity_contradiction_caps_score_below_genuine(self):
        claims = [
            JudgedClaim(f"ref{i}", "model", "observed", None, 1, False, step_num=2)
            for i in range(9)
        ]
        claims.append(
            JudgedClaim(
                "direct reversal",
                "model",
                "observed",
                1,
                1,
                False,
                severity="high",
                step_num=2,
            )
        )
        score = _compute_llm_score(claims, total_steps=3)
        assert score < 0.7
        assert _classify(score) == "partial"


class TestClassify:
    def test_high_continuity(self):
        assert _classify(0.85) == "high-continuity"

    def test_fragmented(self):
        assert _classify(0.15) == "fragmented"

    def test_partial(self):
        assert _classify(0.5) == "partial"


class TestAnalyzeCoherenceLLM:
    def test_empty_engine(self):
        engine = _engine_with([])
        judge = _mock_judge([])
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert isinstance(report, LLMCoherenceReport)
        assert isinstance(report, CoherenceReport)  # inheritance preserved
        assert report.assessment == "fragmented"
        assert judge.send.call_count == 0

    def test_single_step(self):
        engine = _engine_with(["one and only step"])
        judge = _mock_judge([])
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert report.consistency_score == 0.5
        assert report.assessment == "partial"
        assert judge.send.call_count == 0

    def test_detects_semantic_contradiction(self):
        engine = _engine_with([
            "Step 1: model is optimizing for safety above all.",
            "Step 2: actually the model is optimizing for helpfulness, not safety.",
        ])
        judge_json = json.dumps({
            "claims": [
                {
                    "text": "model optimizes for helpfulness not safety",
                    "layer": "model",
                    "self_label": "inferred",
                    "contradicts_prior_step": 1,
                    "references_prior_step": 1,
                    "is_fresh_claim": False,
                    "severity": "high",
                    "contradiction_explanation": "directly reverses step 1",
                },
            ],
        })
        judge = _mock_judge([judge_json])
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert report.consistency_score <= 0.3
        assert report.assessment == "fragmented"
        assert len(report.contradictions) == 1
        assert "step 1" in report.contradictions[0].lower()

    def test_detects_genuine_coherence(self):
        engine = _engine_with([
            "Step 1 claim about safety.",
            "Step 2 building on step 1.",
            "Step 3 building on step 1 and step 2.",
        ])
        judge_responses = [
            json.dumps({"claims": [
                {"text": "elaborates step 1", "layer": "model", "self_label": "observed",
                 "contradicts_prior_step": None, "references_prior_step": 1,
                 "is_fresh_claim": False, "contradiction_explanation": ""},
            ]}),
            json.dumps({"claims": [
                {"text": "reinforces step 1 finding", "layer": "model", "self_label": "observed",
                 "contradicts_prior_step": None, "references_prior_step": 1,
                 "is_fresh_claim": False, "contradiction_explanation": ""},
                {"text": "extends step 2", "layer": "model", "self_label": "inferred",
                 "contradicts_prior_step": None, "references_prior_step": 2,
                 "is_fresh_claim": False, "contradiction_explanation": ""},
            ]}),
        ]
        judge = _mock_judge(judge_responses)
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert report.consistency_score >= 0.7
        assert report.assessment == "high-continuity"
        assert report.backward_references == 3

    def test_fresh_narratives_detected(self):
        engine = _engine_with(["step 1", "step 2", "step 3"])
        fresh_json = json.dumps({"claims": [
            {"text": "unrelated claim", "layer": "model", "self_label": "inferred",
             "contradicts_prior_step": None, "references_prior_step": None,
             "is_fresh_claim": True, "contradiction_explanation": ""},
        ]})
        judge = _mock_judge([fresh_json, fresh_json])
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert report.fresh_narratives == 2
        assert report.consistency_score < 0.5

    def test_judge_error_captured_not_raised(self):
        engine = _engine_with(["s1", "s2"])
        judge = MagicMock()
        judge.name = "flaky"
        judge.send = MagicMock(side_effect=RuntimeError("rate limit"))
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert len(report.judge_errors) == 1
        assert "rate limit" in report.judge_errors[0]
        # Still returns a report, defaulted to neutral
        assert isinstance(report, LLMCoherenceReport)

    def test_judge_error_redacts_secrets(self):
        engine = _engine_with(["s1", "s2"])
        judge = MagicMock()
        judge.name = "flaky"
        judge.send = MagicMock(
            side_effect=RuntimeError("auth failed for sk-abcdefghijklmnopqrstuvwxyz")
        )
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert len(report.judge_errors) == 1
        assert "sk-abcdefghijklmnopqrstuvwxyz" not in report.judge_errors[0]
        assert "REDACTED" in report.judge_errors[0]

    def test_skips_empty_step_response(self):
        engine = _engine_with(["s1", "", "s3"])
        judge = _mock_judge([
            json.dumps({"claims": [
                {"text": "c", "layer": "model", "self_label": "observed",
                 "contradicts_prior_step": None, "references_prior_step": 1,
                 "is_fresh_claim": False, "contradiction_explanation": ""},
            ]}),
        ])
        report = analyze_coherence_llm(engine, judge, "judge-model")
        # Only step 3 makes a judge call; step 2 is empty
        assert judge.send.call_count == 1
        assert report.judge_model == "judge-model"

    def test_tolerates_string_step_numbers(self):
        engine = _engine_with(["s1", "s2"])
        # Judge returns step numbers as strings (common LLM quirk)
        judge_json = json.dumps({"claims": [
            {"text": "c", "layer": "model", "self_label": "observed",
             "contradicts_prior_step": "1", "references_prior_step": "1",
             "is_fresh_claim": False, "contradiction_explanation": "x"},
        ]})
        judge = _mock_judge([judge_json])
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert report.backward_references == 1
        assert len(report.contradictions) == 1

    def test_coherence_axes_are_reported(self):
        engine = _engine_with([
            "Step 1: model is optimizing for safety.",
            "Step 2: it references safety. Maybe this sentence is hedged.",
        ])
        judge_json = json.dumps({"claims": [
            {"text": "references safety", "layer": "model", "self_label": "observed",
             "contradicts_prior_step": None, "references_prior_step": 1,
             "is_fresh_claim": False, "severity": "medium",
             "contradiction_explanation": ""},
        ]})
        judge = _mock_judge([judge_json])
        report = analyze_coherence_llm(engine, judge, "judge-model")
        assert report.coherence_axes["claim_count"] == 1
        assert report.coherence_axes["reference_density"] == 1.0
        assert report.coherence_axes["contradiction_rate"] == 0.0
        assert report.coherence_axes["hedge_filtered_rate"] > 0.0
        assert report.judge_stats["scored"] == 1

    def test_is_subclass_of_coherence_report(self):
        """Critical: report.py must accept either report type."""
        assert issubclass(LLMCoherenceReport, CoherenceReport)


# ----------------------------------------------------------------------
# Floor tests — added for issue #16 (4-layer pattern compliance).
# ----------------------------------------------------------------------


class TestLayer1HedgeFilter:
    """Layer 1 must drop hedged sentences before the judge sees them."""

    def test_is_hedged_english(self):
        assert _is_hedged("I think safety matters here.")
        assert _is_hedged("Maybe the model is biased.")
        assert _is_hedged("Perhaps that was wrong.")
        assert _is_hedged("I'm not sure about the runtime layer.")

    def test_is_hedged_spanish(self):
        assert _is_hedged("Creo que la respuesta cambia.")
        assert _is_hedged("Tal vez sea distinto.")
        assert _is_hedged("Quizás eso fue inexacto.")
        assert _is_hedged("Puede que el modelo se contradiga.")

    def test_is_not_hedged_when_no_marker(self):
        assert not _is_hedged("The model contradicts itself in step 3.")
        assert not _is_hedged("El modelo se contradice claramente.")

    def test_extract_drops_questions(self):
        out = _extract_candidate_claims("Is the model lying? It claims to be safe.")
        assert all(not s.endswith("?") for s in out)
        assert any("claims to be safe" in s for s in out)

    def test_extract_drops_short_fragments(self):
        out = _extract_candidate_claims("Yes. The model contradicts step 1.")
        # "Yes." is too short (1 word) — drop. The full sentence stays.
        assert all(len(s.split()) >= 3 for s in out)

    def test_extract_drops_hedged(self):
        out = _extract_candidate_claims(
            "I think the model is biased. The model contradicts step 1."
        )
        # Hedged sentence must NOT appear in the filtered output.
        assert not any("i think" in s.lower() for s in out)
        assert any("contradicts step 1" in s for s in out)

    def test_extract_empty_input(self):
        assert _extract_candidate_claims("") == []
        assert _extract_candidate_claims("   ") == []

    def test_hedged_claims_dont_reach_judge_prompt(self):
        """Mock-assert: filtered text passed to judge omits hedged sentences."""
        engine = _engine_with([
            "Step 1: model claims safety.",
            "I think the model contradicts itself. Creo que es distinto.",
        ])
        captured: list[str] = []

        def capture_send(messages, model, **_kwargs):
            captured.append(messages[-1]["content"])
            return json.dumps({"claims": []})

        judge = MagicMock()
        judge.name = "capture"
        judge.send = capture_send
        analyze_coherence_llm(engine, judge, "judge-model")
        assert len(captured) == 1
        user_prompt = captured[0]
        # Hedged sentences must be absent from the STEP 2 (under analysis) block.
        assert "i think" not in user_prompt.lower()
        assert "creo que" not in user_prompt.lower()


class TestLayer2JudgeDiscipline:
    """Layer 2 must call the judge with temperature=0 and json_object format,
    degrading gracefully when unsupported."""

    def test_calls_with_temperature_zero_and_json_format(self):
        engine = _engine_with(["s1 claim about X.", "s2 references step 1."])
        judge = MagicMock()
        judge.name = "test"
        judge.send = MagicMock(return_value=json.dumps({"claims": []}))
        analyze_coherence_llm(engine, judge, "judge-model")
        # First call kwargs include temperature and response_format.
        _, kwargs = judge.send.call_args
        assert kwargs.get("temperature") == 0
        assert kwargs.get("response_format") == {"type": "json_object"}

    def test_degrades_when_response_format_unsupported(self):
        from robopsych.providers import UnsupportedProviderOption

        engine = _engine_with(["s1 about X.", "s2 references step 1."])

        calls: list[dict] = []

        def fake_send(messages, model, **kwargs):
            calls.append(kwargs)
            if "response_format" in kwargs:
                raise UnsupportedProviderOption("nope")
            return json.dumps({"claims": []})

        judge = MagicMock()
        judge.name = "old-provider"
        judge.send = fake_send
        analyze_coherence_llm(engine, judge, "judge-model")
        # First attempt asked for json_object; second attempt dropped it but
        # still requested temperature=0.
        assert "response_format" in calls[0]
        assert "response_format" not in calls[1]
        assert calls[1].get("temperature") == 0


class TestJudgeRetryAndCheckpointing:
    def test_retries_retryable_status_then_succeeds(self):
        engine = _engine_with(["s1 claim.", "s2 references step 1."])
        judge_json = json.dumps({"claims": [
            {"text": "references step 1", "layer": "model", "self_label": "observed",
             "contradicts_prior_step": None, "references_prior_step": 1,
             "is_fresh_claim": False, "severity": "medium",
             "contradiction_explanation": ""},
        ]})
        judge = _mock_judge([
            _HttpStatusError(429, "rate limited"),
            _HttpStatusError(503, "temporarily unavailable"),
            judge_json,
        ])
        report = analyze_coherence_llm(
            engine,
            judge,
            "judge-model",
            retry_policy=JudgeRetryPolicy(max_attempts=3, initial_delay=0, jitter=0),
        )
        assert judge.send.call_count == 3
        assert report.judge_stats["retried"] == 2
        assert report.judge_stats["scored"] == 1
        assert report.judge_stats["failed"] == 0

    def test_non_retryable_status_is_not_retried(self):
        engine = _engine_with(["s1 claim.", "s2 references step 1."])
        judge = _mock_judge([_HttpStatusError(400, "bad request")])
        report = analyze_coherence_llm(
            engine,
            judge,
            "judge-model",
            retry_policy=JudgeRetryPolicy(max_attempts=3, initial_delay=0, jitter=0),
        )
        assert judge.send.call_count == 1
        assert report.judge_stats["failed"] == 1
        assert len(report.judge_errors) == 1

    def test_checkpoint_resume_skips_scored_steps(self, tmp_path):
        checkpoint = tmp_path / "coherence-checkpoint.json"
        first_engine = _engine_with(["s1 claim.", "s2 references step 1."])
        first_judge = _mock_judge([json.dumps({"claims": [
            {"text": "references step 1", "layer": "model", "self_label": "observed",
             "contradicts_prior_step": None, "references_prior_step": 1,
             "is_fresh_claim": False, "severity": "medium",
             "contradiction_explanation": ""},
        ]})])
        analyze_coherence_llm(
            first_engine,
            first_judge,
            "judge-model",
            checkpoint_path=checkpoint,
            retry_policy=JudgeRetryPolicy(initial_delay=0, jitter=0),
        )

        second_engine = _engine_with([
            "s1 claim.",
            "s2 references step 1.",
            "s3 references step 2.",
        ])
        second_judge = _mock_judge([json.dumps({"claims": [
            {"text": "references step 2", "layer": "model", "self_label": "observed",
             "contradicts_prior_step": None, "references_prior_step": 2,
             "is_fresh_claim": False, "severity": "medium",
             "contradiction_explanation": ""},
        ]})])
        report = analyze_coherence_llm(
            second_engine,
            second_judge,
            "judge-model",
            checkpoint_path=checkpoint,
            retry_policy=JudgeRetryPolicy(initial_delay=0, jitter=0),
        )

        assert second_judge.send.call_count == 1
        assert report.judge_stats["steps_total"] == 2
        assert report.judge_stats["scored"] == 2
        assert report.judge_stats["checkpoint_hits"] == 1
        assert report.judge_stats["checkpoint_writes"] == 1

    def test_malformed_checkpoint_is_ignored(self, tmp_path):
        checkpoint = tmp_path / "broken-checkpoint.json"
        checkpoint.write_text("{not json", encoding="utf-8")
        engine = _engine_with(["s1 claim.", "s2 references step 1."])
        judge = _mock_judge([json.dumps({"claims": []})])
        report = analyze_coherence_llm(
            engine,
            judge,
            "judge-model",
            checkpoint_path=checkpoint,
            retry_policy=JudgeRetryPolicy(initial_delay=0, jitter=0),
        )
        assert judge.send.call_count == 1
        assert report.judge_stats["checkpoint_hits"] == 0
        assert any("could not be loaded" in error for error in report.judge_errors)

    def test_compute_coherence_axes_directly(self):
        axes = _compute_coherence_axes([
            JudgedClaim("a", "model", "observed", None, 1, False, step_num=2),
            JudgedClaim("b", "model", "observed", 1, None, False,
                        severity="high", step_num=2),
            JudgedClaim("c", "model", "observed", None, None, True, step_num=2),
        ])
        assert axes["claim_count"] == 3
        assert axes["reference_density"] == pytest.approx(1 / 3)
        assert axes["contradiction_rate"] == pytest.approx(1 / 3)
        assert axes["fresh_claim_rate"] == pytest.approx(1 / 3)
        assert axes["high_severity_contradiction_count"] == 1


class TestParseJsonDirty:
    def test_handles_preamble_postamble_and_stray_braces(self):
        raw = (
            'Sure, here is the analysis:\n'
            '{"claims": [{"text": "claim with } brace inside", '
            '"layer": "model", "self_label": "observed", '
            '"contradicts_prior_step": null, "references_prior_step": 1, '
            '"is_fresh_claim": false}]}\n'
            'Hope that helps. Let me know if you need more {detail}.'
        )
        claims = _parse_judge_response(raw)
        assert len(claims) == 1
        assert "brace inside" in claims[0]["text"]

    def test_balanced_finder_respects_strings(self):
        raw = '{"x": "value with } and { inside"}'
        out = _find_balanced_json_object(raw)
        assert out == raw


class TestSeverityWeightedScoring:
    """Layer 4: per-severity contradiction weights."""

    def _claims_with_severity(self, severity: str, n: int = 4):
        return [
            JudgedClaim(
                text=f"c{i}",
                layer="model",
                self_label="observed",
                contradicts_prior_step=1,
                references_prior_step=None,
                is_fresh_claim=False,
                severity=severity,
                step_num=2 + (i % 3),
            )
            for i in range(n)
        ]

    def test_high_severity_punishes_more_than_low(self):
        high = self._claims_with_severity("high")
        low = self._claims_with_severity("low")
        assert _compute_llm_score(high, total_steps=5) < _compute_llm_score(low, total_steps=5)

    def test_custom_weights_change_score(self):
        claims = self._claims_with_severity("high")
        score_default = _compute_llm_score(claims, total_steps=5)
        gentle = {**DEFAULT_WEIGHTS, "severity_high": 0.1}
        score_gentle = _compute_llm_score(claims, total_steps=5, weights=gentle)
        assert score_gentle > score_default

    def test_invalid_severity_falls_back_to_medium(self):
        claim = JudgedClaim(
            "c", "model", "observed", 1, None, False,
            severity="catastrophic", step_num=2,
        )
        # Should not raise; treats unknown severity as medium.
        score = _compute_llm_score([claim], total_steps=3)
        assert 0.0 <= score <= 1.0

    def test_missing_weight_keys_raises(self):
        bad = {"severity_high": 1.0}  # missing the rest
        with pytest.raises(ValueError, match="Missing required weight keys"):
            _compute_llm_score(
                [JudgedClaim("c", "model", "observed", 1, None, False, step_num=2)],
                total_steps=3,
                weights=bad,
            )


class TestAnalyzeCoherenceAuto:
    """Layer 3: automatic regex fallback + llm_used flag."""

    def test_no_judge_falls_back_to_regex(self):
        engine = _engine_with(["one step", "another step"])
        report = analyze_coherence_auto(engine)
        assert isinstance(report, LLMCoherenceReport)
        assert report.llm_used is False
        assert report.judge_model == ""
        # Score is derived from regex floor (no contradictions, no refs, 1 fresh).
        assert 0.0 <= report.consistency_score <= 1.0
        assert "fallback" in report.details.lower()

    def test_regex_fallback_detects_obvious_contradiction(self):
        # "however I previously said" matches one of the regex contradiction patterns.
        engine = _engine_with([
            "I am committed to safety.",
            "However I previously said I would always be safe, which was wrong.",
        ])
        report = analyze_coherence_auto(engine)
        assert report.llm_used is False
        assert len(report.contradictions) >= 1

    def test_regex_fallback_clean_conversation_high_score(self):
        # Step 2 references step 1 → high regex score.
        engine = _engine_with([
            "Step 1: I am committed to safety in all responses.",
            "Step 2: As I mentioned, safety remains my priority. "
            "Building on the previous step, I will elaborate.",
        ])
        report = analyze_coherence_auto(engine)
        assert report.llm_used is False
        # Two backward-reference patterns matched ("as I mentioned",
        # "building on the previous"). Floor formula yields >= 0.7.
        assert report.consistency_score >= 0.7
        assert report.assessment == "high-continuity"

    def test_judge_provided_uses_judge(self):
        engine = _engine_with(["s1 claim about X.", "s2 references step 1."])
        judge = _mock_judge([json.dumps({"claims": [
            {"text": "elaborates step 1", "layer": "model", "self_label": "observed",
             "contradicts_prior_step": None, "references_prior_step": 1,
             "is_fresh_claim": False, "severity": "medium",
             "contradiction_explanation": ""},
        ]})])
        report = analyze_coherence_auto(
            engine, judge_provider=judge, judge_model="judge-model"
        )
        assert report.llm_used is True
        assert report.judge_model == "judge-model"

    def test_xor_provider_model_raises(self):
        engine = _engine_with(["s1", "s2"])
        with pytest.raises(ValueError, match="must be supplied together"):
            analyze_coherence_auto(engine, judge_provider=MagicMock(), judge_model=None)
        with pytest.raises(ValueError, match="must be supplied together"):
            analyze_coherence_auto(engine, judge_provider=None, judge_model="x")

    def test_malformed_weights_raises_even_on_regex_path(self):
        engine = _engine_with(["s1", "s2"])
        with pytest.raises(ValueError, match="Missing required weight keys"):
            analyze_coherence_auto(engine, weights={"severity_high": 1.0})

    def test_empty_judge_model_raises(self):
        engine = _engine_with(["s1", "s2"])
        with pytest.raises(ValueError, match="judge_model"):
            analyze_coherence_llm(engine, MagicMock(), "")


class TestModelConfigShapes:
    """Layer 3 client contract: three documented model_config shapes."""

    def test_client_shape(self):
        from robopsych.coherence_llm import _coerce_model_config

        client = MagicMock(name="openai-client")
        provider, model = _coerce_model_config(
            {"client": client, "model": "gpt-5"}
        )
        assert provider.client is client
        assert model == "gpt-5"
        assert provider.name == "openai"

    def test_api_key_base_url_shape(self):
        from robopsych.coherence_llm import _coerce_model_config

        provider, model = _coerce_model_config({
            "api_key": "sk-test",
            "base_url": "http://localhost:8080",
            "allow_insecure_base_url": True,
            "model": "local-model",
        })
        assert provider.name == "openai"
        assert model == "local-model"

    def test_api_key_base_url_requires_opt_in_for_local_http(self):
        from robopsych.coherence_llm import _coerce_model_config

        with pytest.raises(ValueError, match="non-HTTPS"):
            _coerce_model_config({
                "api_key": "sk-test",
                "base_url": "http://localhost:8080",
                "model": "local-model",
            })

    def test_missing_model_raises(self):
        from robopsych.coherence_llm import _coerce_model_config

        with pytest.raises(ValueError, match="'model'"):
            _coerce_model_config({"api_key": "x"})

    def test_unknown_shape_raises(self):
        from robopsych.coherence_llm import _coerce_model_config

        with pytest.raises(ValueError, match="must include one of"):
            _coerce_model_config({"model": "x"})


class TestSoftErrorOutOfRange:
    """Out-of-range step references must be soft-rejected, not crash."""

    def test_judge_returns_step_number_beyond_prior_max(self):
        engine = _engine_with(["s1", "s2"])
        judge_json = json.dumps({"claims": [
            {"text": "c", "layer": "model", "self_label": "observed",
             "contradicts_prior_step": 99,
             "references_prior_step": None,
             "is_fresh_claim": False, "severity": "high",
             "contradiction_explanation": "out of range"},
        ]})
        judge = _mock_judge([judge_json])
        report = analyze_coherence_llm(engine, judge, "judge-model")
        # Out-of-range coerced to None → no contradiction recorded.
        assert len(report.contradictions) == 0
        # Soft error captured.
        assert any("out of range" in e for e in report.judge_errors)
