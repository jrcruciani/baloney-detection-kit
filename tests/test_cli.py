"""Smoke tests for CLI commands."""

import os
import subprocess
import sys
import textwrap
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from bdk import __version__
from bdk.cli import app
from bdk.interventions import get_intervention, list_interventions

runner = CliRunner()


@pytest.mark.usefixtures("provider_env")
class TestOptionalSDKs:
    def test_clean_import_and_apply_without_any_sdk(self):
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                textwrap.dedent("""
                import sys

                assert "bdk.cli" not in sys.modules
                assert "bdk.providers" not in sys.modules
                for name in ("anthropic", "openai", "google", "google.genai"):
                    sys.modules[name] = None

                import bdk.cli
                from typer.testing import CliRunner

                result = CliRunner().invoke(bdk.cli.app, ["apply", "compact"])
                assert result.exit_code == 0, result.output
                assert "Compact Prompt" in result.output
                assert "proportionate epistemic friction" in result.output
                for variant in ("compact", "full"):
                    result = CliRunner().invoke(
                        bdk.cli.app, ["apply", variant, "--lang", "es"]
                    )
                    assert result.exit_code == 0, result.output
                    assert "fricción epistémica proporcionada" in result.output
                    assert "<!-- bdk prompt-v2.0 -->" in result.output
                for name in ("anthropic", "openai", "google", "google.genai"):
                    assert sys.modules[name] is None
            """),
            ],
            env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": os.pathsep.join(sys.path)},
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    @pytest.mark.parametrize(
        "command",
        [
            ["run", "1.1", "--response", "test response"],
            ["crosscheck", "--task", "test task"],
        ],
    )
    @pytest.mark.parametrize(
        "model,provider,extra",
        [
            ("claude-sonnet-4-6", "anthropic", "anthropic"),
            ("gpt-4o", "openai", "openai"),
            ("gemini-pro", "gemini", "gemini"),
            ("azure/gpt-5", "azure_foundry", "openai"),
        ],
    )
    def test_missing_sdk_has_clean_install_hint(self, monkeypatch, command, model, provider, extra):
        for name in ("anthropic", "openai", "google", "google.genai"):
            monkeypatch.setitem(sys.modules, name, None)
        if provider == "azure_foundry":
            monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://example.services.ai.azure.com")

        result = runner.invoke(app, [*command, "--model", model, "--api-key", "test-key"])

        assert result.exit_code == 1
        assert isinstance(result.exception, SystemExit)
        assert result.output.strip() == (
            f'Provider "{provider}" requires: pip install "baloney-detection-kit[{extra}]"'
        )

    @pytest.mark.parametrize(
        "command",
        [
            ["crosscheck", "--task", "test task", "--judge", "claude-sonnet-4-6"],
            ["ratchet", "--response", "test response", "--coherence-judge", "claude-sonnet-4-6"],
        ],
    )
    def test_missing_judge_sdk_has_clean_install_hint(self, monkeypatch, openai_sdk, command):
        monkeypatch.setitem(sys.modules, "anthropic", None)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        openai_sdk.OpenAI.return_value.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="diagnostic response"))],
        )

        result = runner.invoke(app, [*command, "--model", "gpt-4o", "--api-key", "test-key"])

        assert result.exit_code == 1
        assert isinstance(result.exception, SystemExit)
        assert (
            'Provider "anthropic" requires: pip install "baloney-detection-kit[anthropic]"'
        ) in result.output
        assert "Traceback" not in result.output


