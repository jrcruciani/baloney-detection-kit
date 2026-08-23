"""Tests for security helper utilities."""

from __future__ import annotations

import os
from io import StringIO

import pytest

from robopsych.security import (
    ALLOW_INSECURE_BASE_URL_ENV,
    ensure_text_within_limit,
    private_write_text,
    read_text_file_limited,
    read_text_stream_limited,
    redact_secrets,
    safe_exception_message,
    validate_base_url,
)


def test_redacts_common_secret_patterns():
    text = (
        "openai=sk-abcdefghijklmnopqrstuvwxyz "
        "anthropic=sk-ant-abcdefghijklmnopqrstuvwxyz "
        "github=gho_abcdefghijklmnopqrstuvwxyz "
        "google=AIzaabcdefghijklmnopqrstuvwxyz "
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz"
    )
    redacted = redact_secrets(text)
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "sk-ant-abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "gho_abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "AIzaabcdefghijklmnopqrstuvwxyz" not in redacted
    assert "Bearer abcdefghijklmnopqrstuvwxyz" not in redacted
    assert "REDACTED" in redacted


def test_safe_exception_message_redacts_and_truncates():
    exc = RuntimeError("failed with api_key=sk-abcdefghijklmnopqrstuvwxyz and extra text")
    msg = safe_exception_message(exc, max_chars=40)
    assert msg.startswith("RuntimeError:")
    assert "sk-abcdefghijklmnopqrstuvwxyz" not in msg
    assert msg.endswith("...[truncated]")


def test_ensure_text_within_limit_rejects_oversized_text():
    with pytest.raises(ValueError, match="--response exceeds"):
        ensure_text_within_limit("abcd", source="--response", max_bytes=3)


def test_read_text_file_limited_rejects_oversized_file(tmp_path):
    p = tmp_path / "response.txt"
    p.write_text("abcd")
    with pytest.raises(ValueError, match="exceeds"):
        read_text_file_limited(p, max_bytes=3)


def test_read_text_stream_limited_rejects_oversized_stdin():
    with pytest.raises(ValueError, match="stdin exceeds"):
        read_text_stream_limited(StringIO("abcd"), max_chars=3)


def test_private_write_text_sets_owner_only_permissions(tmp_path):
    p = tmp_path / "session.json"
    private_write_text(p, "{}")
    assert p.read_text() == "{}"
    if os.name == "posix":
        assert p.stat().st_mode & 0o777 == 0o600


def test_validate_base_url_accepts_public_https():
    assert validate_base_url("https://api.example.com/v1") == "https://api.example.com/v1"


def test_validate_base_url_rejects_malformed():
    with pytest.raises(ValueError, match="absolute http"):
        validate_base_url("not-a-url")


def test_validate_base_url_rejects_http_without_opt_in(monkeypatch):
    monkeypatch.delenv(ALLOW_INSECURE_BASE_URL_ENV, raising=False)
    with pytest.raises(ValueError, match="non-HTTPS"):
        validate_base_url("http://localhost:11434/v1")


def test_validate_base_url_allows_insecure_with_explicit_opt_in(monkeypatch):
    monkeypatch.setenv(ALLOW_INSECURE_BASE_URL_ENV, "1")
    assert validate_base_url("http://localhost:11434/v1") == "http://localhost:11434/v1"


def test_validate_base_url_rejects_private_https_without_opt_in(monkeypatch):
    monkeypatch.delenv(ALLOW_INSECURE_BASE_URL_ENV, raising=False)
    with pytest.raises(ValueError, match="localhost/private-network"):
        validate_base_url("https://192.168.1.5/v1")
