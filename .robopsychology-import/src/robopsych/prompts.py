"""Prompt catalog loader."""

from __future__ import annotations

from importlib.resources import files
from typing import Any

import yaml

_catalog: dict[str, Any] | None = None


def _load() -> dict[str, Any]:
    global _catalog
    if _catalog is None:
        data_dir = files("robopsych") / "data" / "prompts.yaml"
        _catalog = yaml.safe_load(data_dir.read_text(encoding="utf-8"))
    return _catalog


def get_prompt(prompt_id: str) -> dict[str, Any]:
    catalog = _load()
    for p in catalog["prompts"]:
        if p["id"] == prompt_id:
            return p
    raise KeyError(f"Prompt {prompt_id!r} not found")


def list_prompts(mode: str | None = None) -> list[dict[str, Any]]:
    """Return all prompts, optionally filtered by mode."""
    prompts = _load()["prompts"]
    if mode is None:
        return prompts
    return [p for p in prompts if p.get("mode") == mode]


def get_diagnostic_prompts() -> list[dict[str, Any]]:
    """Return only diagnostic prompts (mode == 'diagnostic')."""
    return [p for p in _load()["prompts"] if p.get("mode") == "diagnostic"]


def get_intervention_prompts() -> list[dict[str, Any]]:
    """Return only prompts that include intervention (mode == 'diagnostic+intervention')."""
    return [p for p in _load()["prompts"] if p.get("mode") == "diagnostic+intervention"]


def get_rules() -> list[dict[str, Any]]:
    return _load()["rules"]


def get_flowchart() -> dict[str, Any]:
    return _load()["flowchart"]


def get_ratchet_sequence() -> list[str]:
    return _load()["flowchart"]["ratchet_sequence"]


def get_pure_ratchet_sequence() -> list[str]:
    """Return the diagnostic-only ratchet sequence (no intervention prompts)."""
    return _load()["flowchart"]["pure_ratchet_sequence"]


def get_diagnostic_variant(prompt_id: str) -> str:
    """Return the diagnostic-only variant ID if it exists, else the original."""
    variant = f"{prompt_id}d"
    catalog = _load()
    for p in catalog["prompts"]:
        if p["id"] == variant:
            return variant
    return prompt_id


def render_prompt(prompt_id: str, variables: dict[str, str] | None = None) -> str:
    prompt = get_prompt(prompt_id)
    template = prompt["template"]
    if variables:
        template = template.format(**variables)
    return template