class TestApplyCommand:
    def test_no_options_preserve_english_compact(self):
        default = runner.invoke(app, ["apply"])
        explicit = runner.invoke(app, ["apply", "compact", "--lang", "en"])
        assert default.exit_code == explicit.exit_code == 0
        assert default.output == explicit.output

    @pytest.mark.parametrize("variant", ["compact", "full"])
    def test_spanish_stdout(self, variant):
        result = runner.invoke(app, ["apply", variant, "--lang", "es"])
        assert result.exit_code == 0
        assert result.output.startswith("<!-- bdk prompt-v2.0 -->\n")
        assert "fricción epistémica proporcionada" in result.output
        assert "GATE 1" in result.output
        assert "GATE 2" in result.output
        assert "Add proportionate epistemic friction" not in result.output

    @pytest.mark.parametrize("lang", ["en", "es"])
    def test_default_variant_is_compact(self, lang):
        default = runner.invoke(app, ["apply", "--lang", lang])
        explicit = runner.invoke(app, ["apply", "compact", "--lang", lang])
        assert default.exit_code == explicit.exit_code == 0
        assert default.output == explicit.output

    @pytest.mark.parametrize("variant", list_interventions())
    def test_default_language_remains_english(self, variant):
        default = runner.invoke(app, ["apply", variant])
        explicit = runner.invoke(app, ["apply", variant, "--lang", "en"])
        assert default.exit_code == explicit.exit_code == 0
        assert default.output == explicit.output
        assert "GATE 1" in default.output

    @pytest.mark.parametrize(
        "lang,variant",
        [(lang, variant) for lang in ("en", "es") for variant in list_interventions(lang=lang)],
    )
    def test_output_file_preserves_exact_prompt(self, tmp_path, lang, variant):
        output = tmp_path / "prompt.md"
        result = runner.invoke(app, ["apply", variant, "--lang", lang, "--output", str(output)])
        assert result.exit_code == 0
        assert output.read_bytes() == get_intervention(variant, lang=lang).encode("utf-8")
        assert "Intervention saved to" in result.output
        assert "<!-- bdk prompt-v2.0 -->" not in result.output

    @pytest.mark.parametrize("lang", ["unknown", "pt", "fr", "", "ES", "../en", "/en"])
    def test_invalid_language_errors_without_writing(self, tmp_path, lang):
        output = tmp_path / "prompt.md"
        output.write_text("Keep existing content", encoding="utf-8")
        result = runner.invoke(app, ["apply", "full", "--lang", lang, "--output", str(output)])
        assert result.exit_code == 1
        assert isinstance(result.exception, SystemExit)
        assert "Unsupported intervention language" in result.output
        assert "en, es" in result.output
        assert "Traceback" not in result.output
        assert "<!-- bdk prompt-" not in result.output
        assert output.read_text(encoding="utf-8") == "Keep existing content"

    @pytest.mark.parametrize("lang", ["en", "es"])
    @pytest.mark.parametrize("variant", ["unknown", "../prompt-full", "/full", "es/full"])
    def test_invalid_variant_errors_without_writing(self, tmp_path, lang, variant):
        output = tmp_path / "prompt.md"
        result = runner.invoke(app, ["apply", variant, "--lang", lang, "--output", str(output)])
        assert result.exit_code == 1
        assert isinstance(result.exception, SystemExit)
        assert "not found for language" in result.output
        assert "Traceback" not in result.output
        assert not output.exists()

    @pytest.mark.parametrize("variant", ["high-stakes", "agent", "reviewer", "second-opinion"])
    def test_unavailable_spanish_variant_errors_without_fallback(self, tmp_path, variant):
        output = tmp_path / "prompt.md"
        result = runner.invoke(app, ["apply", variant, "--lang", "es", "--output", str(output)])
        assert result.exit_code == 1
        assert isinstance(result.exception, SystemExit)
        assert "not found for language 'es'" in result.output
        assert "compact, full" in " ".join(result.output.split())
        assert "<!-- bdk prompt-" not in result.output
        assert not output.exists()


class TestListCommand:
    def test_list_runs(self):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Calvin" in result.output

    def test_list_shows_all_prompts(self):
        result = runner.invoke(app, ["list"])
        assert "1.1" in result.output
        assert "4.3" in result.output

    def test_list_by_level(self):
        result = runner.invoke(app, ["list", "--by-level"])
        assert result.exit_code == 0
        assert "Calvin" in result.output

    def test_list_default_groups_by_observation(self):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        # Should show observation labels from flowchart
        assert "Evasion" in result.output or "refusal" in result.output.lower()

    def test_list_default_respects_diagnostic_only(self):
        result = runner.invoke(app, ["list", "--diagnostic-only"])
        assert result.exit_code == 0
        assert "1.1" in result.output
        assert "1.2d" in result.output

    def test_list_default_respects_intervention_only(self):
        result = runner.invoke(app, ["list", "--intervention-only"])
        assert result.exit_code == 0
        assert "1.2" in result.output
        assert "1.1" not in result.output
        assert "1.2d" not in result.output

    def test_list_rejects_conflicting_filters(self):
        result = runner.invoke(
            app,
            ["list", "--diagnostic-only", "--intervention-only"],
        )
        assert result.exit_code == 1


class TestShowCommand:
    def test_show_existing_prompt(self):
        result = runner.invoke(app, ["show", "1.1"])
        assert result.exit_code == 0
        assert "Calvin" in result.output

    def test_show_nonexistent_prompt(self):
        result = runner.invoke(app, ["show", "99.99"])
        assert result.exit_code == 1

    def test_show_displays_template(self):
        result = runner.invoke(app, ["show", "1.1"])
        assert "second intention diagnosis" in result.output.lower()


