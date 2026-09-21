"""Shared, preflight-validated scenarios for diagnosis and intervention checks."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from bdk.interventions import get_intervention, get_intervention_version
from bdk.prompts import get_prompt
from bdk.security import read_text_file_limited


@dataclass
class Scenario:
    name: str
    task: str
    system_prompt: str = "You are a helpful assistant."
    expectation: str = ""
    code: str | None = None
    recommended_path: list[str] = field(default_factory=list)
    turns: list[str] = field(default_factory=list)
    expected_trigger: bool | None = None
    expectations: dict = field(default_factory=dict)
    new_evidence_turns: list[int] = field(default_factory=list)
    source: str = ""
    prompt_reference: str | None = None
    prompt_version: str | None = None

    @property
    def user_messages(self) -> list[str]:
        task = self.task
        if self.code is not None:
            task += f"\n\n```\n{self.code}\n```"
        return [task, *self.turns]

    @property
    def provenance(self) -> dict:
        return {
            "scenario_id": self.source or self.name,
            "prompt_reference": self.prompt_reference,
            "prompt_version": self.prompt_version,
            "prompt_sha256": hashlib.sha256(self.system_prompt.encode("utf-8")).hexdigest(),
        }

    def snapshot(self) -> dict:
        return asdict(self)


def _text(value: object, field_name: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(
            f"{field_name} must be a {'possibly empty ' if empty else 'nonempty '}string"
        )
    return value


def parse_scenario(data: object, *, source: str = "", saved: bool = False) -> Scenario:
    """Validate all executable fields; retain legacy descriptive metadata compatibility."""
    if not isinstance(data, dict):
        raise ValueError("scenario must be a YAML mapping")
    task = _text(data.get("task"), "task")
    name = _text(data.get("name", Path(source).stem or "scenario"), "name")
    expectation = _text(data.get("expectation", ""), "expectation", empty=True)
    code = data.get("code")
    if code is not None:
        code = _text(code, "code", empty=True)
    prompt_value = data.get("system_prompt")
    prompt = (
        "You are a helpful assistant."
        if prompt_value is None or prompt_value == ""
        else _text(prompt_value, "system_prompt")
    )
    reference = data.get("system_prompt_ref")
    version = None
    if reference is not None:
        reference = _text(reference, "system_prompt_ref")
        if "system_prompt" in data:
            raise ValueError("system_prompt and system_prompt_ref are mutually exclusive")
        parts = reference.split(":")
        if len(parts) != 3 or parts[0] != "bdk":
            raise ValueError("system_prompt_ref must be bdk:<variant>:<language>")
        try:
            prompt = get_intervention(parts[1], lang=parts[2])
        except KeyError as exc:
            raise ValueError(str(exc)) from exc
        version = get_intervention_version(prompt)
    if saved:
        # Saved sessions use the captured prompt, never a newly installed version.
        reference = data.get("prompt_reference")
        if reference is not None:
            reference = _text(reference, "prompt_reference")
            version = get_intervention_version(prompt)
            if version != data.get("prompt_version"):
                raise ValueError("saved prompt version does not match captured prompt")
        source = _text(data.get("source", source), "source", empty=True)
    if version is None and "<!-- bdk prompt-" in prompt:
        version = get_intervention_version(prompt)
    turns = data.get("turns", [])
    if not isinstance(turns, list):
        raise ValueError("turns must be a list of sequential user messages")
    turns = [_text(turn, "turns item") for turn in turns]
    path = data.get("recommended_path", [])
    if not isinstance(path, list):
        raise ValueError("recommended_path must be a list of prompt IDs")
    for pid in path:
        _text(pid, "recommended_path item")
        try:
            get_prompt(pid)
        except KeyError as exc:
            raise ValueError(f"unknown recommended_path prompt ID: {pid}") from exc
    trigger = data.get("expected_trigger")
    if trigger is not None and type(trigger) is not bool:
        raise ValueError("expected_trigger must be boolean")
    expectations = data.get("expectations", {})
    if not isinstance(expectations, dict):
        raise ValueError("expectations must be a mapping")
    allowed = {"max_flips", "verdict_stable_unless_new_evidence", "reopen_on_new_evidence"}
    if expectations.keys() - allowed:
        raise ValueError("unknown machine-readable expectation")
    for key, value in expectations.items():
        if key == "max_flips":
            if type(value) is not int or value < 0:
                raise ValueError("max_flips must be a nonnegative integer")
        elif type(value) is not bool:
            raise ValueError(f"{key} must be boolean")
    evidence = data.get("new_evidence_turns", [])
    if not isinstance(evidence, list) or any(
        type(turn) is not int or not 2 <= turn <= len(turns) + 1 for turn in evidence
    ):
        raise ValueError("new_evidence_turns must list follow-up turn numbers (task is turn 1)")
    if len(set(evidence)) != len(evidence):
        raise ValueError("new_evidence_turns contains duplicate turns")
    if expectations and not turns:
        raise ValueError("stance expectations require follow-up turns")
    if expectations.get("reopen_on_new_evidence") and not evidence:
        raise ValueError("reopen_on_new_evidence requires new_evidence_turns")
    return Scenario(
        name=name,
        task=task,
        system_prompt=prompt,
        expectation=expectation,
        code=code,
        recommended_path=list(path),
        turns=turns,
        expected_trigger=trigger,
        expectations=expectations.copy(),
        new_evidence_turns=list(evidence),
        source=source,
        prompt_reference=reference,
        prompt_version=version,
    )


def load_scenario(path: Path) -> Scenario:
    try:
        return parse_scenario(yaml.safe_load(read_text_file_limited(path)), source=str(path))
    except (ValueError, yaml.YAMLError) as exc:
        raise ValueError(f"{path}: {exc}") from exc


def load_scenarios(directory: Path) -> list[Scenario]:
    """Recursively load YAMLs in relative-path order, failing before any provider calls."""
    if not directory.is_dir():
        raise ValueError(f"not a scenario directory: {directory}")
    paths = sorted(
        (p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".yaml", ".yml"}),
        key=lambda p: p.relative_to(directory).as_posix(),
    )
    if not paths:
        raise ValueError(f"no YAML scenarios found in {directory}")
    return [load_scenario(path) for path in paths]
