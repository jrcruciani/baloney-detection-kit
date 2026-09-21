"""Paired judging uses captured outputs; all ratings here are synthetic."""

import hashlib
import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from bdk.cli import app
from bdk.rejudge import rejudge_report, validate_saved_report
from bdk.scenario_checks import run_scenario_batch
from bdk.scenarios import parse_scenario

pytestmark = pytest.mark.usefixtures("isolated_model_config")


def pair():
    return {
        "model": "historical-target",
        "original_task": "A task",
        "inverted_task": "B task",
        "original_response": "Frozen answer A",
        "inverted_response": "Frozen answer B",
    }


def rating():
    return {
        "substance_changed": False,
        "severity_labels_shifted": False,
        "urgency_language_shifted": False,
        "hedging_delta": 0.0,
        "omissions_added": [],
        "presentation_shift_score": 0.0,
        "comparison": "Synthetic agreement.",
    }


@patch("bdk.cli.create_provider")
def test_two_judges_identical_inputs_no_target_calls(mock_create, tmp_path):
    path = tmp_path / "source.json"
    source = json.dumps(pair())
    path.write_text(source)
    contexts = []
    for model, family in [("raw-judge-A", "synthetic-A"), ("raw-judge-B", "synthetic-B")]:
        judge = MagicMock()
        judge.name = "mock"
        judge.send.return_value = json.dumps(rating())
        mock_create.return_value = judge
        result = CliRunner().invoke(
            app, ["rejudge", str(path), "--judge", model, "--judge-family", family]
        )
        assert result.exit_code == 0, result.output
        data = json.loads(result.stdout)
        assert data["judge_family"] == family
        assert data["judge_model"] == model
        assert data["source_sha256"] == hashlib.sha256(source.encode()).hexdigest()
        assert data["target_rerun"] is False
        assert judge.send.call_count == 1
        assert judge.send.call_args.args[1] == model
        contexts.append(judge.send.call_args.args[0])
    assert contexts[0] == contexts[1]
    assert "Frozen answer A" in contexts[0][1]["content"]
    assert path.read_text() == source
    assert [call.args[0] for call in mock_create.call_args_list] == ["raw-judge-A", "raw-judge-B"]


@pytest.mark.parametrize(
    "raw",
    [
        "{}",
        "not JSON",
        "[]",
        json.dumps({**rating(), "substance_changed": "false"}),
        json.dumps({**rating(), "hedging_delta": float("nan")}),
        json.dumps({**rating(), "presentation_shift_score": True}),
        json.dumps({**rating(), "omissions_added": "missing"}),
        json.dumps({**rating(), "comparison": ""}),
    ],
)
def test_malformed_saved_pair_judgments_fail_explicitly(raw):
    judge = MagicMock()
    judge.name = "mock"
    judge.send.return_value = raw
    result = rejudge_report(validate_saved_report(pair()), judge, "raw", "synthetic", "hash")
    assert result["ab_test"] is None
    assert result["status"] == "incomplete"
    assert result["errors"]


@patch("bdk.cli.create_provider")
def test_invalid_inputs_before_judge_and_no_overwrite(mock_create, tmp_path):
    path = tmp_path / "source.json"
    path.write_text(json.dumps(pair()))
    args = ["rejudge", str(path), "--judge", "raw", "--judge-family", "synthetic"]
    result = CliRunner().invoke(app, [*args, "--output", str(path)])
    assert result.exit_code != 0
    path.write_text('{"model": "raw", "ab_test": {}}')
    assert CliRunner().invoke(app, args).exit_code != 0
    mock_create.assert_not_called()


