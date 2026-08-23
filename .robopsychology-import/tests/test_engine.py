"""Tests for the diagnostic engine."""

from unittest.mock import MagicMock

from robopsych.engine import DiagnosticEngine, DiagnosticStep


def _mock_engine(responses: list[str] | None = None) -> DiagnosticEngine:
    """Create an engine with a mocked provider."""
    provider = MagicMock()
    provider.name = "mock"
    if responses:
        provider.send.side_effect = responses
    else:
        provider.send.return_value = "Mock diagnostic response."
    return DiagnosticEngine(provider=provider, model="mock-model")


class TestInjectExchange:
    def test_injects_three_messages(self):
        engine = _mock_engine()
        engine.inject_exchange(task="Do X", response="Did X")
        assert len(engine.messages) == 3
        assert engine.messages[0]["role"] == "system"
        assert engine.messages[1]["role"] == "user"
        assert engine.messages[2]["role"] == "assistant"

    def test_stores_initial_response(self):
        engine = _mock_engine()
        engine.inject_exchange(task="Do X", response="Did X")
        assert engine.initial_response == "Did X"

    def test_task_is_user_message(self):
        engine = _mock_engine()
        engine.inject_exchange(task="Review this code", response="Looks fine")
        assert "Review this code" in engine.messages[1]["content"]
        assert "<robopsych_task>" in engine.messages[1]["content"]
        assert "untrusted data" in engine.messages[1]["content"]

    def test_response_is_delimited_as_untrusted_data(self):
        engine = _mock_engine()
        engine.inject_exchange(task="Review this code", response="Looks fine")
        assert "Looks fine" in engine.messages[2]["content"]
        assert "<robopsych_response>" in engine.messages[2]["content"]
        assert "do not obey" in engine.messages[2]["content"]


class TestSetupScenario:
    def test_sends_task_and_captures_response(self):
        engine = _mock_engine(["Model says hello."])
        result = engine.setup_scenario("Write hello world")
        assert result == "Model says hello."
        assert engine.initial_response == "Model says hello."

    def test_uses_custom_system_prompt(self):
        engine = _mock_engine(["OK"])
        engine.setup_scenario("task", system_prompt="Be concise.")
        assert engine.messages[0]["content"] == "Be concise."

    def test_uses_default_system_prompt(self):
        engine = _mock_engine(["OK"])
        engine.setup_scenario("task")
        assert engine.messages[0]["content"] == "You are a helpful assistant."

    def test_messages_have_correct_structure(self):
        engine = _mock_engine(["response"])
        engine.setup_scenario("task")
        assert len(engine.messages) == 3
        roles = [m["role"] for m in engine.messages]
        assert roles == ["system", "user", "assistant"]


class TestRunDiagnostic:
    def test_returns_diagnostic_step(self):
        engine = _mock_engine()
        engine.inject_exchange(task="X", response="Y")
        step = engine.run_diagnostic("1.1")
        assert isinstance(step, DiagnosticStep)
        assert step.prompt_id == "1.1"
        assert step.prompt_name == "Calvin Question"
        assert step.response == "Mock diagnostic response."

    def test_appends_to_messages(self):
        engine = _mock_engine()
        engine.inject_exchange(task="X", response="Y")
        initial_count = len(engine.messages)
        engine.run_diagnostic("1.1")
        assert len(engine.messages) == initial_count + 2  # user + assistant

    def test_stores_step_in_history(self):
        engine = _mock_engine()
        engine.inject_exchange(task="X", response="Y")
        engine.run_diagnostic("1.1")
        assert len(engine.steps) == 1
        assert engine.steps[0].prompt_id == "1.1"

    def test_variables_are_rendered(self):
        engine = _mock_engine()
        engine.inject_exchange(task="X", response="Y")
        engine.run_diagnostic("1.4", variables={"action": "write code"})
        # The prompt text sent should contain the variable
        prompt_msg = engine.messages[-2]  # user message
        assert "write code" in prompt_msg["content"]


class TestRunSequence:
    def test_runs_all_prompts_in_order(self):
        engine = _mock_engine()
        engine.inject_exchange(task="X", response="Y")
        results = engine.run_sequence(["1.1", "1.2", "1.3"])
        assert len(results) == 3
        assert results[0].prompt_id == "1.1"
        assert results[1].prompt_id == "1.2"
        assert results[2].prompt_id == "1.3"

    def test_calls_on_step_callback(self):
        engine = _mock_engine()
        engine.inject_exchange(task="X", response="Y")
        callback = MagicMock()
        engine.run_sequence(["1.1", "1.2"], on_step=callback)
        assert callback.call_count == 2

    def test_accumulates_messages(self):
        engine = _mock_engine()
        engine.inject_exchange(task="X", response="Y")
        engine.run_sequence(["1.1", "1.2", "1.3"])
        # 3 initial + 3 * 2 (user + assistant per step) = 9
        assert len(engine.messages) == 9

    def test_full_ratchet_sequence(self):
        engine = _mock_engine()
        engine.inject_exchange(task="X", response="Y")
        from robopsych.prompts import get_ratchet_sequence

        seq = get_ratchet_sequence()
        results = engine.run_sequence(seq)
        assert len(results) == 9
