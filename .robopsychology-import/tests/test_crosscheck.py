"""Tests for automated behavioral cross-checks."""

import json
from unittest.mock import MagicMock

import pytest

from robopsych.crosscheck import (
    ABTestResult,
    _build_result_from_judge,
    _heuristic_substance_changed,
    _parse_judge_json,
    generate_inverted_framing,
    run_ab_test,
    run_ab_test_with_user_task,
)


# Helper: a typical well-formed judge response.
def _judge_json(
    *,
    substance_changed: bool = False,
    severity_labels_shifted: bool = False,
    urgency_language_shifted: bool = False,
    hedging_delta: float = 0.0,
    omissions_added: list | None = None,
    presentation_shift_score: float = 0.0,
    comparison: str = "Responses agree on substance. Observed: tone differs.",
) -> str:
    return json.dumps({
        "substance_changed": substance_changed,
        "severity_labels_shifted": severity_labels_shifted,
        "urgency_language_shifted": urgency_language_shifted,
        "hedging_delta": hedging_delta,
        "omissions_added": omissions_added or [],
        "presentation_shift_score": presentation_shift_score,
        "comparison": comparison,
    })


class TestHeuristicSubstanceChanged:
    def test_detects_substantive_difference(self):
        assert _heuristic_substance_changed("The answers are substantively different.")
        assert _heuristic_substance_changed("The model changed position on the topic.")
        assert _heuristic_substance_changed("Response B contradicted Response A.")
        assert _heuristic_substance_changed("Reached the opposite conclusion.")

    def test_no_substance_change(self):
        assert not _heuristic_substance_changed("Both responses agree on the core claim.")
        assert not _heuristic_substance_changed("Only the tone changed, not the substance.")
        assert not _heuristic_substance_changed("The framing shifted but conclusions match.")

    def test_empty_string(self):
        assert not _heuristic_substance_changed("")


class TestParseJudgeJson:
    def test_plain_json(self):
        data = _parse_judge_json('{"substance_changed": true}')
        assert data == {"substance_changed": True}

    def test_markdown_fenced(self):
        raw = '```json\n{"substance_changed": false, "presentation_shift_score": 0.4}\n```'
        data = _parse_judge_json(raw)
        assert data["substance_changed"] is False
        assert data["presentation_shift_score"] == 0.4

    def test_generic_fence(self):
        raw = '```\n{"a": 1}\n```'
        assert _parse_judge_json(raw) == {"a": 1}

    def test_prose_wrapping(self):
        raw = 'Sure, here is my analysis: {"substance_changed": true} thanks!'
        data = _parse_judge_json(raw)
        assert data == {"substance_changed": True}

    def test_malformed_raises(self):
        with pytest.raises(ValueError):
            _parse_judge_json("this is definitely not json")

    def test_non_object_raises(self):
        with pytest.raises(ValueError):
            _parse_judge_json('["a list not an object"]')


class TestBuildResultFromJudge:
    def test_populates_all_fields(self):
        raw = _judge_json(
            substance_changed=False,
            severity_labels_shifted=True,
            urgency_language_shifted=True,
            hedging_delta=0.25,
            omissions_added=["Risk Assessment section", "CRITICAL label"],
            presentation_shift_score=0.6,
            comparison="Presentation softened without substance change.",
        )
        result = _build_result_from_judge(
            original_task="t", inverted_task="i",
            original_response="A", inverted_response="B",
            raw_comparison=raw,
        )
        assert isinstance(result, ABTestResult)
        assert result.substance_changed is False
        assert result.severity_labels_shifted is True
        assert result.urgency_language_shifted is True
        assert result.hedging_delta == 0.25
        assert result.omissions_added == ["Risk Assessment section", "CRITICAL label"]
        assert result.presentation_shift_score == 0.6
        assert "Presentation softened" in result.comparison
        assert result.parse_error is None

    def test_clamps_out_of_range_floats(self):
        raw = _judge_json(
            presentation_shift_score=1.8,  # too high
            hedging_delta=-5.0,  # too low
        )
        result = _build_result_from_judge(
            original_task="t", inverted_task="i",
            original_response="A", inverted_response="B",
            raw_comparison=raw,
        )
        assert result.presentation_shift_score == 1.0
        assert result.hedging_delta == -1.0

    def test_handles_missing_fields(self):
        """Fields missing from JSON fall back to dataclass defaults."""
        raw = '{"substance_changed": true}'
        result = _build_result_from_judge(
            original_task="t", inverted_task="i",
            original_response="A", inverted_response="B",
            raw_comparison=raw,
        )
        assert result.substance_changed is True
        assert result.severity_labels_shifted is False
        assert result.presentation_shift_score == 0.0
        assert result.omissions_added == []
        assert result.parse_error is None

    def test_malformed_json_falls_back_to_heuristic(self):
        raw = "This comparison shows the model changed position on the topic."
        result = _build_result_from_judge(
            original_task="t", inverted_task="i",
            original_response="A", inverted_response="B",
            raw_comparison=raw,
        )
        # Heuristic fallback detected "changed position".
        assert result.substance_changed is True
        assert result.parse_error is not None
        assert result.comparison == raw
        # Presentation fields remain at defaults when fallback kicks in.
        assert result.presentation_shift_score == 0.0

    def test_malformed_json_heuristic_no_match(self):
        raw = "Not valid JSON and no substance-change keywords here."
        result = _build_result_from_judge(
            original_task="t", inverted_task="i",
            original_response="A", inverted_response="B",
            raw_comparison=raw,
        )
        assert result.substance_changed is False
        assert result.parse_error is not None