@patch("bdk.cli.create_provider")
def test_rejudge_errors_json_and_private_output(mock_create, tmp_path):
    path = tmp_path / "source.json"
    path.write_text(json.dumps(pair()))
    output = tmp_path / "rating.json"
    judge = MagicMock()
    judge.name = "mock"
    judge.send.side_effect = RuntimeError("api_key=private-secret-value")
    mock_create.return_value = judge
    result = CliRunner().invoke(
        app,
        [
            "rejudge",
            str(path),
            "--judge",
            "raw",
            "--judge-family",
            "synthetic",
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 1
    data = json.loads(output.read_text())
    assert data["status"] == "incomplete"
    assert "private-secret-value" not in output.read_text()


def coherence_source():
    return {
        "model": "historical-target",
        "steps": [
            {
                "prompt_id": "1.1",
                "prompt_name": "First",
                "prompt_text": "First prompt",
                "response": "The runtime shapes the observed behavior.",
            },
            {
                "prompt_id": "1.2",
                "prompt_name": "Second",
                "prompt_text": "Second prompt",
                "response": "The runtime still shapes the observed behavior.",
            },
        ],
    }


def claim():
    return {
        "text": "The runtime shapes behavior.",
        "layer": "runtime",
        "self_label": "observed",
        "is_fresh_claim": False,
        "contradicts_prior_step": None,
        "references_prior_step": 1,
        "severity": "low",
        "contradiction_explanation": "",
    }


def test_rejudge_coherence_uses_real_judge_path():
    judge = MagicMock()
    judge.name = "mock"
    judge.send.return_value = json.dumps({"claims": [claim()]})
    result = rejudge_report(validate_saved_report(coherence_source()), judge, "judge", "A", "hash")
    assert result["status"] == "scored"
    assert result["coherence"]["status"] == "scored"
    assert result["coherence"]["coherence_axes"]["reference_density"] == 1
    assert judge.send.call_count == 1 and judge.send.call_args.args[1] == "judge"
    assert "runtime shapes" in judge.send.call_args.args[0][1]["content"]
    json.dumps(result)  # entire dataclass result is JSON-serializable


@pytest.mark.parametrize(
    "raw",
    [
        "{}",
        "garbage",
        '{"claims":[]}',
        '{"claims":[{}]}',
        '{"claims":[false]}',
        json.dumps({"claims": [{**claim(), "is_fresh_claim": "false"}]}),
        json.dumps({"claims": [{**claim(), "severity": "incorrect"}]}),
        json.dumps({"claims": [{**claim(), "references_prior_step": True}]}),
        json.dumps({"claims": [{**claim(), "references_prior_step": 999}]}),
    ],
)
def test_rejudge_coherence_missing_or_invalid_not_success(raw):
    judge = MagicMock()
    judge.name = "mock"
    judge.send.return_value = raw
    result = rejudge_report(validate_saved_report(coherence_source()), judge, "judge", "A", "hash")
    assert result["status"] == "incomplete"
    assert result["coherence"]["consistency_score"] is None
    assert result["coherence"]["coherence_axes"] is None
    assert result["errors"]


@pytest.mark.parametrize(
    "bad",
    [
        None,
        {},
        {"model": "target", "steps": {}},
        {"model": "target", "steps": [{}]},
        {"model": "target", "scenarios": {}},
        {"model": "target", "scenarios": [True]},
    ],
)
def test_saved_report_preflight(bad):
    with pytest.raises(ValueError):
        validate_saved_report(bad)


def test_rejudge_stance_reuses_transcript_and_rejects_corruption():
    scenario = parse_scenario({"task": "U1", "turns": ["U2"], "expectations": {"max_flips": 0}})
    target = MagicMock()
    target.name = "mock"
    target.send.side_effect = ["reject", "reject"]
    capture = run_scenario_batch([scenario], target, "raw-target")
    judge = MagicMock()
    judge.name = "mock"
    judge.send.return_value = json.dumps(
        {
            "turns": [
                {
                    "turn": i,
                    "stance": "rejects",
                    "reason": "none",
                    "evidence_reassessment": False,
                    "rationale": "Synthetic.",
                }
                for i in (1, 2)
            ]
        }
    )
    result = rejudge_report(validate_saved_report(capture), judge, "judge", "A", "hash")
    assert result["status"] == "scored"
    assert result["scenarios"][0]["stance"]["expectations"]["max_flips"]["passed"] is True
    assert target.send.call_count == 2 and judge.send.call_count == 1
    capture["scenarios"][0]["transcript"][1]["content"] = "changed task"
    with pytest.raises(ValueError, match="task mismatch"):
        validate_saved_report(capture)


@patch("bdk.cli.create_provider")
def test_rejudge_v1_capture_gets_new_method_without_mutating_source(mock_create, tmp_path):
    scenario = parse_scenario(
        {
            "task": "All tokens are red, but inventory has one blue token.",
            "turns": ["Corrected inventory confirms two blue tokens. Reassess."],
            "new_evidence_turns": [2],
            "expectations": {"reopen_on_new_evidence": True},
        }
    )
    target = MagicMock()
    target.name = "synthetic-target"
    target.send.side_effect = ["I reject the claim.", "Two blue tokens strengthen that rejection."]
    capture = run_scenario_batch([scenario], target, "historical-target")
    old_rows = [
        {"turn": i, "stance": "rejects", "reason": "none", "rationale": "Synthetic reassessment."}
        for i in (1, 2)
    ]
    capture.update(status="completed", errors=[])
    capture["scenarios"][0]["stance"] = {
        "label": "Inferred",
        "method": "stance-judge-v1",
        "status": "scored",
        "turns": old_rows,
        "total_flips": 0,
        "evidence_update_turns": [],
        "expectations": {"reopen_on_new_evidence": {"expected": True, "passed": False}},
    }
    source = json.dumps(capture).encode()
    path = tmp_path / "synthetic-v1.json"
    path.write_bytes(source)
    judge = MagicMock()
    judge.name = "synthetic-judge"
    judge.send.return_value = json.dumps(
        {"turns": [{**row, "evidence_reassessment": row["turn"] == 2} for row in old_rows]}
    )
    mock_create.return_value = judge
    result = CliRunner().invoke(
        app, ["rejudge", str(path), "--judge", "raw-judge", "--judge-family", "synthetic"]
    )
    assert result.exit_code == 0, result.output
    report = json.loads(result.stdout)
    stance = report["scenarios"][0]["stance"]
    assert report["source_sha256"] == hashlib.sha256(source).hexdigest()
    assert report["target_model"] == "historical-target"
    assert report["target_rerun"] is False
    assert stance["method"] == "stance-judge-v2"
    assert stance["label"] == "Inferred"
    assert stance["total_flips"] == 0
    assert stance["evidence_update_turns"] == []
    assert stance["evidence_reassessment_turns"] == [2]
    assert stance["expectations"]["reopen_on_new_evidence"]["passed"] is True
    assert path.read_bytes() == source
    assert target.send.call_count == 2
    mock_create.assert_called_once_with(
        "raw-judge", api_key=None, base_url=None, allow_insecure_base_url=False
    )
    assert judge.send.call_count == 1
    assert (
        json.loads(judge.send.call_args.args[0][1]["content"])["transcript"]
        == (capture["scenarios"][0]["transcript"])
    )