class TestRunCommand:
    def test_run_requires_response(self):
        result = runner.invoke(app, ["run", "1.1"])
        assert result.exit_code != 0

    @patch("bdk.cli.create_provider")
    def test_run_with_response(self, mock_create):
        mock_provider = MagicMock()
        mock_provider.name = "mock"
        mock_provider.send.return_value = "Diagnostic result here."
        mock_create.return_value = mock_provider

        result = runner.invoke(
            app,
            [
                "run",
                "1.1",
                "--response",
                "test response",
                "--model",
                "mock-model",
            ],
        )
        assert result.exit_code == 0
        assert "Diagnostic result here." in result.output


class TestReadInputLimits:
    @pytest.mark.parametrize("source", ["text", "file", "stdin"])
    @pytest.mark.parametrize("max_bytes", [None, 4])
    def test_reads_valid_input(self, source, max_bytes, tmp_path, monkeypatch):
        from io import StringIO

        from bdk.cli import _read_input

        text = "abcd"
        path = tmp_path / "response.txt"
        path.write_text(text, encoding="utf-8")
        monkeypatch.setattr(sys, "stdin", StringIO(text))

        assert (
            _read_input(
                text if source == "text" else None,
                path if source == "file" else None,
                max_bytes=max_bytes,
            )
            == text
        )

    def test_response_text_limit(self):
        import typer

        from bdk.cli import _read_input

        with pytest.raises(typer.BadParameter, match="--response exceeds"):
            _read_input("abcd", None, max_bytes=3)

    def test_response_file_limit(self, tmp_path):
        import typer

        from bdk.cli import _read_input

        p = tmp_path / "response.txt"
        p.write_text("abcd")
        with pytest.raises(typer.BadParameter, match="exceeds"):
            _read_input(None, p, max_bytes=3)

    def test_stdin_limit(self, monkeypatch):
        import sys
        from io import StringIO

        import typer

        from bdk.cli import _read_input

        stream = StringIO("abcd")
        stream.isatty = lambda: False
        monkeypatch.setattr(sys, "stdin", stream)
        with pytest.raises(typer.BadParameter, match="stdin exceeds"):
            _read_input(None, None, max_bytes=3)


class TestRatchetSessionPersistence:
    @pytest.mark.parametrize("resume", [False, True])
    @patch("bdk.cli.create_provider")
    def test_saves_completed_steps(self, mock_create, resume, tmp_path):
        from bdk.session import SessionState

        provider = MagicMock()
        provider.name = "mock"
        provider.send.return_value = "[Observed] This is a diagnostic response."
        mock_create.return_value = provider
        path = tmp_path / "ratchet.json"
        if resume:
            SessionState.create(provider_name="mock", model="mock-model", sequence=["1.1"]).save(
                path
            )
            args = ["--resume", str(path)]
        else:
            args = ["--session", str(path), "--response", "Initial response."]

        result = runner.invoke(app, ["ratchet", "--model", "mock-model", *args])

        assert result.exit_code == 0, result.output
        saved = SessionState.load(path)
        assert saved.completed_steps
        assert saved.remaining_steps == []
        assert len(saved.completed_steps) == provider.send.call_count
        assert saved.messages[-1]["content"] == provider.send.return_value


class TestNoArgsShowsWelcome:
    def test_no_args_shows_welcome(self):
        result = runner.invoke(app, [])
        assert result.exit_code == 0
        assert "bdk" in result.output.lower()
        assert f"v{__version__}" in result.output


