"""Packaged preventive intervention prompts."""

from __future__ import annotations

from importlib.resources import files

_INTERVENTIONS = {
    "en": {
        "compact": "prompt-compact.md",
        "full": "prompt-full.md",
        "high-stakes": "prompt-high-stakes.md",
        "agent": "prompt-agent.md",
        "reviewer": "prompt-reviewer.md",
        "second-opinion": "prompt-second-opinion.md",
    },
    "es": {
        "compact": "es/prompt-compact.md",
        "full": "es/prompt-full.md",
    },
}


def _catalog(lang: str) -> dict[str, str]:
    try:
        return _INTERVENTIONS[lang]
    except KeyError as exc:
        available = ", ".join(_INTERVENTIONS)
        raise ValueError(
            f"Unsupported intervention language {lang!r}. Choose one of: {available}."
        ) from exc


def list_interventions(*, lang: str = "en") -> list[str]:
    """Return variants for an explicitly supported language; default to English."""
    return list(_catalog(lang))


def get_intervention(variant: str, *, lang: str = "en") -> str:
    """Load an allowlisted variant/language pair without language fallback."""
    catalog = _catalog(lang)
    try:
        filename = catalog[variant]
    except KeyError as exc:
        available = ", ".join(catalog)
        raise KeyError(
            f"Intervention {variant!r} not found for language {lang!r}. Choose one of: {available}."
        ) from exc

    path = files("bdk") / "data" / "interventions" / filename
    return path.read_text(encoding="utf-8")
