from pathlib import Path

import pytest

from bdk.interventions import get_intervention, list_interventions


def test_intervention_catalog_is_complete():
    assert list_interventions() == [
        "compact",
        "full",
        "high-stakes",
        "agent",
        "reviewer",
        "second-opinion",
    ]


@pytest.mark.parametrize("variant", list_interventions())
def test_packaged_intervention_matches_public_prompt(variant):
    root = Path(__file__).resolve().parents[1]
    filename = {
        "compact": "prompt-compact.md",
        "full": "prompt-full.md",
        "high-stakes": "prompt-high-stakes.md",
        "agent": "prompt-agent.md",
        "reviewer": "prompt-reviewer.md",
        "second-opinion": "prompt-second-opinion.md",
    }[variant]
    public_prompt = root / "prompts" / "intervention" / filename

    assert get_intervention(variant) == public_prompt.read_text(encoding="utf-8")


def test_unknown_intervention_fails_explicitly():
    with pytest.raises(KeyError, match="not found"):
        get_intervention("unknown")
