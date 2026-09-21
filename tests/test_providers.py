"""Tests for provider detection, creation, and Gemini requests."""

import importlib.util
import os
import sys
from dataclasses import dataclass
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call, patch

import pytest

from bdk import providers
from bdk.providers import (
    GeminiProvider,
    UnsupportedProviderOption,
    create_provider,
    detect_provider,
)


@pytest.fixture
def gemini_sdk(monkeypatch):
    @dataclass
    class Part:
        text: str

    @dataclass
    class Content:
        role: str
        parts: list[Part]

    @dataclass
    class GenerateContentConfig:
        system_instruction: str | None = None
        temperature: float | None = None
        response_mime_type: str | None = None

    def create_client(*, api_key):
        return SimpleNamespace(
            models=SimpleNamespace(
                generate_content=Mock(return_value=SimpleNamespace(text="pong")),
            ),
        )

    google = ModuleType("google")
    genai = ModuleType("google.genai")
    types = ModuleType("google.genai.types")
    types.Part = Part
    types.Content = Content
    types.GenerateContentConfig = GenerateContentConfig
    genai.Client = Mock(side_effect=create_client)
    genai.types = types
    google.genai = genai
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.genai", genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", types)
    return genai


class TestDetectProvider:
    def test_claude_models(self):
        assert detect_provider("claude-sonnet-4-6") == "anthropic"
        assert detect_provider("claude-3-opus") == "anthropic"
        assert detect_provider("claude-haiku") == "anthropic"

    def test_gpt_models(self):
        assert detect_provider("gpt-4o") == "openai"
        assert detect_provider("gpt-3.5-turbo") == "openai"

    def test_o_series_models(self):
        assert detect_provider("o1-preview") == "openai"
        assert detect_provider("o3-mini") == "openai"
        assert detect_provider("o4-mini") == "openai"

    def test_gemini_models(self):
        assert detect_provider("gemini-pro") == "gemini"
        assert detect_provider("gemini-1.5-flash") == "gemini"
        assert detect_provider("gemini-2.0-flash") == "gemini"

    def test_unknown_model_defaults_to_openai(self):
        assert detect_provider("llama-3") == "openai"
        assert detect_provider("mistral-large") == "openai"


class TestCreateProvider:
    def test_anthropic_with_explicit_key(self):
        provider = create_provider("claude-sonnet-4-6", api_key="test-key")
        assert provider.name == "anthropic"

    def test_anthropic_with_env_key(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-key"}):
            provider = create_provider("claude-sonnet-4-6")
            assert provider.name == "anthropic"

    def test_anthropic_without_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
            with patch.dict(os.environ, env, clear=True):
                with pytest.raises(SystemExit):
                    create_provider("claude-sonnet-4-6")

    def test_openai_with_explicit_key(self):
        provider = create_provider("gpt-4o", api_key="test-key")
        assert provider.name == "openai"

    def test_openai_with_env_key(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            provider = create_provider("gpt-4o")
            assert provider.name == "openai"

    def test_openai_with_base_url(self):
        provider = create_provider("gpt-4o", api_key="test-key", base_url="https://api.example.com/v1")
        assert provider.name == "openai"

    def test_openai_rejects_insecure_base_url_without_opt_in(self):
        with pytest.raises(ValueError, match="non-HTTPS"):
            create_provider("gpt-4o", api_key="test-key", base_url="http://localhost:8080")

    def test_openai_allows_insecure_base_url_with_explicit_opt_in(self):
        provider = create_provider(
            "gpt-4o",
            api_key="test-key",
            base_url="http://localhost:8080",
            allow_insecure_base_url=True,
        )
        assert provider.name == "openai"

    def test_openai_allows_insecure_base_url_with_env_opt_in(self):
        with patch.dict(os.environ, {"ROBOPSYCH_ALLOW_INSECURE_BASE_URL": "1"}):
            provider = create_provider(
                "gpt-4o",
                api_key="test-key",
                base_url="http://localhost:8080",
            )
        assert provider.name == "openai"

    def test_openai_without_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
            with patch.dict(os.environ, env, clear=True):
                with pytest.raises(SystemExit):
                    create_provider("gpt-4o")

    def test_gemini_with_explicit_key(self):
        with patch("bdk.providers.GeminiProvider.__init__", return_value=None):
            provider = create_provider("gemini-pro", api_key="test-key")
            assert provider.name == "gemini"

    def test_gemini_with_env_key(self):
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "env-key"}),
            patch("bdk.providers.GeminiProvider.__init__", return_value=None),
        ):
            provider = create_provider("gemini-pro")
            assert provider.name == "gemini"

    def test_gemini_with_google_api_key(self):
        with (
            patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key"}),
            patch("bdk.providers.GeminiProvider.__init__", return_value=None),
        ):
            provider = create_provider("gemini-pro")
            assert provider.name == "gemini"

    def test_gemini_without_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            env = {
                k: v for k, v in os.environ.items()
                if k not in ("GEMINI_API_KEY", "GOOGLE_API_KEY")
            }
            with patch.dict(os.environ, env, clear=True):
                with pytest.raises(SystemExit):
                    create_provider("gemini-pro")


