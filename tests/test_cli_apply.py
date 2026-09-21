"""Exact machine-readable and plain intervention output, without provider SDKs."""

import json
import os
import stat

import pytest
from typer.testing import CliRunner

from bdk.cli import app
from bdk.interventions import get_intervention, list_interventions

runner = CliRunner()
pytestmark = pytest.mark.usefixtures("isolated_model_config")
VARIANTS = [(lang, variant) for lang in ("en", "es") for variant in list_interventions(lang=lang)]


@pytest.mark.parametrize("lang,variant", VARIANTS)
@pytest.mark.parametrize("format", ["plain", "json"])
def test_exact_stdout(lang, variant, format, monkeypatch):
    monkeypatch.setenv("COLUMNS", "20")
    monkeypatch.setenv("FORCE_COLOR", "1")
    result = runner.invoke(app, ["apply", variant, "--lang", lang, "--format", format], color=True)
    prompt = get_intervention(variant, lang=lang)
    assert result.exit_code == 0, result.output
    assert result.stderr == ""
    assert "\x1b" not in result.stdout
    if format == "json":
        assert json.loads(result.stdout) == {
            "variant": variant,
            "prompt_version": "prompt-v2.0",
            "lang": lang,
            "content": prompt,
        }
        assert result.stdout.encode("utf-8") == (
            json.dumps(json.loads(result.stdout), ensure_ascii=False) + "\n"
        ).encode("utf-8")
    else:
        assert result.stdout.encode("utf-8") == prompt.encode("utf-8")
    if lang == "es":
        assert any(ord(char) > 127 for char in prompt)


@pytest.mark.parametrize("lang", ["en", "es"])
def test_json_default_variant(lang):
    result = runner.invoke(app, ["apply", "--lang", lang, "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["variant"] == "compact"


@pytest.mark.parametrize("lang", ["en", "es"])
@pytest.mark.parametrize("format", ["plain", "json"])
def test_lists_available_variants_and_versions(lang, format):
    result = runner.invoke(app, ["apply", "--list", "--lang", lang, "--format", format])
    assert result.exit_code == 0, result.output
    entries = [
        {"variant": variant, "prompt_version": "prompt-v2.0", "lang": lang}
        for variant in list_interventions(lang=lang)
    ]
    if format == "json":
        assert json.loads(result.stdout) == entries
    else:
        assert result.stdout == "".join(
            f"{entry['variant']}\t{entry['prompt_version']}\t{lang}\n" for entry in entries
        )
    assert result.stderr == ""


@pytest.mark.parametrize("lang", ["en", "es"])
@pytest.mark.parametrize("format", ["plain", "json"])
@pytest.mark.parametrize("listing", [False, True])
def test_output_file_matches_stdout_and_is_private(tmp_path, lang, format, listing):
    args = ["apply", *(["--list"] if listing else ["full"]), "--lang", lang, "--format", format]
    stdout = runner.invoke(app, args)
    output = tmp_path / "nested" / "prompt.txt"
    result = runner.invoke(app, [*args, "--output", str(output)])
    assert stdout.exit_code == result.exit_code == 0, result.output
    assert output.read_bytes() == stdout.stdout.encode("utf-8")
    assert result.stdout == ""
    assert "Intervention saved to" in result.stderr
    if os.name == "posix":
        assert stat.S_IMODE(output.stat().st_mode) == 0o600


def test_overwritten_output_gets_private_permissions(tmp_path):
    output = tmp_path / "prompt.json"
    output.write_text("Old content.")
    output.chmod(0o644)
    result = runner.invoke(app, ["apply", "--format", "json", "--output", str(output)])
    assert result.exit_code == 0, result.output
    assert json.loads(output.read_text())["content"] == get_intervention("compact")
    if os.name == "posix":
        assert stat.S_IMODE(output.stat().st_mode) == 0o600


@pytest.mark.parametrize(
    "args",
    [
        ["--format", "yaml"],
        ["--format", "JSON"],
        ["--format", ""],
        ["--list", "--format", "markdown"],
        ["compact", "--list"],
        ["unknown", "--list", "--format", "json"],
        ["--list", "--lang", "fr", "--format", "json"],
        ["full", "--lang", "ES", "--format", "json"],
        ["unknown", "--format", "json"],
        ["agent", "--lang", "es", "--format", "json"],
        ["", "--format", "json"],
    ],
)
def test_invalid_options_are_clean_and_do_not_write(args, tmp_path):
    output = tmp_path / "existing.txt"
    output.write_text("Keep this.")
    result = runner.invoke(app, ["apply", *args, "--output", str(output)])
    assert result.exit_code in (1, 2)
    assert isinstance(result.exception, SystemExit)
    assert result.stdout == ""
    assert result.stderr
    assert "Traceback" not in result.stderr
    assert output.read_text() == "Keep this."


def test_private_write_failure_is_explicit(monkeypatch, tmp_path):
    def fail(*args):
        raise PermissionError("test write denied")

    monkeypatch.setattr("bdk.cli.private_write_text", fail)
    result = runner.invoke(app, ["apply", "--format", "json", "--output", str(tmp_path / "out")])
    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert result.stdout == ""
    assert "test write denied" in result.stderr


@pytest.mark.parametrize("listing", [False, True])
@pytest.mark.parametrize("lang", ["en", "es"])
def test_metadata_comes_from_packaged_marker(monkeypatch, listing, lang):
    prompt = "<!-- bdk prompt-v9.7 -->\n[red]literal[/red]\nUnicode: \u00f1, \u2014\n\n"
    monkeypatch.setattr("bdk.cli.get_intervention", lambda *args, **kwargs: prompt)
    result = runner.invoke(
        app, ["apply", *(["--list"] if listing else []), "--lang", lang, "--format", "json"]
    )
    assert result.exit_code == 0, result.output
    data = json.loads(result.stdout)
    if listing:
        assert all(entry["prompt_version"] == "prompt-v9.7" for entry in data)
    else:
        assert data["prompt_version"] == "prompt-v9.7"
        assert data["content"] == prompt
        plain = runner.invoke(app, ["apply", "--lang", lang])
        assert plain.stdout == prompt


@pytest.mark.parametrize(
    "prompt",
    ["No marker.", "\n<!-- bdk prompt-v2.0 -->\n", "<!-- bdk prompt-v2.0 -->\n" * 2],
)
@pytest.mark.parametrize("listing", [False, True])
def test_invalid_markers_do_not_produce_success_metadata(monkeypatch, prompt, listing):
    monkeypatch.setattr("bdk.cli.get_intervention", lambda *args, **kwargs: prompt)
    result = runner.invoke(app, ["apply", *(["--list"] if listing else []), "--format", "json"])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "version marker" in result.stderr
