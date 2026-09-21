"""Session persistence for long ratchet sequences."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from bdk.scenarios import parse_scenario
from bdk.security import private_write_text, read_text_file_limited


@dataclass
class SessionState:
    """Serializable snapshot of a ratchet session."""

    provider_name: str
    model: str
    scenario_name: str = ""
    task: str = ""
    system_prompt: str | None = None
    initial_response: str | None = None
    sequence: list[str] = field(default_factory=list)
    completed_steps: list[dict] = field(default_factory=list)
    messages: list[dict] = field(default_factory=list)
    started_at: str = ""
    updated_at: str = ""
    scenario: dict | None = None
    scenario_messages: list[dict] = field(default_factory=list)
    scenario_analysis: dict | None = None

    def save(self, path: Path) -> None:
        """Save session state to a JSON file."""
        self.updated_at = datetime.now(timezone.utc).isoformat()
        private_write_text(
            path,
            json.dumps(asdict(self), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> SessionState:
        """Load session state from a JSON file."""
        data = json.loads(read_text_file_limited(path))
        if not isinstance(data, dict):
            raise ValueError("saved session must be a JSON object")
        if data.get("scenario") is not None:
            scenario = parse_scenario(data["scenario"], saved=True)
            analysis = data.get("scenario_analysis")
            if analysis is not None and (
                not isinstance(analysis, dict)
                or analysis.get("status") not in ("scored", "incomplete", "error", "unavailable")
            ):
                raise ValueError("invalid saved scenario analysis")
            messages = data.get("scenario_messages", [])
            if not isinstance(messages, list) or len(messages) % 2 != 1:
                raise ValueError("saved scenario transcript must contain complete exchanges")
            if messages[0] != {"role": "system", "content": scenario.system_prompt}:
                raise ValueError("saved scenario system prompt mismatch")
            if len(messages) > 1 + 2 * len(scenario.user_messages):
                raise ValueError("saved scenario has excess turns")
            for index, message in enumerate(messages[1:], 1):
                role = "user" if index % 2 else "assistant"
                if (
                    not isinstance(message, dict)
                    or message.get("role") != role
                    or not isinstance(message.get("content"), str)
                    or not message["content"].strip()
                ):
                    raise ValueError("invalid saved scenario message")
                if role == "user" and message["content"] != scenario.user_messages[index // 2]:
                    raise ValueError("saved scenario user message mismatch")
        return cls(**data)

    @property
    def remaining_steps(self) -> list[str]:
        """Return prompt IDs not yet completed."""
        done = {s["prompt_id"] for s in self.completed_steps}
        return [pid for pid in self.sequence if pid not in done]

    @classmethod
    def create(
        cls,
        provider_name: str,
        model: str,
        sequence: list[str],
        scenario_name: str = "",
        task: str = "",
        system_prompt: str | None = None,
    ) -> SessionState:
        return cls(
            provider_name=provider_name,
            model=model,
            scenario_name=scenario_name,
            task=task,
            system_prompt=system_prompt,
            sequence=sequence,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
