"""CLI-only model aliases; provider and engine APIs continue to take raw IDs."""

from __future__ import annotations

import tomllib
from pathlib import Path


class ModelConfigError(ValueError):
    """An alias configuration cannot be read or does not match the schema."""


def _read_models(path: Path) -> dict[str, str]:
    try:
        path.lstat()
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise ModelConfigError(f"Cannot access model config {path}: {exc}") from exc

    try:
        with path.open("rb") as stream:
            data = tomllib.load(stream)
    except (OSError, ValueError) as exc:
        raise ModelConfigError(f"Cannot read model config {path}: {exc}") from exc

    if set(data) != {"models"} or not isinstance(data["models"], dict):
        raise ModelConfigError(f'{path}: expected only a [models] table of alias = "model-id"')

    models = {}
    for alias, model in data["models"].items():
        if not alias or any(char.isspace() for char in alias):
            raise ModelConfigError(f"{path}: model alias names must be nonempty without whitespace")
        if (
            not isinstance(model, str)
            or not model
            or any(char.isspace() for char in model)
            or "://" in model
            or model == "default"
        ):
            raise ModelConfigError(
                f"{path}: [models].{alias} must be a nonempty raw model ID string "
                'without whitespace, not a URL or the reserved name "default"'
            )
        models[alias] = model
    return models


def load_model_aliases() -> dict[str, str]:
    """Merge user and current-directory aliases, with local values winning."""
    try:
        paths = (Path.home() / ".config" / "bdk" / "config.toml", Path.cwd() / "bdk.toml")
    except (OSError, RuntimeError) as exc:
        raise ModelConfigError(f"Cannot locate model configuration: {exc}") from exc
    aliases = {}
    for path in paths:
        aliases.update(_read_models(path))
    return aliases


def resolve_model(model: str) -> str:
    """Resolve one alias lookup, never recursively; leave other raw IDs unchanged."""
    aliases = load_model_aliases()
    if model == "default" and model not in aliases:
        raise ModelConfigError(
            'Model alias "default" is not configured. Set default = "your-model-id" '
            "under [models] in ./bdk.toml or ~/.config/bdk/config.toml, "
            "or pass a raw model ID."
        )
    return aliases.get(model, model)
