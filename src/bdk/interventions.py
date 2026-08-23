"""Packaged preventive intervention prompts."""

from __future__ import annotations

from importlib.resources import files

_INTERVENTIONS = {
    "compact": "prompt-compact.md",
    "full": "prompt-full.md",
    "high-stakes": "prompt-high-stakes.md",
    "agent": "prompt-agent.md",
    "reviewer": "prompt-reviewer.md",
    "second-opinion": "prompt-second-opinion.md",
}


def list_interventions() -> list[str]:
    """Return the available preventive intervention variants."""
    return list(_INTERVENTIONS)


def get_intervention(variant: str) -> str:
    """Load a packaged preventive intervention by name."""
    try:
        filename = _INTERVENTIONS[variant]
    except KeyError as exc:
        raise KeyError(f"Intervention {variant!r} not found") from exc

    path = files("bdk") / "data" / "interventions" / filename
    return path.read_text(encoding="utf-8")
