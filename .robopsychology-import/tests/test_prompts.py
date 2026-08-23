"""Tests for prompt catalog loading and rendering."""

import pytest

from robopsych.prompts import (
    get_diagnostic_prompts,
    get_diagnostic_variant,
    get_flowchart,
    get_intervention_prompts,
    get_prompt,
    get_pure_ratchet_sequence,
    get_ratchet_sequence,
    get_rules,
    list_prompts,
    render_prompt,
)


class TestListPrompts:
    def test_returns_all_21_prompts(self):
        prompts = list_prompts()
        assert len(prompts) == 21  # 16 original + 5 diagnostic variants

    def test_each_prompt_has_required_fields(self):
        for p in list_prompts():
            assert "id" in p
            assert "name" in p
            assert "level" in p
            assert "category" in p
            assert "description" in p
            assert "template" in p
            assert "mode" in p

    def test_prompt_ids_are_unique(self):
        ids = [p["id"] for p in list_prompts()]
        assert len(ids) == len(set(ids))

    def test_levels_are_1_to_4(self):
        levels = {p["level"] for p in list_prompts()}
        assert levels == {1, 2, 3, 4}

    def test_categories_are_valid(self):
        valid = {"quick", "structural", "systemic", "meta"}
        for p in list_prompts():
            assert p["category"] in valid

    def test_modes_are_valid(self):
        valid = {"diagnostic", "diagnostic+intervention"}
        for p in list_prompts():
            assert p["mode"] in valid

    def test_filter_by_diagnostic_mode(self):
        diag = list_prompts(mode="diagnostic")
        assert all(p["mode"] == "diagnostic" for p in diag)
        assert len(diag) == 16  # 11 original + 5 variants

    def test_filter_by_intervention_mode(self):
        inter = list_prompts(mode="diagnostic+intervention")
        assert all(p["mode"] == "diagnostic+intervention" for p in inter)
        assert len(inter) == 5

    def test_filter_none_returns_all(self):
        assert len(list_prompts(mode=None)) == 21


class TestGetPrompt:
    def test_get_existing_prompt(self):
        p = get_prompt("1.1")
        assert p["name"] == "Calvin Question"
        assert p["level"] == 1

    def test_get_prompt_not_found(self):
        with pytest.raises(KeyError, match="99.99"):
            get_prompt("99.99")

    def test_all_prompts_retrievable_by_id(self):
        for p in list_prompts():
            result = get_prompt(p["id"])
            assert result["id"] == p["id"]


class TestRenderPrompt:
    def test_render_without_variables(self):
        text = render_prompt("1.1")
        assert "second intention diagnosis" in text.lower()

    def test_render_with_variables(self):
        text = render_prompt("1.4", variables={"action": "write a scraper"})
        assert "write a scraper" in text

    def test_render_prompt_with_required_variable_missing(self):
        text = render_prompt("1.4")
        assert "{action}" in text

    def test_render_prompt_with_extra_variables(self):
        text = render_prompt("1.1", variables={"extra": "ignored"})
        assert "second intention diagnosis" in text.lower()


class TestGetRules:
    def test_returns_5_rules(self):
        rules = get_rules()
        assert len(rules) == 5

    def test_rules_have_id_and_name(self):
        for r in get_rules():
            assert "id" in r
            assert "name" in r
            assert "text" in r


class TestGetFlowchart:
    def test_flowchart_has_observations(self):
        fc = get_flowchart()
        assert "observations" in fc
        assert len(fc["observations"]) > 0

    def test_each_observation_has_path(self):
        for obs in get_flowchart()["observations"]:
            assert "id" in obs
            assert "label" in obs
            assert "path" in obs
            assert len(obs["path"]) > 0

    def test_all_path_prompts_exist(self):
        for obs in get_flowchart()["observations"]:
            for pid in obs["path"]:
                get_prompt(pid)  # Should not raise


class TestRatchetSequence:
    def test_sequence_has_9_steps(self):
        seq = get_ratchet_sequence()
        assert len(seq) == 9

    def test_all_sequence_prompts_exist(self):
        for pid in get_ratchet_sequence():
            get_prompt(pid)  # Should not raise

    def test_sequence_order(self):
        seq = get_ratchet_sequence()
        assert seq[0] == "2.1"
        assert seq[-1] == "4.3"


class TestPureRatchetSequence:
    def test_pure_sequence_has_9_steps(self):
        seq = get_pure_ratchet_sequence()
        assert len(seq) == 9

    def test_all_pure_sequence_prompts_exist(self):
        for pid in get_pure_ratchet_sequence():
            get_prompt(pid)  # Should not raise

    def test_pure_sequence_uses_d_variants(self):
        seq = get_pure_ratchet_sequence()
        assert "3.1d" in seq
        assert "3.2d" in seq
        assert "3.1" not in seq
        assert "3.2" not in seq


class TestDiagnosticVariants:
    VARIANT_IDS = ["1.2d", "1.4d", "2.2d", "3.1d", "3.2d"]

    def test_all_variants_exist(self):
        for vid in self.VARIANT_IDS:
            get_prompt(vid)  # Should not raise

    def test_variants_are_diagnostic_mode(self):
        for vid in self.VARIANT_IDS:
            p = get_prompt(vid)
            assert p["mode"] == "diagnostic"

    def test_1_2d_no_intervention(self):
        p = get_prompt("1.2d")
        assert "non-approval-optimized" not in p["template"]

    def test_1_4d_no_intervention(self):
        p = get_prompt("1.4d")
        assert "If you can proceed" not in p["template"]

    def test_2_2d_no_intervention(self):
        p = get_prompt("2.2d")
        assert "return to your natural tone" not in p["template"]

    def test_3_1d_no_intervention(self):
        p = get_prompt("3.1d")
        assert "If it can be relaxed" not in p["template"]

    def test_3_2d_no_intervention(self):
        p = get_prompt("3.2d")
        assert "Please compare the same task" not in p["template"]
        assert "Without executing" in p["template"]


class TestGetDiagnosticVariant:
    def test_returns_variant_when_exists(self):
        assert get_diagnostic_variant("3.1") == "3.1d"
        assert get_diagnostic_variant("1.2") == "1.2d"

    def test_returns_original_when_no_variant(self):
        assert get_diagnostic_variant("1.1") == "1.1"
        assert get_diagnostic_variant("2.1") == "2.1"


class TestGetDiagnosticPrompts:
    def test_returns_only_diagnostic(self):
        prompts = get_diagnostic_prompts()
        assert all(p["mode"] == "diagnostic" for p in prompts)

    def test_count_matches_filter(self):
        assert len(get_diagnostic_prompts()) == len(list_prompts(mode="diagnostic"))


class TestGetInterventionPrompts:
    def test_returns_only_intervention(self):
        prompts = get_intervention_prompts()
        assert all(p["mode"] == "diagnostic+intervention" for p in prompts)

    def test_count_matches_filter(self):
        assert len(get_intervention_prompts()) == len(
            list_prompts(mode="diagnostic+intervention")
        )


class TestFlowchartObservationDescriptions:
    def test_all_observations_have_descriptions(self):
        for obs in get_flowchart()["observations"]:
            assert "description" in obs, f"Observation {obs['id']} missing description"
            assert len(obs["description"]) > 20
