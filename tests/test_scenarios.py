"""Synthetic scenario/schema and sequential-history tests; never live evidence."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from bdk.engine import DiagnosticEngine
from bdk.interventions import get_intervention
from bdk.scenarios import Scenario, load_scenario, load_scenarios, parse_scenario

ROOT = Path(__file__).parents[1]


def test_legacy_schema_code_and_recommended_path():
    spec = load_scenario(ROOT / "scenarios/sycophancy.yaml")
    assert spec.expected_trigger is None
    assert spec.turns == []
    assert spec.recommended_path == ["1.2", "3.2", "4.1"]
    assert spec.user_messages[0] == f"{spec.task}\n\n```\n{spec.code}\n```"
    assert spec.system_prompt == "You are a helpful assistant."
    assert parse_scenario(spec.snapshot(), saved=True) == spec


def test_all_new_negative_scenarios_use_real_prompt():
    specs = load_scenarios(ROOT / "scenarios/negative")
    assert len(specs) >= 8
    assert [s.source for s in specs] == sorted(s.source for s in specs)
    for spec in specs:
        assert spec.expected_trigger is False
        assert spec.system_prompt == get_intervention("full")
        assert spec.prompt_version == "prompt-v2.0"
        assert spec.provenance["prompt_sha256"]
        assert "No BDK protocol section headers; answers directly; <=" in spec.expectation
        assert parse_scenario(spec.snapshot(), saved=True) == spec
    assert all(s.expected_trigger is True for s in load_scenarios(ROOT / "scenarios/positive"))


@pytest.mark.parametrize(
    "fields",
    [
        {"task": False},
        {"system_prompt": None},
        {"name": []},
        {"code": {}},
        {"turns": "not-list"},
        {"turns": [1]},
        {"turns": [""]},
        {"expected_trigger": "false"},
        {"recommended_path": "1.2"},
        {"recommended_path": [1.2]},
        {"recommended_path": ["not-real"]},
        {"expectation": {}},
        {"system_prompt_ref": "../prompt"},
        {"system_prompt_ref": "bdk:nope:en"},
        {"system_prompt_ref": "bdk:full:en", "system_prompt": "override"},
        {"expectations": {"max_flips": True}},
        {"expectations": {"max_flips": -1}},
        {"expectations": {"verdict_stable_unless_new_evidence": "true"}},
        {"expectations": {"unknown": False}},
        {"new_evidence_turns": [0]},
        {"new_evidence_turns": [2, 2]},
        {"new_evidence_turns": [True]},
        {"expectations": {"reopen_on_new_evidence": True}},
    ],
)
def test_preflight_invalid_fields(fields):
    with pytest.raises(ValueError):
        parse_scenario({"task": "Original", "turns": ["Follow-up"], **fields})


def test_bad_files_and_empty_directory(tmp_path):
    with pytest.raises(ValueError, match="no YAML"):
        load_scenarios(tmp_path)
    (tmp_path / "ignore.txt").write_text("not yaml")
    (tmp_path / "bad.yaml").write_text("task: [")
    with pytest.raises(ValueError, match="bad.yaml"):
        load_scenarios(tmp_path)
    (tmp_path / "bad.yaml").write_text("- not a mapping")
    with pytest.raises(ValueError, match="mapping"):
        load_scenario(tmp_path / "bad.yaml")


def test_engine_exact_sequential_history():
    provider = MagicMock()
    provider.send.side_effect = ["A1", "A2", "A3"]
    spec = parse_scenario({"task": "U1", "system_prompt": "S", "turns": ["U2", "U3"]})
    engine = DiagnosticEngine(provider, "raw-id")
    snapshots = []
    assert engine.run_scenario(spec, on_turn=lambda: snapshots.append(engine.messages.copy())) == [
        "A1",
        "A2",
        "A3",
    ]
    expected = [{"role": "system", "content": "S"}]
    for i, call in enumerate(provider.send.call_args_list, 1):
        expected.append({"role": "user", "content": f"U{i}"})
        assert call.args == (expected, "raw-id")
        expected.append({"role": "assistant", "content": f"A{i}"})
    assert snapshots == [expected[:3], expected[:5], expected[:7]]
    assert engine.initial_response == "A1"
    assert engine.scenario_messages == expected


def test_engine_validates_before_call_and_retains_completed_turns():
    provider = MagicMock()
    engine = DiagnosticEngine(provider, "raw-id")
    with pytest.raises(ValueError):
        engine.run_scenario(Scenario("Bad", "task", turns=[False]))
    provider.send.assert_not_called()
    provider.send.side_effect = ["A1", RuntimeError("target unavailable")]
    spec = parse_scenario({"task": "U1", "turns": ["U2"]})
    with pytest.raises(RuntimeError):
        engine.run_scenario(spec)
    assert len(engine.messages) == len(engine.scenario_messages) == 3
    provider.send.side_effect = ["A2"]
    engine.run_scenario(spec)
    assert engine.messages[-1]["content"] == "A2"
    assert provider.send.call_count == 3
