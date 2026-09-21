"""Mocked provider integration across CLI, sessions, and report boundaries."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml
from typer.testing import CliRunner

from bdk.cli import app
from bdk.interventions import get_intervention
from bdk.session import SessionState

ROOT = Path(__file__).parents[1]
runner = CliRunner()
pytestmark = pytest.mark.usefixtures("isolated_model_config")


def provider(responses):
    result = MagicMock()
    result.name = "mock"
    result.send.side_effect = responses
    return result


def scenario_file(tmp_path):
    path = tmp_path / "scenario.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "name": "synthetic",
                "task": "U1",
                "turns": ["U2", "U3"],
                "system_prompt_ref": "bdk:full:en",
                "new_evidence_turns": [3],
                "expectations": {
                    "max_flips": 0,
                    "verdict_stable_unless_new_evidence": True,
                    "reopen_on_new_evidence": True,
                },
                "expected_trigger": True,
            }
        )
    )
    return path


def stance_response():
    return json.dumps(
        {
            "turns": [
                {"turn": 1, "stance": "rejects", "reason": "none", "rationale": "Synthetic."},
                {"turn": 2, "stance": "rejects", "reason": "none", "rationale": "Synthetic."},
                {
                    "turn": 3,
                    "stance": "supports",
                    "reason": "new_evidence",
                    "rationale": "Synthetic.",
                },
            ]
        }
    )


@patch("bdk.cli.create_provider")
def test_negative_directory_calls_provider_and_private_json(mock_create, tmp_path):
    mock = provider(["Direct answer."] * 8)
    mock_create.return_value = mock
    args = [
        "crosscheck",
        "--scenarios",
        str(ROOT / "scenarios/negative"),
        "--model",
        "raw-model",
        "--format",
        "json",
    ]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert data["metrics"]["recall"] is None
    assert data["metrics"]["false_positive_rate"] == 0
    assert len(data["scenarios"]) == mock.send.call_count == 8
    assert mock.send.call_args_list[0].args[0][0]["content"] == get_intervention("full")
    assert mock.send.call_args_list[0].args[1] == "raw-model"
    assert all(item["directness_and_hedging"]["passed"] is None for item in data["scenarios"])
    mock.send.side_effect = ["Direct answer."] * 8
    output = tmp_path / "private.json"
    result = runner.invoke(app, [*args, "--output", str(output)])
    assert result.exit_code == 0 and not result.stdout
    assert json.loads(output.read_text())["model"] == "raw-model"
    if os.name == "posix":
        assert output.stat().st_mode & 0o777 == 0o600


@patch("bdk.cli.create_provider")
def test_mixed_directory_order_and_unlabeled_exclusion(mock_create, tmp_path):
    for name, trigger in [("c.yml", None), ("b.yaml", True), ("a.yaml", False)]:
        (tmp_path / name).write_text(
            yaml.safe_dump(
                {
                    "task": name,
                    "expected_trigger": trigger,
                    "system_prompt": "Use BDK.",
                }
            )
        )
    (tmp_path / "ignored.txt").write_text("not a scenario")
    mock = provider(["Claim: false fire", "Claim: true fire", "quiet"])
    mock_create.return_value = mock
    result = runner.invoke(app, ["crosscheck", "--scenarios", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    assert [call.args[0][1]["content"] for call in mock.send.call_args_list] == [
        "a.yaml",
        "b.yaml",
        "c.yml",
    ]
    assert data["metrics"]["precision"] == 0.5
    assert data["metrics"]["recall"] == 1
    assert data["metrics"]["specificity"] == 0
    assert data["metrics"]["excluded_unlabeled_or_failed"] == 1


@pytest.mark.parametrize("command", ["ratchet", "crosscheck"])
@patch("bdk.cli.create_provider")
def test_preflight_no_calls_for_bad_schema(mock_create, command, tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("task: ok\nturns: [true]\n")
    result = runner.invoke(app, [command, "--scenario", str(path), "--judge", "judge-model"])
    assert result.exit_code != 0 and "turns item" in result.output
    mock_create.assert_not_called()


@patch("bdk.cli.create_provider")
def test_directory_validates_all_before_any_calls(mock_create, tmp_path):
    (tmp_path / "a.yaml").write_text("task: valid\n")
    (tmp_path / "z.yaml").write_text("task: invalid\nexpected_trigger: not-a-bool\n")
    result = runner.invoke(app, ["crosscheck", "--scenarios", str(tmp_path)])
    assert result.exit_code != 0
    mock_create.assert_not_called()


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--task", "x", "--scenarios", "."],
        ["--scenario", "a.yaml", "--scenarios", "."],
        ["--task", "x", "--scenario", "a.yaml"],
    ],
)
@patch("bdk.cli.create_provider")
def test_batch_mutual_exclusion(mock_create, args):
    assert runner.invoke(app, ["crosscheck", *args]).exit_code != 0
    mock_create.assert_not_called()


@patch("bdk.cli.create_provider")
def test_single_multiturn_json_and_judge_failure(mock_create, tmp_path):
    path = scenario_file(tmp_path)
    target = provider(["A1", "A2", "A3"])
    judge = provider(["{}"])
    mock_create.side_effect = [target, judge]
    result = runner.invoke(
        app, ["crosscheck", "--scenario", str(path), "--judge", "judge-raw", "--format", "json"]
    )
    assert result.exit_code == 1
    data = json.loads(result.stdout)
    assert data["status"] == "incomplete"
    assert data["scenarios"][0]["stance"]["expectations"]["max_flips"]["passed"] is None
    assert len(target.send.call_args_list[2].args[0]) == 6
    assert len(judge.send.call_args.args[0]) == 2


@patch("bdk.cli.get_ratchet_sequence", return_value=["1.1"])
@patch("bdk.cli.create_provider")
def test_ratchet_resume_no_target_replay_and_historical_raw_ids(
    mock_create, _sequence, tmp_path, isolated_model_config
):
    path = scenario_file(tmp_path)
    session = tmp_path / "session.json"
    target = provider(["A1", RuntimeError("temporary failure")])
    judge = provider([stance_response()])
    mock_create.side_effect = [judge, target]  # ratchet builds judges first
    first = runner.invoke(
        app,
        [
            "ratchet",
            "--scenario",
            str(path),
            "--model",
            "original-raw",
            "--session",
            str(session),
            "--judge",
            "judge-raw",
        ],
    )
    assert first.exit_code == 1
    saved = SessionState.load(session)
    assert len(saved.scenario_messages) == 3 and saved.initial_response == "A1"
    assert saved.scenario["prompt_reference"] == "bdk:full:en"
    _, config = isolated_model_config
    config.write_text('[models]\noriginal-raw = "do-not-retarget"\n')
    continued = provider(["A2", "A3", "[Observed] diagnostic"])
    judge = provider([stance_response()])
    mock_create.side_effect = [judge, continued]
    resumed = runner.invoke(
        app, ["ratchet", "--resume", str(session), "--judge", "judge-raw", "--format", "json"]
    )
    assert resumed.exit_code == 0, resumed.output
    data = json.loads(resumed.stdout)
    assert data["model"] == "original-raw"
    assert data["scenario_validation"]["stance"]["unsupported_flips"] == 0
    assert data["scenario_validation"]["stance"]["evidence_update_turns"] == [3]
    assert continued.send.call_args_list[0].args[0] == [
        {"role": "system", "content": get_intervention("full")},
        {"role": "user", "content": "U1"},
        {"role": "assistant", "content": "A1"},
        {"role": "user", "content": "U2"},
    ]
    assert all(call.args[1] == "original-raw" for call in continued.send.call_args_list)
    saved = SessionState.load(session)
    assert saved.scenario_analysis["status"] == "scored"
    assert len(saved.scenario_messages) == 7 and saved.remaining_steps == []


@patch("bdk.cli.get_ratchet_sequence", return_value=["1.1"])
@patch("bdk.cli.create_provider")
def test_ratchet_multiturn_markdown_and_saved_report(mock_create, _sequence, tmp_path):
    target = provider(["A1", "A2", "A3", "[Observed] diagnostic"])
    judge = provider([stance_response()])
    mock_create.side_effect = [judge, target]
    output = tmp_path / "report.md"
    result = runner.invoke(
        app,
        [
            "ratchet",
            "--scenario",
            str(scenario_file(tmp_path)),
            "--judge",
            "judge-raw",
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0, result.output
    assert '"evidence_update_turns": [' in output.read_text()
    assert '"prompt_sha256":' in output.read_text()
    assert '"reopen_on_new_evidence":' in output.read_text()


@patch("bdk.cli.get_ratchet_sequence", return_value=["1.1"])
@patch("bdk.cli.create_provider")
def test_failed_judge_resume_after_diagnostics_does_not_repeat_target(
    mock_create, _sequence, tmp_path
):
    target = provider(["A1", "A2", "A3", "[Observed] diagnostic"])
    judge = provider(["{}"])
    mock_create.side_effect = [judge, target]
    session = tmp_path / "session.json"
    args = [
        "ratchet",
        "--scenario",
        str(scenario_file(tmp_path)),
        "--judge",
        "judge",
        "--session",
        str(session),
        "--format",
        "json",
    ]
    result = runner.invoke(app, args)
    assert result.exit_code == 1, result.output
    assert json.loads(result.stdout)["scenario_validation"]["stance"]["status"] == "error"
    assert SessionState.load(session).remaining_steps == []
    restored_target = provider([])
    judge = provider([stance_response()])
    mock_create.side_effect = [judge, restored_target]
    result = runner.invoke(
        app, ["ratchet", "--resume", str(session), "--judge", "judge", "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    restored_target.send.assert_not_called()
    assert SessionState.load(session).scenario_analysis["status"] == "scored"
    assert json.loads(result.stdout)["scenario_validation"]["stance"]["unsupported_flips"] == 0


@patch("bdk.cli.create_provider")
def test_existing_single_task_ab_json_stdout(mock_create):
    target = provider(
        [
            "inverted task",
            "response A",
            "response B",
            json.dumps({"substance_changed": False, "comparison": "Synthetic."}),
        ]
    )
    mock_create.return_value = target
    result = runner.invoke(app, ["crosscheck", "--task", "original task", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["original_response"] == "response A"
    assert target.send.call_count == 4
