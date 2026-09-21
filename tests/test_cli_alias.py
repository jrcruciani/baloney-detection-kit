"""Both declared entry points preserve commands and exact pipeline output."""

import importlib
import json
import tomllib
from pathlib import Path

import pytest
from rich.text import Text
from typer.testing import CliRunner

from bdk.interventions import get_intervention, list_interventions

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]
runner = CliRunner()
pytestmark = pytest.mark.usefixtures("isolated_model_config", "provider_env")


@pytest.fixture(params=["bdk", "robopsych"])
def entrypoint(request):
    name = request.param
    module, attribute = SCRIPTS[name].split(":")
    return name, getattr(importlib.import_module(module), attribute)


@pytest.mark.parametrize("force_color", [False, True])
def test_help_deprecates_only_the_alias(entrypoint, force_color, monkeypatch):
    if force_color:
        monkeypatch.setenv("FORCE_COLOR", "1")
        monkeypatch.delenv("NO_COLOR", raising=False)
    else:
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.delenv("FORCE_COLOR", raising=False)
    name, app = entrypoint
    result = runner.invoke(app, ["--help"], prog_name=name, terminal_width=160, color=True)
    assert result.exit_code == 0, result.output
    help_text = " ".join(Text.from_ansi(result.stdout).plain.split())
    assert f"Usage: {name}" in help_text
    assert "bdk is the canonical executable." in help_text
    assert "Only the robopsych alias is deprecated:" in help_text
    assert "compatible throughout BDK 3.x" in help_text
    assert "will be removed in 4.0" in help_text
    assert "Use bdk instead." in help_text
    assert result.stderr == ""


@pytest.mark.parametrize(
    "lang,variant",
    [(lang, variant) for lang in ("en", "es") for variant in list_interventions(lang=lang)],
)
@pytest.mark.parametrize("format", ["plain", "json"])
def test_entrypoint_apply_preserves_exact_stdout(entrypoint, lang, variant, format):
    name, app = entrypoint
    result = runner.invoke(
        app, ["apply", variant, "--lang", lang, "--format", format], prog_name=name
    )
    prompt = get_intervention(variant, lang=lang)
    expected = (
        json.dumps(
            {"variant": variant, "prompt_version": "prompt-v2.0", "lang": lang, "content": prompt},
            ensure_ascii=False,
        )
        + "\n"
        if format == "json"
        else prompt
    )
    assert result.exit_code == 0, result.output
    assert result.stdout.encode("utf-8") == expected.encode("utf-8")
    assert result.stderr == ""


def test_legacy_diagnostic_command_matches_canonical_output():
    module, attribute = SCRIPTS["bdk"].split(":")
    canonical = runner.invoke(
        getattr(importlib.import_module(module), attribute), ["list"], prog_name="bdk"
    )
    module, attribute = SCRIPTS["robopsych"].split(":")
    legacy = runner.invoke(
        getattr(importlib.import_module(module), attribute), ["list"], prog_name="robopsych"
    )
    assert canonical.exit_code == legacy.exit_code == 0
    assert canonical.stdout == legacy.stdout
    assert "1.1" in legacy.stdout
    assert "deprecated" not in legacy.stdout
    assert canonical.stderr == legacy.stderr == ""