class TestGeminiProvider:
    def test_creates_independent_clients(self, gemini_sdk):
        first = create_provider("gemini-pro", api_key="first-key")
        second = create_provider("gemini-pro", api_key="second-key")

        assert gemini_sdk.Client.call_args_list == [
            call(api_key="first-key"),
            call(api_key="second-key"),
        ]
        assert first.client is not second.client
        assert first.client is not None
        assert first.send([{"role": "user", "content": "hello"}], "gemini-pro") == "pong"
        second.client.models.generate_content.assert_not_called()

    @pytest.mark.parametrize("temperature", [None, 0.0, 0.7])
    @pytest.mark.parametrize("response_format", [None, {"type": "json_object"}])
    def test_send_preserves_history_config_and_text(
        self, gemini_sdk, temperature, response_format,
    ):
        provider = GeminiProvider(api_key="test-key")
        generate = provider.client.models.generate_content
        generate.return_value = SimpleNamespace(text=' {"answer": "pong"} \n')
        messages = [
            {"role": "system", "content": "Follow these instructions."},
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
            {"role": "user", "content": "Follow-up question"},
            {"role": "assistant", "content": "Follow-up answer"},
            {"role": "user", "content": "Final question"},
        ]
        original_messages = [message.copy() for message in messages]

        text = provider.send(
            messages,
            "gemini-pro",
            temperature=temperature,
            response_format=response_format,
        )

        types = gemini_sdk.types
        generate.assert_called_once_with(
            model="gemini-pro",
            contents=[
                types.Content(role="user", parts=[types.Part(text="First question")]),
                types.Content(role="model", parts=[types.Part(text="First answer")]),
                types.Content(role="user", parts=[types.Part(text="Follow-up question")]),
                types.Content(role="model", parts=[types.Part(text="Follow-up answer")]),
                types.Content(role="user", parts=[types.Part(text="Final question")]),
            ],
            config=types.GenerateContentConfig(
                system_instruction="Follow these instructions.",
                temperature=temperature,
                response_mime_type="application/json" if response_format else None,
            ),
        )
        assert text == ' {"answer": "pong"} \n'
        assert messages == original_messages

    def test_send_without_system_or_optional_kwargs(self, gemini_sdk):
        provider = GeminiProvider(api_key="test-key")

        assert provider.send([{"role": "user", "content": "hello"}], "gemini-pro") == "pong"

        types = gemini_sdk.types
        provider.client.models.generate_content.assert_called_once_with(
            model="gemini-pro",
            contents=[types.Content(role="user", parts=[types.Part(text="hello")])],
            config=types.GenerateContentConfig(),
        )

    def test_send_preserves_last_system_instruction(self, gemini_sdk):
        provider = GeminiProvider(api_key="test-key")

        provider.send(
            [
                {"role": "system", "content": "Initial instructions"},
                {"role": "user", "content": "hello"},
                {"role": "system", "content": "Updated instructions"},
            ],
            "gemini-pro",
        )

        types = gemini_sdk.types
        provider.client.models.generate_content.assert_called_once_with(
            model="gemini-pro",
            contents=[types.Content(role="user", parts=[types.Part(text="hello")])],
            config=types.GenerateContentConfig(system_instruction="Updated instructions"),
        )

    @pytest.mark.parametrize("response_format", [
        {},
        {"type": "text"},
        {"type": "json_schema", "json_schema": {"type": "object"}},
    ])
    def test_rejects_unsupported_response_format_before_request(self, gemini_sdk, response_format):
        provider = GeminiProvider(api_key="test-key")

        with pytest.raises(UnsupportedProviderOption, match="does not support response_format"):
            provider.send(
                [{"role": "user", "content": "hello"}],
                "gemini-pro",
                response_format=response_format,
            )

        provider.client.models.generate_content.assert_not_called()

    @pytest.mark.parametrize("response", [
        SimpleNamespace(),
        SimpleNamespace(text=None),
        SimpleNamespace(text=""),
        SimpleNamespace(text=" \n\t"),
        SimpleNamespace(text=123),
    ])
    def test_rejects_unusable_response_text(self, gemini_sdk, response):
        provider = GeminiProvider(api_key="test-key")
        provider.client.models.generate_content.return_value = response

        with pytest.raises(ValueError, match="Gemini response did not contain usable text"):
            provider.send([{"role": "user", "content": "hello"}], "gemini-pro")

    def test_propagates_sdk_errors(self, gemini_sdk):
        provider = GeminiProvider(api_key="test-key")
        provider.client.models.generate_content.side_effect = RuntimeError("SDK request failed")

        with pytest.raises(RuntimeError, match="SDK request failed"):
            provider.send([{"role": "user", "content": "hello"}], "gemini-pro")

    def test_import_does_not_require_gemini_sdk(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "google", None)
        monkeypatch.setitem(sys.modules, "google.genai", None)
        monkeypatch.setitem(sys.modules, "google.genai.types", None)
        spec = importlib.util.spec_from_file_location(
            "providers_without_gemini", providers.__file__,
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)

        assert module.detect_provider("gemini-pro") == "gemini"
        with pytest.raises(ModuleNotFoundError):
            module.GeminiProvider(api_key="test-key")
