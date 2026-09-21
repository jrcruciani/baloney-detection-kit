"""Exercise resolved IDs all the way from CLI options to provider sends."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import typer
from typer.testing import CliRunner

from bdk.cli import _build_engine, _build_judge, app
from bdk.session import SessionState

pytestmark = pytest.mark.usefixtures("isolated_model_config", "provider_env")
runner = CliRunner()
TARGET_COMMANDS = [
    ["run", "1.2", "--response", "Initial response."],
    ["guided", "--response", "Initial response."],
    ["ratchet", "--response", "Initial response."],
    ["compare", "1.2", "--response", "Initial response."],
    ["crosscheck", "--task", "Test the claim."],
]
JUDGE_COMMANDS = [
    ["crosscheck", "--task", "Test the claim.", "--judge"],
    ["ratchet", "--response", "Initial response.", "--behavioral", "--judge"],
    ["ratchet", "--response", "Initial response.", "--coherence-judge"],
]


@pytest.fixture
def providers(monkeypatch):
    instances = {}

    def create(model, **kwargs):
        if model not in instances:
            provider = MagicMock()
            provider.name = "mock"
            provider.send.return_value = json.dumps(
                {"claims": [], "substance_changed": False, "explanation": "No change."}
            )
            instances[model] = provider
        return instances[model]

    factory = MagicMock(side_effect=create)
    monkeypatch.setattr("bdk.cli.create_provider", factory)
    return factory, instances


@pytest.fixture
def configured_models(isolated_model_config):
    _, local = isolated_model_config
    local.write_text(
        '[models]\ndefault = "gpt-target"\nreferee = "claude-judge"\n'
        'gpt-target = "do-not-expand-again"\nclaude-judge = "do-not-expand-again"\n'
    )


@pytest.mark.parametrize("command", TARGET_COMMANDS, ids=lambda command: command[0])
@pytest.mark.parametrize("use_alias", [False, True], ids=["raw", "alias"])
def test_target_model_reaches_every_send(command, use_alias, isolated_model_config, providers):
    _, local = isolated_model_config
    local.write_text('[models]\ndefault = "gpt-target"\n')
    factory, instances = providers
    selected = "default" if use_alias else "gpt-target"
    option = "--models" if command[0] == "compare" else "--model"

    result = runner.invoke(app, [*command, option, selected], input="2\nn\n")

    assert result.exit_code == 0, result.output
    assert [call.args[0] for call in factory.call_args_list] == ["gpt-target"]
    calls = instances["gpt-target"].send.call_args_list
    assert calls
    assert all(call.args[1] == "gpt-target" for call in calls)


@pytest.mark.parametrize("command", TARGET_COMMANDS, ids=lambda command: command[0])
def test_target_alias_is_not_resolved_twice(command, configured_models, providers):
    factory, instances = providers
    option = "--models" if command[0] == "compare" else "--model"
    result = runner.invoke(app, [*command, option, "default"], input="2\nn\n")
    assert result.exit_code == 0, result.output
    assert factory.call_args.args[0] == "gpt-target"
    assert all(call.args[1] == "gpt-target" for call in instances["gpt-target"].send.call_args_list)


@pytest.mark.parametrize("command", JUDGE_COMMANDS, ids=["crosscheck", "behavioral", "coherence"])
@pytest.mark.parametrize("use_alias", [False, True], ids=["raw", "alias"])
def test_judge_model_reaches_every_send(command, use_alias, isolated_model_config, providers):
    _, local = isolated_model_config
    local.write_text('[models]\ndefault = "gpt-target"\nreferee = "claude-judge"\n')
    factory, instances = providers
    selected = "referee" if use_alias else "claude-judge"
    result = runner.invoke(app, [*command, selected, "--model", "default"])
    assert result.exit_code == 0, result.output
    assert {call.args[0] for call in factory.call_args_list} == {"gpt-target", "claude-judge"}
    for model, provider in instances.items():
        assert provider.send.call_count
        assert all(call.args[1] == model for call in provider.send.call_args_list)


@pytest.mark.parametrize("command", JUDGE_COMMANDS, ids=["crosscheck", "behavioral", "coherence"])
def test_judge_alias_is_not_resolved_twice(command, configured_models, providers):
    factory, instances = providers
    result = runner.invoke(app, [*command, "referee", "--model", "default"])
    assert result.exit_code == 0, result.output
    assert {call.args[0] for call in factory.call_args_list} == {"gpt-target", "claude-judge"}
    assert all(
        call.args[1] == "claude-judge" for call in instances["claude-judge"].send.call_args_list
    )


@pytest.mark.parametrize("helper", ["engine", "judge"])
@pytest.mark.parametrize("model", ["claude-raw", "gpt-raw", "gemini-raw", "azure/deployment"])
def test_helpers_use_resolved_id_and_keep_provider_options(
    helper, model, isolated_model_config, providers
):
    _, local = isolated_model_config
    local.write_text(f'[models]\ndefault = "{model}"\n')
    factory, instances = providers
    if helper == "engine":
        engine = _build_engine("default", "test-key", "http://localhost:9999", True)
        provider, actual_model = engine.provider, engine.model
    else:
        provider, actual_model = _build_judge("default", "test-key", "http://localhost:9999", True)
    assert actual_model == model
    assert provider is instances[model]
    factory.assert_called_once_with(
        model, api_key="test-key", base_url="http://localhost:9999", allow_insecure_base_url=True
    )


@pytest.mark.parametrize("helper", ["engine", "judge"])
def test_helpers_reject_missing_default(helper, providers):
    with pytest.raises(typer.BadParameter, match="not configured"):
        if helper == "engine":
            _build_engine("default", None, None)
        else:
            _build_judge("default")
    providers[0].assert_not_called()


ERROR_COMMANDS = [
    [*command, "--models" if command[0] == "compare" else "--model", "default"]
    for command in TARGET_COMMANDS
] + [[*command, "default", "--model", "gpt-target"] for command in JUDGE_COMMANDS]


@pytest.mark.parametrize("command", ERROR_COMMANDS)
@pytest.mark.parametrize("failure", ["missing-default", "malformed", "schema", "filesystem"])
def test_model_errors_never_reach_provider_send(command, failure, isolated_model_config, providers):
    _, local = isolated_model_config
    if failure == "malformed":
        local.write_text("[models")
    elif failure == "schema":
        local.write_text("[models]\ndefault = 42\n")
    elif failure == "filesystem":
        local.mkdir()
    factory, instances = providers
    result = runner.invoke(app, command, input="2\nn\n")
    assert result.exit_code == 2, result.output
    assert isinstance(result.exception, SystemExit)
    assert "Traceback" not in result.output
    expected = {
        "missing-default": "not configured",
        "malformed": "Cannot read model config",
        "schema": "[models].default",
        "filesystem": "Cannot read model config",
    }
    assert expected[failure] in result.output
    assert all(call.args[0] != "default" for call in factory.call_args_list)
    for provider in instances.values():
        provider.send.assert_not_called()


@pytest.mark.parametrize("selected", ["default", "gpt-target"])
def test_run_alias_and_raw_id_reach_mock_sdk(isolated_model_config, openai_sdk, tmp_path, selected):
    _, local = isolated_model_config
    local.write_text('[models]\ndefault = "gpt-target"\n')
    sdk_send = openai_sdk.OpenAI.return_value.chat.completions.create
    sdk_send.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Diagnostic result."))]
    )
    report = tmp_path / "report.json"
    result = runner.invoke(
        app,
        [
            "run",
            "1.2",
            "--model",
            selected,
            "--response",
            "Original response.",
            "--api-key",
            "test-key",
            "--format",
            "json",
            "--output",
            str(report),
        ],
    )
    assert result.exit_code == 0, result.output
    assert sdk_send.call_args.kwargs["model"] == "gpt-target"
    assert json.loads(report.read_text())["model"] == "gpt-target"


@pytest.mark.parametrize("selected", ["azure", "azure/gpt-deployment"])
def test_azure_alias_keeps_deployment_routing(
    isolated_model_config, openai_sdk, monkeypatch, selected
):
    _, local = isolated_model_config
    local.write_text('[models]\nazure = "azure/gpt-deployment"\n')
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://example.services.ai.azure.com")
    sdk_send = openai_sdk.OpenAI.return_value.responses.create
    sdk_send.return_value = SimpleNamespace(
        output=[SimpleNamespace(content=[SimpleNamespace(text="Diagnostic result.")])]
    )
    result = runner.invoke(
        app,
        ["run", "1.2", "--model", selected, "--response", "Response.", "--api-key", "test-key"],
    )
    assert result.exit_code == 0, result.output
    assert sdk_send.call_args.kwargs["model"] == "azure/gpt-deployment"
    assert openai_sdk.OpenAI.call_args.kwargs["base_url"].endswith("/openai")


def test_alias_does_not_bypass_url_safety(isolated_model_config, openai_sdk):
    _, local = isolated_model_config
    local.write_text('[models]\ndefault = "gpt-target"\n')
    result = runner.invoke(
        app,
        [
            "run",
            "1.2",
            "--model",
            "default",
            "--response",
            "Response.",
            "--api-key",
            "test-key",
            "--base-url",
            "http://localhost:9999",
        ],
    )
    assert result.exit_code != 0
    openai_sdk.OpenAI.assert_not_called()


def test_library_engine_does_not_resolve_cli_aliases(configured_models):
    from bdk.engine import DiagnosticEngine

    provider = MagicMock()
    engine = DiagnosticEngine(provider=provider, model="default")
    engine.setup_scenario("Task.")
    assert provider.send.call_args.args[1] == "default"


def test_unchanged_cli_default(providers):
    result = runner.invoke(app, ["run", "1.2", "--response", "Response."])
    assert result.exit_code == 0, result.output
    assert providers[0].call_args.args[0] == "claude-sonnet-4-6"


def test_report_session_and_checkpoint_store_actual_ids(configured_models, providers, tmp_path):
    report = tmp_path / "report.json"
    session = tmp_path / "session.json"
    result = runner.invoke(
        app,
        [
            "ratchet",
            "--model",
            "default",
            "--response",
            "Response.",
            "--coherence-judge",
            "referee",
            "--session",
            str(session),
            "--format",
            "json",
            "--output",
            str(report),
        ],
    )
    assert result.exit_code == 0, result.output
    assert SessionState.load(session).model == "gpt-target"
    data = json.loads(report.read_text())
    assert data["model"] == "gpt-target"
    assert data["coherence"]["judge_model"] == "claude-judge"
    assert json.loads(session.with_suffix(".json.coherence.json").read_text())["judge_model"] == (
        "claude-judge"
    )


@pytest.mark.parametrize("config", ['[models]\ngpt-target = "wrong-model"\n', "[models"])
def test_resume_keeps_saved_raw_id_even_when_config_changes(
    isolated_model_config, providers, tmp_path, config
):
    _, local = isolated_model_config
    local.write_text(config)
    session = tmp_path / "session.json"
    SessionState.create("mock", "gpt-target", ["1.2"]).save(session)
    result = runner.invoke(app, ["ratchet", "--resume", str(session)])
    assert result.exit_code == 0, result.output
    assert providers[0].call_args.args[0] == "gpt-target"
    assert SessionState.load(session).model == "gpt-target"
    assert providers[1]["gpt-target"].send.call_args.args[1] == "gpt-target"


def test_complete_resume_needs_no_config_or_providers(isolated_model_config, providers, tmp_path):
    _, local = isolated_model_config
    local.write_text("[models")
    session = tmp_path / "complete.json"
    SessionState.create("mock", "gpt-target", []).save(session)
    result = runner.invoke(
        app,
        [
            "ratchet",
            "--resume",
            str(session),
            "--behavioral",
            "--judge",
            "default",
            "--coherence-judge",
            "default",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "already complete" in result.output
    providers[0].assert_not_called()


def test_compare_report_uses_resolved_ids(configured_models, providers, tmp_path):
    report = tmp_path / "compare.md"
    result = runner.invoke(
        app,
        [
            "compare",
            "1.2",
            "--models",
            "default, gpt-other",
            "--response",
            "Response.",
            "--output",
            str(report),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "## gpt-target" in report.read_text()
    assert "## gpt-other" in report.read_text()
    assert "## default" not in report.read_text()


def test_compare_validates_all_models_before_sending(providers):
    result = runner.invoke(
        app, ["compare", "1.2", "--models", "gpt-target,default", "--response", "Response."]
    )
    assert result.exit_code == 2
    assert "not configured" in result.output
    providers[0].assert_not_called()


@pytest.mark.parametrize("format", ["markdown", "json"])
def test_crosscheck_report_uses_resolved_ids(configured_models, providers, tmp_path, format):
    report = tmp_path / "crosscheck.txt"
    result = runner.invoke(
        app,
        [
            "crosscheck",
            "--model",
            "default",
            "--judge",
            "referee",
            "--task",
            "Task.",
            "--format",
            format,
            "--output",
            str(report),
        ],
    )
    assert result.exit_code == 0, result.output
    if format == "json":
        data = json.loads(report.read_text())
        assert data["model"] == "gpt-target"
        assert data["judge_model"] == "claude-judge"
    else:
        assert "**Model:** `gpt-target`" in report.read_text()
        assert "**Judge:** `claude-judge`" in report.read_text()


@pytest.mark.parametrize("command", ["coherence", "score"])
def test_offline_analysis_does_not_resolve_historical_models(
    isolated_model_config, providers, tmp_path, command
):
    _, local = isolated_model_config
    local.write_text("[models")
    report = tmp_path / "report.json"
    report.write_text(json.dumps({"model": "default", "provider": "mock", "steps": []}))
    result = runner.invoke(app, [command, str(report)])
    assert result.exit_code == 0, result.output
    providers[0].assert_not_called()
