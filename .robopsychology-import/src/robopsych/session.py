"""Session persistence for long ratchet sequences."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from robopsych.security import private_write_text


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
        data = json.loads(path.read_text(encoding="utf-8"))
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
