"""API providers for model interaction."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlsplit, urlunsplit

try:
    import openai
except ImportError:  # pragma: no cover - optional dependency
    openai = None

from robopsych.security import validate_base_url

OpenAI = openai.OpenAI if openai is not None else None


class UnsupportedProviderOption(Exception):
    """Raised by a provider when a requested optional send() kwarg is not supported.

    Callers (e.g. the LLM judge) catch this to degrade gracefully — for example,
    if a provider does not support response_format, retry without it.
    """


class Provider(ABC):
    """Base provider interface.

    The ``send`` method accepts optional ``temperature`` and ``response_format``
    kwargs. Backward compatibility: providers MUST tolerate calls without them.
    If a provider does not support a requested option, it should raise
    ``UnsupportedProviderOption`` so callers can degrade.
    """

    name: str

    @abstractmethod
    def send(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> str: ...


class AnthropicProvider(Provider):
    name = "anthropic"

    def __init__(self, api_key: str):
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)

    def send(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        system = None
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)

        kwargs: dict = {
            "model": model,
            "messages": chat_messages,
            "max_tokens": 4096,
        }
        if system:
            kwargs["system"] = system
        if temperature is not None:
            kwargs["temperature"] = temperature
        if response_format is not None:
            # Anthropic does not support response_format. Surface as unsupported
            # so the caller can decide to retry without it.
            raise UnsupportedProviderOption(
                "AnthropicProvider does not support response_format; "
                "retry without it."
            )

        response = self.client.messages.create(**kwargs)
        return response.content[0].text


class OpenAIProvider(Provider):
    name = "openai"

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        *,
        allow_insecure_base_url: bool | None = None,
    ):
        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = validate_base_url(
                base_url,
                allow_insecure=allow_insecure_base_url,
            )
        self.client = OpenAI(**kwargs)

    def send(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        kwargs: dict = {
            "model": model,
            "messages": messages,
            "max_tokens": 4096,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        if response_format is not None:
            kwargs["response_format"] = response_format
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content


class AzureFoundryProvider(Provider):
    name = "azure_foundry"

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        api_version: str,
        *,
        family: str,
        deployment: str | None = None,
        allow_insecure_base_url: bool | None = None,
    ):
        self._family = family
        self._deployment = deployment
        self._endpoint = validate_base_url(
            endpoint,
            allow_insecure=allow_insecure_base_url,
        )
        self.client = OpenAI(
            api_key=api_key,
            base_url=self._build_base_url(self._endpoint, family),
            default_query={"api-version": api_version},
        )

    @staticmethod
    def _build_base_url(endpoint: str, family: str) -> str:
        parsed = urlsplit(endpoint)
        path = parsed.path.rstrip("/")

        if family == "gpt":
            if path.endswith("/openai"):
                return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
            if path.endswith("/responses"):
                return urlunsplit(
                    (parsed.scheme, parsed.netloc, path.removesuffix("/responses"), "", "")
                )
            return urlunsplit((parsed.scheme, parsed.netloc, f"{path}/openai", "", ""))

        if path.endswith("/models"):
            return urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
        if path.endswith("/chat/completions"):
            return urlunsplit(
                (parsed.scheme, parsed.netloc, path.removesuffix("/chat/completions"), "", "")
            )
        return urlunsplit((parsed.scheme, parsed.netloc, f"{path}/models", "", ""))

    def _create_responses(self, kwargs: dict[str, Any], *, temperature: float | None) -> Any:
        try:
            return self.client.responses.create(**kwargs)
        except Exception as exc:
            if openai is not None and isinstance(exc, openai.BadRequestError):
                message = str(exc).lower()
                if temperature is not None and "temperature" in message:
                    kwargs.pop("temperature", None)
                    return self.client.responses.create(**kwargs)
            raise

    def send(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        request_model = self._deployment or model
        if self._family == "gpt":
            kwargs: dict[str, Any] = {
                "model": request_model,
                "input": messages,
            }
            if temperature is not None:
                kwargs["temperature"] = temperature
            if response_format is not None:
                rf_type = (response_format or {}).get("type")
                if rf_type != "json_object":
                    raise UnsupportedProviderOption(
                        f"AzureFoundryProvider does not support response_format={response_format!r}"
                    )
                kwargs["text"] = {"format": {"type": "json_object"}}
            response = self._create_responses(kwargs, temperature=temperature)
            return self._extract_response_text(response)

        kwargs = {
            "model": request_model,
            "messages": messages,
            "max_tokens": 4096,
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        if response_format is not None:
            raise UnsupportedProviderOption(
                "AzureFoundryProvider chat-completions models do not support response_format; "
                "retry without it."
            )
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    @staticmethod
    def _extract_response_text(response: Any) -> str:
        for item in getattr(response, "output", []) or []:
            for part in getattr(item, "content", []) or []:
                text = getattr(part, "text", None)
                if text:
                    return text
        output_text = getattr(response, "output_text", None)
        if output_text:
            return output_text
        raise ValueError("Unexpected Azure Foundry response shape")


class GeminiProvider(Provider):
    name = "gemini"

    def __init__(self, api_key: str):
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self._genai = genai

    def send(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> str:
        system_instruction = None
        contents = []
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({"role": role, "parts": [msg["content"]]})

        generation_config: dict[str, Any] = {}
        if temperature is not None:
            generation_config["temperature"] = temperature
        if response_format is not None:
            rf_type = (response_format or {}).get("type")
            if rf_type == "json_object":
                generation_config["response_mime_type"] = "application/json"
            else:
                raise UnsupportedProviderOption(
                    f"GeminiProvider does not support response_format={response_format!r}"
                )

        gm = self._genai.GenerativeModel(model, system_instruction=system_instruction)
        if generation_config:
            response = gm.generate_content(contents, generation_config=generation_config)
        else:
            response = gm.generate_content(contents)
        return response.text


# Model prefix → provider mapping
PROVIDER_PREFIXES = {
    "claude-": "anthropic",
    "gpt-": "openai",
    "o1": "openai",
    "o3": "openai",
    "o4": "openai",
    "gemini-": "gemini",
}
AZURE_FOUNDRY_MODEL_PREFIXES = (
    "azure/",
    "deepseek-",
    "gpt-",
    "mistral-",
    "o1",
    "o3",
    "o4",
)


def _azure_foundry_model_family(model: str) -> str:
    normalized = model.lower()
    if normalized.startswith("azure/"):
        normalized = normalized.split("/", 1)[1]

    if normalized.startswith(("gpt-", "o1", "o3", "o4")):
        return "gpt"
    return "chat"


def _azure_foundry_configured() -> bool:
    return any(
        os.environ.get(name)
        for name in (
            "AZURE_FOUNDRY_ENDPOINT",
            "AZURE_FOUNDRY_CHAT_ENDPOINT",
            "AZURE_FOUNDRY_GPT_ENDPOINT",
        )
    )


def _looks_like_azure_foundry_endpoint(base_url: str | None) -> bool:
    if not base_url:
        return False
    normalized = base_url.lower()
    return "services.ai.azure.com" in normalized or "cognitiveservices.azure.com" in normalized


def _should_use_azure_foundry(model: str, base_url: str | None = None) -> bool:
    if _looks_like_azure_foundry_endpoint(base_url):
        return model.lower().startswith(AZURE_FOUNDRY_MODEL_PREFIXES)
    return _azure_foundry_configured() and model.lower().startswith(
        AZURE_FOUNDRY_MODEL_PREFIXES
    )


def detect_provider(model: str) -> str:
    if _should_use_azure_foundry(model):
        return "azure_foundry"
    for prefix, provider in PROVIDER_PREFIXES.items():
        if model.startswith(prefix):
            return provider
    return "openai"  # default: OpenAI-compatible


def create_provider(
    model: str,
    api_key: str | None = None,
    base_url: str | None = None,
    *,
    deployment: str | None = None,
    allow_insecure_base_url: bool = False,
) -> Provider:
    provider_name = detect_provider(model)
    if provider_name == "openai" and _should_use_azure_foundry(model, base_url):
        provider_name = "azure_foundry"

    if provider_name == "azure_foundry":
        key = api_key or os.environ.get("AZURE_FOUNDRY_API_KEY")
        if not key:
            raise SystemExit("Set AZURE_FOUNDRY_API_KEY or use --api-key")

        endpoint = base_url if _looks_like_azure_foundry_endpoint(base_url) else None
        endpoint = endpoint or (
            os.environ.get("AZURE_FOUNDRY_GPT_ENDPOINT")
            if _azure_foundry_model_family(model) == "gpt"
            else os.environ.get("AZURE_FOUNDRY_CHAT_ENDPOINT")
        )
        endpoint = endpoint or os.environ.get("AZURE_FOUNDRY_ENDPOINT")
        if not endpoint:
            raise SystemExit(
                "Set AZURE_FOUNDRY_ENDPOINT or "
                "AZURE_FOUNDRY_CHAT_ENDPOINT/AZURE_FOUNDRY_GPT_ENDPOINT"
            )
        version = (
            os.environ.get("AZURE_FOUNDRY_GPT_API_VERSION")
            or os.environ.get("AZURE_FOUNDRY_API_VERSION")
            or (
                "2025-04-01-preview"
                if _azure_foundry_model_family(model) == "gpt"
                else "2024-05-01-preview"
            )
        )
        allow_insecure = True if allow_insecure_base_url else None
        return AzureFoundryProvider(
            api_key=key,
            endpoint=endpoint,
            api_version=version,
            family=_azure_foundry_model_family(model),
            deployment=deployment,
            allow_insecure_base_url=allow_insecure,
        )

    if provider_name == "anthropic":
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise SystemExit("Set ANTHROPIC_API_KEY or use --api-key")
        return AnthropicProvider(api_key=key)

    if provider_name == "gemini":
        key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise SystemExit("Set GEMINI_API_KEY or GOOGLE_API_KEY or use --api-key")
        return GeminiProvider(api_key=key)

    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("Set OPENAI_API_KEY or use --api-key")
    allow_insecure = True if allow_insecure_base_url else None
    return OpenAIProvider(
        api_key=key,
        base_url=base_url,
        allow_insecure_base_url=allow_insecure,
    )
