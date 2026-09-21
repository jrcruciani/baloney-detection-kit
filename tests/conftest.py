"""Opt-in SDK doubles; unit tests never need installed provider SDKs."""

import os
import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def isolated_model_config(tmp_path, monkeypatch):
    """Keep CLI configuration reads and writes away from the developer's files."""
    home = tmp_path / "home"
    cwd = tmp_path / "work"
    home.mkdir()
    cwd.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.chdir(cwd)
    user = home / ".config" / "bdk" / "config.toml"
    user.parent.mkdir(parents=True)
    return user, cwd / "bdk.toml"


@pytest.fixture
def provider_env(monkeypatch):
    for name in os.environ:
        if (
            name.startswith(
                (
                    "ANTHROPIC_",
                    "OPENAI_",
                    "GEMINI_",
                    "GOOGLE_",
                    "AZURE_FOUNDRY_",
                )
            )
            or name == "ROBOPSYCH_ALLOW_INSECURE_BASE_URL"
        ):
            monkeypatch.delenv(name)


@pytest.fixture
def anthropic_sdk(monkeypatch):
    sdk = ModuleType("anthropic")
    sdk.Anthropic = MagicMock()
    monkeypatch.setitem(sys.modules, "anthropic", sdk)
    return sdk


@pytest.fixture
def openai_sdk(monkeypatch):
    class BadRequestError(Exception):
        pass

    sdk = ModuleType("openai")
    sdk.OpenAI = MagicMock()
    sdk.AzureOpenAI = MagicMock()
    sdk.BadRequestError = BadRequestError
    monkeypatch.setitem(sys.modules, "openai", sdk)
    return sdk
