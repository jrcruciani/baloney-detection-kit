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


def test_spanish_catalog_only_contains_requested_variants():
    assert list_interventions(lang="es") == ["compact", "full"]
    assert list_interventions(lang="en") == list_interventions()


@pytest.mark.parametrize("variant", list_interventions())
def test_explicit_english_matches_legacy_api(variant):
    assert get_intervention(variant, lang="en") == get_intervention(variant)


@pytest.mark.parametrize("variant", ["compact", "full"])
def test_packaged_spanish_matches_public_bytes(variant):
    root = Path(__file__).resolve().parents[1]
    public = root / "prompts" / "intervention" / "es" / f"prompt-{variant}.md"
    assert get_intervention(variant, lang="es").encode("utf-8") == public.read_bytes()
    assert get_intervention(variant, lang="es") != get_intervention(variant)


@pytest.mark.parametrize("lang", ["", "pt", "fr", "ES", "es-MX", "../en", "/en", "es/.."])
def test_unsupported_language_never_accesses_resources(monkeypatch, lang):
    def unexpected_access(*args):
        pytest.fail("Invalid language must fail before reading package resources")

    monkeypatch.setattr("bdk.interventions.files", unexpected_access)
    with pytest.raises(ValueError, match="Unsupported intervention language"):
        list_interventions(lang=lang)
    with pytest.raises(ValueError, match="Unsupported intervention language"):
        get_intervention("full", lang=lang)


@pytest.mark.parametrize("lang", ["en", "es"])
@pytest.mark.parametrize("variant", ["unknown", "", "../prompt-full", "/full", "es/full"])
def test_invalid_variant_never_accesses_resources(monkeypatch, lang, variant):
    def unexpected_access(*args):
        pytest.fail("Invalid variant must fail before reading package resources")

    monkeypatch.setattr("bdk.interventions.files", unexpected_access)
    with pytest.raises(KeyError, match="not found"):
        get_intervention(variant, lang=lang)


@pytest.mark.parametrize("variant", ["high-stakes", "agent", "reviewer", "second-opinion"])
def test_unavailable_spanish_variant_does_not_fall_back_to_english(variant):
    with pytest.raises(KeyError, match="language 'es'. Choose one of: compact, full"):
        get_intervention(variant, lang="es")