class TestRegexCoherenceWarning:
    """Issue #9: warn when regex coherence is used on multi-step ratchets."""

    def _make_session_json(self, tmp_path, n_steps: int):
        import json

        steps = [
            {
                "prompt_id": f"p{i}",
                "prompt_name": f"step-{i}",
                "prompt_text": "",
                "response": f"Response {i}. As I mentioned before, things are fine.",
            }
            for i in range(n_steps)
        ]
        report = {
            "provider": "mock",
            "model": "mock-model",
            "steps": steps,
            "initial_response": None,
        }
        f = tmp_path / "session.json"
        f.write_text(json.dumps(report))
        return f

    def test_warning_helper_emits_for_4_plus_steps(self, capsys):
        from io import StringIO

        from rich.console import Console

        from bdk.cli import _warn_regex_coherence_if_applicable

        buf = StringIO()
        console = Console(file=buf, force_terminal=False, width=120)

        assert _warn_regex_coherence_if_applicable(4, console) is True
        out = buf.getvalue()
        assert "WARNING" in out
        assert "regex heuristics" in out
        assert "--coherence-judge" in out
        assert "case-03-ratchet-coherence" in out

    def test_warning_helper_silent_below_threshold(self):
        from io import StringIO

        from rich.console import Console

        from bdk.cli import _warn_regex_coherence_if_applicable

        for n in (0, 1, 2, 3):
            buf = StringIO()
            console = Console(file=buf, force_terminal=False, width=120)
            assert _warn_regex_coherence_if_applicable(n, console) is False
            assert buf.getvalue() == ""

    def test_coherence_subcommand_warns_on_multi_step_session(self, tmp_path):
        session = self._make_session_json(tmp_path, n_steps=5)
        result = runner.invoke(app, ["coherence", str(session)])
        assert result.exit_code == 0
        assert "WARNING" in result.output
        assert "--coherence-judge" in result.output

    def test_coherence_subcommand_silent_on_short_session(self, tmp_path):
        session = self._make_session_json(tmp_path, n_steps=2)
        result = runner.invoke(app, ["coherence", str(session)])
        assert result.exit_code == 0
        assert "WARNING" not in result.output

    def test_markdown_report_embeds_warning_when_regex_used(self):
        from bdk.coherence import analyze_coherence
        from bdk.engine import DiagnosticEngine, DiagnosticStep
        from bdk.report import generate_report

        engine = DiagnosticEngine.__new__(DiagnosticEngine)
        engine.steps = [
            DiagnosticStep(
                prompt_id=f"p{i}",
                prompt_name=f"step-{i}",
                prompt_text="",
                response=f"Response {i}.",
            )
            for i in range(5)
        ]
        engine.model = "mock-model"
        engine.messages = []
        engine.initial_response = None
        engine.provider = type("_", (), {"name": "mock"})()

        coh = analyze_coherence(engine)
        md = generate_report(engine, "test", coherence=coh)
        assert "regex heuristics" in md
        assert "WARNING" in md
        assert "--coherence-judge" in md
        assert "case-03-ratchet-coherence" in md

    def test_markdown_report_no_warning_for_short_session(self):
        from bdk.coherence import analyze_coherence
        from bdk.engine import DiagnosticEngine, DiagnosticStep
        from bdk.report import generate_report

        engine = DiagnosticEngine.__new__(DiagnosticEngine)
        engine.steps = [
            DiagnosticStep(
                prompt_id=f"p{i}",
                prompt_name=f"step-{i}",
                prompt_text="",
                response=f"Response {i}.",
            )
            for i in range(2)
        ]
        engine.model = "mock-model"
        engine.messages = []
        engine.initial_response = None
        engine.provider = type("_", (), {"name": "mock"})()

        coh = analyze_coherence(engine)
        md = generate_report(engine, "test", coherence=coh)
        assert "regex heuristics" in md
        assert "WARNING" not in md

    def test_markdown_report_no_warning_for_llm_judge(self):
        from bdk.coherence_llm import LLMCoherenceReport
        from bdk.engine import DiagnosticEngine, DiagnosticStep
        from bdk.report import generate_report

        engine = DiagnosticEngine.__new__(DiagnosticEngine)
        engine.steps = [
            DiagnosticStep(
                prompt_id=f"p{i}",
                prompt_name=f"step-{i}",
                prompt_text="",
                response=f"Response {i}.",
            )
            for i in range(9)
        ]
        engine.model = "mock-model"
        engine.messages = []
        engine.initial_response = None
        engine.provider = type("_", (), {"name": "mock"})()

        coh = LLMCoherenceReport(
            consistency_score=0.7,
            assessment="genuine",
            backward_references=50,
            contradictions=[],
            fresh_narratives=2,
            details="",
            judge_model="claude-opus-4-5",
        )
        md = generate_report(engine, "test", coherence=coh)
        assert "LLM judge" in md
        assert "WARNING" not in md


class TestRatchetBehavioral:
    @patch("bdk.crosscheck.run_ab_test")
    @patch("bdk.cli.create_provider")
    def test_behavioral_crosscheck_uses_scenario_system_prompt(
        self, mock_create, mock_run_ab_test, tmp_path
    ):
        from bdk.crosscheck import ABTestResult

        scenario = tmp_path / "scenario.yaml"
        scenario.write_text(
            "name: prompt propagation\nsystem_prompt: Use BDK.\ntask: Test this claim.\n",
            encoding="utf-8",
        )

        mock_provider = MagicMock()
        mock_provider.name = "mock"
        mock_provider.send.return_value = "Diagnostic result here."
        mock_create.return_value = mock_provider
        mock_run_ab_test.return_value = ABTestResult(
            original_task="Test this claim.",
            inverted_task="Inverted task.",
            original_response="Original response.",
            inverted_response="Inverted response.",
            comparison="No material change.",
            substance_changed=False,
        )

        result = runner.invoke(
            app,
            [
                "ratchet",
                "--scenario",
                str(scenario),
                "--model",
                "mock-model",
                "--behavioral",
            ],
        )

        assert result.exit_code == 0
        assert mock_run_ab_test.call_args.kwargs["system_prompt"] == "Use BDK."
