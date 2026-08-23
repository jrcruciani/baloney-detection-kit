"""Tests for Azure Foundry provider routing and behavior."""

from __future__ import annotations

import os
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
from openai import BadRequestError

from robopsych.providers import UnsupportedProviderOption, create_provider, detect_provider


@pytest.fixture
def foundry_env() -> dict[str, str]:
    return {
        "AZURE_FOUNDRY_ENDPOINT": "https://csajlf.services.ai.azure.com/api/projects/proj-default",
        "AZURE_FOUNDRY_API_KEY": "test-key",
        "AZURE_FOUNDRY_API_VERSION": "2024-05-01-preview",
    }


class TestAzureFoundryRouting:
    def test_routes_deepseek_model_to_foundry_chat_sdk(self, foundry_env):
        with patch.dict(os.environ, foundry_env, clear=False):
            provider = create_provider("deepseek-r1", api_key="test-key")
            assert provider.name == "azure_foundry"
            assert detect_provider("deepseek-r1") == "azure_foundry"

    def test_routes_gpt_model_to_foundry_responses_sdk(self, foundry_env):
        with patch.dict(os.environ, foundry_env, clear=False):
            provider = create_provider("gpt-5", api_key="test-key")
            assert provider.name == "azure_foundry"
            assert detect_provider("gpt-5") == "azure_foundry"

    def test_raises_unsupported_when_response_format_unsupported_by_family(self, foundry_env):
        with patch.dict(os.environ, foundry_env, clear=False):
            provider = create_provider("mistral-large", api_key="test-key")
            with pytest.raises(UnsupportedProviderOption):
                provider.send(
                    [{"role": "user", "content": "hello"}],
                    model="mistral-large",
                    response_format={"type": "json_object"},
                )


class TestAzureFoundrySend:
    def test_deepseek_send_uses_chat_completions(self, foundry_env):
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="pong"))]
        )
        fake_client = SimpleNamespace()
        fake_client.chat = SimpleNamespace()
        fake_client.chat.completions = SimpleNamespace(create=lambda **kwargs: fake_response)

        with (
            patch.dict(os.environ, foundry_env, clear=False),
            patch("robopsych.providers.OpenAI", return_value=fake_client) as openai_ctor,
        ):
            provider = create_provider("deepseek-r1", api_key="test-key")
            text = provider.send(
                [{"role": "user", "content": "say pong"}],
                model="deepseek-r1",
            )

        assert text == "pong"
        assert openai_ctor.call_count == 1
        assert openai_ctor.call_args.kwargs["base_url"].endswith("/models")
        assert openai_ctor.call_args.kwargs["default_query"]["api-version"] == "2024-05-01-preview"

    def test_deepseek_send_uses_deployment_override(self, foundry_env):
        captured = {}
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="pong"))]
        )
        fake_client = SimpleNamespace()
        fake_client.chat = SimpleNamespace()
        fake_client.chat.completions = SimpleNamespace(
            create=lambda **kwargs: captured.update(kwargs) or fake_response
        )

        with (
            patch.dict(os.environ, foundry_env, clear=False),
            patch("robopsych.providers.OpenAI", return_value=fake_client),
        ):
            provider = create_provider(
                "deepseek-r1",
                api_key="test-key",
                deployment="custom-deepseek",
            )
            text = provider.send(
                [{"role": "user", "content": "say pong"}],
                model="deepseek-r1",
            )

        assert text == "pong"
        assert captured["model"] == "custom-deepseek"

    def test_gpt_send_uses_responses(self, foundry_env):
        fake_response = SimpleNamespace(
            output=[SimpleNamespace(content=[SimpleNamespace(text="pong")])]
        )
        fake_client = SimpleNamespace()
        fake_client.responses = SimpleNamespace(create=lambda **kwargs: fake_response)

        with (
            patch.dict(os.environ, foundry_env, clear=False),
            patch("robopsych.providers.OpenAI", return_value=fake_client) as openai_ctor,
        ):
            provider = create_provider("gpt-5", api_key="test-key")
            text = provider.send(
                [{"role": "user", "content": "say pong"}],
                model="gpt-5",
            )

        assert text == "pong"
        assert openai_ctor.call_count == 1
        assert openai_ctor.call_args.kwargs["base_url"].endswith("/openai")
        assert openai_ctor.call_args.kwargs["default_query"]["api-version"] == "2024-05-01-preview"

    def test_gpt_send_uses_deployment_override(self, foundry_env):
        captured = {}
        fake_response = SimpleNamespace(
            output=[SimpleNamespace(content=[SimpleNamespace(text="pong")])]
        )
        fake_client = SimpleNamespace()
        fake_client.responses = SimpleNamespace(
            create=lambda **kwargs: captured.update(kwargs) or fake_response
        )

        with (
            patch.dict(os.environ, foundry_env, clear=False),
            patch("robopsych.providers.OpenAI", return_value=fake_client),
        ):
            provider = create_provider(
                "gpt-5",
                api_key="test-key",
                deployment="custom-gpt",
            )
            text = provider.send(
                [{"role": "user", "content": "say pong"}],
                model="gpt-5",
            )

        assert text == "pong"
        assert captured["model"] == "custom-gpt"

    def test_gpt_send_retries_without_temperature_when_responses_rejects_it(self, foundry_env):
        fake_response = SimpleNamespace(
            output=[SimpleNamespace(content=[SimpleNamespace(text="pong")])]
        )
        calls = []

        def create(**kwargs):
            calls.append(kwargs.copy())
            if len(calls) == 1:
                raise BadRequestError(
                    "Unsupported parameter: 'temperature' is not supported with this model.",
                    response=httpx.Response(
                        400,
                        request=httpx.Request("POST", "https://example.com"),
                    ),
                    body={},
                )
            return fake_response

        fake_client = SimpleNamespace()
        fake_client.responses = SimpleNamespace(create=create)

        with (
            patch.dict(os.environ, foundry_env, clear=False),
            patch("robopsych.providers.OpenAI", return_value=fake_client),
        ):
            provider = create_provider("gpt-5", api_key="test-key")
            text = provider.send(
                [{"role": "user", "content": "say pong"}],
                model="gpt-5",
                temperature=0.3,
            )

        assert text == "pong"
        assert len(calls) == 2
        assert "temperature" not in calls[1]