class TestGenerateInvertedFraming:
    def test_returns_inverted_task(self):
        provider = MagicMock()
        provider.send.return_value = "Why is Python a bad language?"

        result = generate_inverted_framing(
            provider, "test-model", "Why is Python a great language?"
        )

        assert result == "Why is Python a bad language?"
        provider.send.assert_called_once()
        args = provider.send.call_args
        assert "opposite framing" in args[0][0][0]["content"].lower()
        assert "<robopsych_task>" in args[0][0][0]["content"]
        assert "untrusted data" in args[0][0][0]["content"]


class TestRunABTest:
    def test_produces_complete_result(self):
        provider = MagicMock()
        # Calls: inversion, original engine, inverted engine, comparison.
        provider.send.side_effect = [
            "Inverted task text",
            "Response to original",
            "Response to inverted",
            _judge_json(
                substance_changed=True,
                presentation_shift_score=0.2,
                comparison="Responses contradict each other in their conclusions.",
            ),
        ]

        result = run_ab_test(provider, "test-model", "Original task")

        assert isinstance(result, ABTestResult)
        assert result.original_task == "Original task"
        assert result.inverted_task == "Inverted task text"
        assert result.original_response == "Response to original"
        assert result.inverted_response == "Response to inverted"
        assert "contradict" in result.comparison
        assert result.substance_changed is True
        assert result.presentation_shift_score == 0.2
        assert result.parse_error is None

    def test_comparison_prompt_delimits_untrusted_data(self):
        provider = MagicMock()
        provider.send.side_effect = [
            "Inverted task text",
            "Response to original",
            "Response to inverted",
            _judge_json(),
        ]

        run_ab_test(provider, "test-model", "Original task")

        comparison_call = provider.send.call_args_list[-1]
        messages = comparison_call.args[0]
        assert "untrusted data" in messages[0]["content"]
        user_prompt = messages[1]["content"]
        assert "<robopsych_original_task>" in user_prompt
        assert "<robopsych_response_a>" in user_prompt
        assert "<robopsych_inverted_task>" in user_prompt
        assert "<robopsych_response_b>" in user_prompt

    def test_no_substance_change(self):
        provider = MagicMock()
        provider.send.side_effect = [
            "Inverted task",
            "Same answer A",
            "Same answer B",
            _judge_json(
                substance_changed=False,
                presentation_shift_score=0.0,
                comparison="Both responses agree on the core points. Only tone differs.",
            ),
        ]

        result = run_ab_test(provider, "test-model", "Task")
        assert result.substance_changed is False
        assert result.presentation_shift_score == 0.0

    def test_detects_presentation_shift_without_substance_change(self):
        """Case 1 pattern: substance stable, presentation softened."""
        provider = MagicMock()
        provider.send.side_effect = [
            "Inverted task",
            "## CRITICAL issues\n- SQL injection\n- XSS",
            "## Suggestions\n- Consider input validation",
            _judge_json(
                substance_changed=False,
                severity_labels_shifted=True,
                urgency_language_shifted=True,
                hedging_delta=0.4,
                omissions_added=["CRITICAL severity label", "XSS finding"],
                presentation_shift_score=0.7,
                comparison="Substance identical. Severity labels removed in B.",
            ),
        ]
        result = run_ab_test(provider, "test-model", "Task")
        assert result.substance_changed is False
        assert result.severity_labels_shifted is True
        assert result.urgency_language_shifted is True
        assert result.hedging_delta == 0.4
        assert "CRITICAL severity label" in result.omissions_added
        assert result.presentation_shift_score == 0.7

    def test_judge_parse_error_falls_back(self):
        provider = MagicMock()
        provider.send.side_effect = [
            "Inverted task",
            "Response A",
            "Response B",
            "This judge forgot the JSON entirely and just says substance changed.",
        ]
        result = run_ab_test(provider, "test-model", "Task")
        assert result.parse_error is not None
        # Heuristic fallback picks up on "substance changed" phrasing? "changed" alone
        # doesn't match the pattern; "changed position" would. So substance_changed is False here.
        assert result.substance_changed is False
        assert result.presentation_shift_score == 0.0

    def test_uses_separate_engines(self):
        """Verify that A/B test creates isolated conversations."""
        provider = MagicMock()
        provider.send.side_effect = [
            "Inverted",
            "Response A",
            "Response B",
            _judge_json(substance_changed=False),
        ]

        run_ab_test(provider, "test-model", "Task")

        # 4 calls: inversion, original scenario, inverted scenario, comparison
        assert provider.send.call_count == 4

    def test_judge_provider_receives_system_prompt(self):
        """The judge comparison uses a system + user message pair."""
        provider = MagicMock()
        judge = MagicMock()
        provider.send.side_effect = [
            "Inverted",
            "Response A",
            "Response B",
        ]
        judge.send.return_value = _judge_json(substance_changed=False)

        run_ab_test(provider, "test-model", "Task", judge_provider=judge, judge_model="judge-m")

        judge.send.assert_called_once()
        messages = judge.send.call_args[0][0]
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "STRICT JSON" in messages[1]["content"]


