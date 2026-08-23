"""Small security helpers for CLI inputs, logs, and generated artifacts."""

from __future__ import annotations

import ipaddress
import os
import re
from pathlib import Path
from typing import TextIO
from urllib.parse import urlparse

DEFAULT_MAX_INPUT_BYTES = 10 * 1024 * 1024
DEFAULT_MAX_ERROR_CHARS = 2_000

ALLOW_INSECURE_BASE_URL_ENV = "ROBOPSYCH_ALLOW_INSECURE_BASE_URL"

_TRUTHY = {"1", "true", "yes", "on"}

_SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{10,}"), "sk-ant-***REDACTED***"),
    (re.compile(r"sk-[A-Za-z0-9_-]{10,}"), "sk-***REDACTED***"),
    (re.compile(r"gh[opsru]_[A-Za-z0-9_]{10,}"), "gh***_***REDACTED***"),
    (re.compile(r"AIza[0-9A-Za-z_-]{10,}"), "AIza***REDACTED***"),
    (re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{10,}", re.IGNORECASE), "Bearer ***REDACTED***"),
    (
        re.compile(
            r"(?i)\b(api[_-]?key|x-api-key|authorization)(\s*[:=]\s*)"
            r"([\"']?)[^\"'\s,}]{8,}([\"']?)"
        ),
        r"\1\2\3***REDACTED***\4",
    ),
)


def _truncate(text: str, max_chars: int | None) -> str:
    if max_chars is None or len(text) <= max_chars:
        return text
    return text[:max_chars] + "...[truncated]"


def redact_secrets(value: object, *, max_chars: int | None = None) -> str:
    """Return ``value`` as text with common API-key/token patterns redacted."""
    text = str(value)
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return _truncate(text, max_chars)


def safe_exception_message(exc: Exception, *, max_chars: int = DEFAULT_MAX_ERROR_CHARS) -> str:
    """Format an exception for logs/reports without leaking common secrets."""
    return redact_secrets(f"{type(exc).__name__}: {exc}", max_chars=max_chars)


def ensure_text_within_limit(
    text: str,
    *,
    source: str,
    max_bytes: int = DEFAULT_MAX_INPUT_BYTES,
) -> str:
    """Validate in-memory text before it is used as prompt/report input."""
    if len(text.encode("utf-8")) > max_bytes:
        raise ValueError(f"{source} exceeds {max_bytes} bytes")
    return text


def read_text_file_limited(
    path: Path,
    *,
    max_bytes: int = DEFAULT_MAX_INPUT_BYTES,
    encoding: str = "utf-8",
) -> str:
    """Read a text file, rejecting content larger than ``max_bytes``."""
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"{path} exceeds {max_bytes} bytes")
    data = path.read_bytes()
    if len(data) > max_bytes:
        raise ValueError(f"{path} exceeds {max_bytes} bytes")
    return data.decode(encoding)


def read_text_stream_limited(
    stream: TextIO,
    *,
    source: str = "stdin",
    max_chars: int = DEFAULT_MAX_INPUT_BYTES,
) -> str:
    """Read from a text stream, rejecting content beyond ``max_chars``."""
    data = stream.read(max_chars + 1)
    if len(data) > max_chars:
        raise ValueError(f"{source} exceeds {max_chars} characters")
    return data


def private_write_text(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    """Write text with owner-only permissions where the platform supports it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding=encoding) as f:
        f.write(content)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def private_open_text(path: Path, *, encoding: str = "utf-8") -> TextIO:
    """Open a text file for writing with owner-only permissions when possible."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return os.fdopen(fd, "w", encoding=encoding)


def insecure_base_url_allowed() -> bool:
    """Return whether explicit opt-in for insecure/private base URLs is set."""
    return os.environ.get(ALLOW_INSECURE_BASE_URL_ENV, "").strip().lower() in _TRUTHY


def _is_local_or_private_host(hostname: str | None) -> bool:
    if not hostname:
        return False
    host = hostname.strip().lower().rstrip(".")
    if host in {"localhost", "0.0.0.0"}:
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_loopback or ip.is_private or ip.is_link_local


def validate_base_url(
    base_url: str | None,
    *,
    allow_insecure: bool | None = None,
) -> str | None:
    """Validate an OpenAI-compatible base URL before API keys are sent to it."""
    if base_url is None:
        return None
    value = base_url.strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.hostname:
        raise ValueError("base_url must be an absolute http(s) URL")

    allow = insecure_base_url_allowed() if allow_insecure is None else allow_insecure
    reasons: list[str] = []
    if parsed.scheme != "https":
        reasons.append("non-HTTPS")
    if _is_local_or_private_host(parsed.hostname):
        reasons.append("localhost/private-network")
    if reasons and not allow:
        joined = ", ".join(reasons)
        raise ValueError(
            f"base_url uses {joined} routing; set "
            f"{ALLOW_INSECURE_BASE_URL_ENV}=1 or pass --allow-insecure-base-url "
            "to opt in explicitly"
        )
    return value
