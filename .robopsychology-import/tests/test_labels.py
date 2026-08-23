"""Tests for structured label parsing."""

from robopsych.labels import (
    Label,
    count_structured_labels,
    has_structured_labels,
    parse_labeled_claims,
)


class TestBracketedForm:
    def test_simple_bracketed(self):
        text = "[Observed] the model refused the task"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.OBSERVED
        assert "refused" in claims[0].text

    def test_bulleted_bracketed(self):
        text = """
        - [Observed] claim one
        - [Inferred] claim two
        * [Observed] claim three
        """
        claims = parse_labeled_claims(text)
        assert len(claims) == 3
        assert claims[0].label == Label.OBSERVED
        assert claims[1].label == Label.INFERRED
        assert claims[2].label == Label.OBSERVED

    def test_bold_bracketed(self):
        text = "- **[Observed]** the refusal mentioned policy"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.OBSERVED

    def test_bracketed_with_colon(self):
        text = "- [Inferred]: the model inferred user intent"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.INFERRED

    def test_weakly_grounded(self):
        text = "- [Weakly grounded] there might be a pattern here"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.WEAKLY_GROUNDED

    def test_weakly_hyphenated(self):
        text = "- [Weakly-grounded] this is hard to verify"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.WEAKLY_GROUNDED

    def test_anchored_maps_to_observed(self):
        text = "- [Anchored] fact X is confirmed by explicit constraint"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.OBSERVED

    def test_case_insensitive(self):
        text = "- [observed] lowercase bracket"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.OBSERVED


class TestColonPrefixForm:
    def test_colon_prefix_accepted(self):
        text = "Observed: the refusal cited a safety concern explicitly"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.OBSERVED

    def test_colon_with_bullet(self):
        text = "- Inferred: the model is applying an overly-broad category match"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.INFERRED

    def test_colon_requires_substantial_text(self):
        # "Observed:" alone (as section header) should NOT match — too short.
        text = "Observed:\n- item one\n- item two"
        claims = parse_labeled_claims(text)
        # Section header itself has no claim text after colon
        assert len(claims) == 0

    def test_colon_two_words_rejected(self):
        # Two words after colon is too short to be a real claim
        text = "Observed: behavior shift"
        claims = parse_labeled_claims(text)
        assert len(claims) == 0


class TestProseRejection:
    """Verify that prose uses of 'observed' and 'inferred' are NOT captured."""

    def test_rejects_prose_observed(self):
        text = (
            "Looking at the response, I observed that the model was hedging. "
            "It then inferred my intent from context clues."
        )
        claims = parse_labeled_claims(text)
        assert claims == []

    def test_rejects_word_boundaries(self):
        text = "The unobserved cause was inferring something"
        assert parse_labeled_claims(text) == []

    def test_rejects_mid_sentence_brackets(self):
        """Brackets mid-sentence shouldn't match — only line-start."""
        text = "The model's behavior [Observed] is to refuse"
        claims = parse_labeled_claims(text)
        # This one is ambiguous — start-of-line matcher won't catch mid-sentence
        # Actually the regex uses ^ with MULTILINE, so mid-line is NOT matched.
        # But "The model's behavior " counts as preceding content, so no match.
        # But wait, ^ with MULTILINE matches start-of-line only. The pattern
        # allows leading whitespace and bullet marker, so mid-sentence fails.
        assert claims == []


class TestDeduplication:
    def test_bracketed_takes_precedence_over_colon(self):
        # Same line has both — should only count once
        text = "- [Observed]: the model said no"
        claims = parse_labeled_claims(text)
        assert len(claims) == 1
        assert claims[0].label == Label.OBSERVED

    def test_different_lines_both_count(self):
        text = "- [Observed] line one\n- [Inferred] line two"
        claims = parse_labeled_claims(text)
        assert len(claims) == 2


class TestCountStructuredLabels:
    def test_counts_per_label(self):
        text = """
        - [Observed] one
        - [Observed] two
        - [Inferred] three
        - [Weakly grounded] four
        """
        counts = count_structured_labels(text)
        assert counts["observed"] == 2
        # Inferred includes weakly-grounded in the 2-way split
        assert counts["inferred"] == 2
        assert counts["weakly_grounded"] == 1

    def test_empty_text(self):
        assert count_structured_labels("") == {
            "observed": 0, "inferred": 0, "weakly_grounded": 0,
        }

    def test_prose_only_returns_zero(self):
        text = "I observed the model. It inferred my intent."
        assert count_structured_labels(text) == {
            "observed": 0, "inferred": 0, "weakly_grounded": 0,
        }


class TestHasStructuredLabels:
    def test_true_when_labels_present(self):
        assert has_structured_labels("- [Observed] something")

    def test_false_for_prose(self):
        assert not has_structured_labels("I observed the model refused.")

    def test_false_for_empty(self):
        assert not has_structured_labels("")


class TestReportIntegration:
    """Verify report.count_labels prefers structured, falls back to legacy."""

    def test_structured_path(self):
        from robopsych.report import count_labels
        text = "- [Observed] claim A\n- [Inferred] claim B\n- [Inferred] claim C"
        counts = count_labels(text)
        assert counts["observed"] == 1
        assert counts["inferred"] == 2

    def test_structured_ignores_prose(self):
        """Prose uses DO NOT inflate counts when structured labels are present."""
        from robopsych.report import count_labels
        text = (
            "I observed previously. I inferred before too.\n"
            "- [Observed] real labeled claim\n"
        )
        counts = count_labels(text)
        assert counts["observed"] == 1  # NOT 2
        assert counts["inferred"] == 0  # NOT 1

    def test_legacy_fallback(self):
        """When no structured labels, falls back to bare-word regex."""
        from robopsych.report import count_labels
        text = "I observed the model behavior and inferred the cause."
        counts = count_labels(text)
        # Legacy regex matches both bare words
        assert counts["observed"] == 1
        assert counts["inferred"] == 1