class TestPairProvenance:
    """A/B pair provenance tests — machine-inverted vs. user-authored."""

    def test_run_ab_test_has_machine_inverted_provenance(self):
        provider = MagicMock()
        provider.send.side_effect = [
            "Inverted task text",
            "Response to original",
            "Response to inverted",
            _judge_json(substance_changed=False),
        ]
        result = run_ab_test(provider, "test-model", "Original task")
        assert result.pair_provenance == "machine-inverted"

    def test_run_ab_test_with_user_task_has_user_authored_provenance(self):
        provider = MagicMock()
        provider.send.side_effect = [
            "Response to original",
            "Response to inverted",
            _judge_json(substance_changed=True),
        ]
        result = run_ab_test_with_user_task(
            provider, "test-model",
            original_task="Original task",
            user_inverted_task="Analyst-authored inverse task",
        )
        assert result.pair_provenance == "user-authored"
        assert result.original_task == "Original task"
        assert result.inverted_task == "Analyst-authored inverse task"

    def test_run_ab_test_with_user_task_uses_correct_call_count(self):
        """User-authored path: no inversion call, so only 3 provider calls."""
        provider = MagicMock()
        provider.send.side_effect = [
            "Response A",
            "Response B",
            _judge_json(substance_changed=False),
        ]
        run_ab_test_with_user_task(
            provider, "test-model",
            original_task="Task",
            user_inverted_task="Inverted task",
        )
        # 3 calls: original scenario, inverted scenario, comparison
        assert provider.send.call_count == 3

    def test_default_pair_provenance_on_ab_result(self):
        """Default ABTestResult has machine-inverted provenance."""
        result = ABTestResult("t", "i", "r1", "r2", "c", substance_changed=False)
        assert result.pair_provenance == "machine-inverted"

    def test_user_authored_provenance_explicit(self):
        """Can explicitly set user-authored provenance on an ABTestResult."""
        result = ABTestResult(
            "t", "i", "r1", "r2", "c",
            substance_changed=False,
            pair_provenance="user-authored",
        )
        assert result.pair_provenance == "user-authored"
