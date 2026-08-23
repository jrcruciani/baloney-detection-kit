"""Structured parsing of Observed / Inferred labels in diagnostic responses.

The existing `count_labels` in report.py counts bare word occurrences of
"observed" and "inferred" — which contaminates with prose uses ("I observed
that the model...", "the inferred cause could be..."). That overcount makes
the label_distribution metric in scoring.py an unreliable signal.

This module parses **structured** labels in the bullet form that R2 asks for:

    [Observed] the refusal cited a safety policy
    - [Observed] the refusal cited a safety policy
    * [Inferred] the model is applying a broad category

Also accepts bold variants (`**[Observed]**`) and the `Observed:` / `Inferred:`
prefix form that some models emit when asked for structured output.

Prose uses of the words do NOT match. Parenthetical classifications at the
END of a claim are also not captured here — only explicit bullet-style labels.

Falls back gracefully: if a response contains no structured labels, the caller
(report.py) can still use the legacy regex count as a last-resort heuristic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Label(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    WEAKLY_GROUNDED = "weakly_grounded"


@dataclass
class LabeledClaim:
    """A single claim that was explicitly marked by the model with a label."""

    label: Label
    text: str
    line_num: int  # 1-indexed line within the response where the claim was found


# Bracketed bullet form: optional bullet marker, optional bold, bracketed label,
# optional colon/dash, then claim text.
#
# Matches:
#   [Observed] the refusal cited X
#   - [Observed] the refusal cited X
#   * **[Inferred]** pattern Y
#   - [Observed]: text
#   - [Weakly grounded] text
#
# Does NOT match:
#   I observed that the model...
#   the inferred cause...
_BRACKETED = re.compile(
    r"^[ \t]*(?:[-*+•][ \t]*)?(?:\*\*)?[ \t]*"  # optional bullet + optional bold open
    r"\[\s*(?P<label>Observed|Inferred|Weakly[\s-]grounded|Anchored)\s*\]"
    r"[ \t]*(?:\*\*)?"                     # optional bold close
    r"[ \t]*[:\-–]?[ \t]*"                 # optional separator
    r"(?P<text>[^\n]+?)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)

# Colon-prefix form (without brackets) — only accepted at line start after
# optional bullet, to avoid matching prose like "As I observed: ...".
#
# Matches:
#   Observed: the refusal cited X
#   - Observed: the refusal cited X
#   Inferred: the model is ...
_COLON_PREFIX = re.compile(
    r"^[ \t]*(?:[-*+•][ \t]*)?(?:\*\*)?[ \t]*"
    r"(?P<label>Observed|Inferred|Weakly[\s-]grounded|Anchored)"
    r"[ \t]*(?:\*\*)?[ \t]*:[ \t]*"
    r"(?P<text>[^\n]+?)[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)


def _normalize_label(raw: str) -> Label:
    norm = raw.lower().replace("-", " ").strip()
    if norm == "observed" or norm == "anchored":
        return Label.OBSERVED
    if norm == "inferred":
        return Label.INFERRED
    if norm == "weakly grounded":
        return Label.WEAKLY_GROUNDED
    raise ValueError(f"Unknown label: {raw!r}")


def parse_labeled_claims(text: str) -> list[LabeledClaim]:
    """Extract every explicitly-labeled claim from a response.

    Recognizes bracketed form ([Observed] ...) and colon-prefix form
    (Observed: ...). Duplicates across forms (same line matching both) are
    deduplicated by line number — bracketed takes precedence.
    """
    if not text:
        return []

    # Build a line number map for position -> line.
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def pos_to_line(pos: int) -> int:
        # Binary-ish: line_starts is sorted
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1  # 1-indexed

    claims: list[LabeledClaim] = []
    seen_lines: set[int] = set()

    for match in _BRACKETED.finditer(text):
        line = pos_to_line(match.start())
        if line in seen_lines:
            continue
        try:
            label = _normalize_label(match.group("label"))
        except ValueError:
            continue
        claim_text = match.group("text").strip()
        if not claim_text:
            continue
        claims.append(LabeledClaim(label=label, text=claim_text, line_num=line))
        seen_lines.add(line)

    for match in _COLON_PREFIX.finditer(text):
        line = pos_to_line(match.start())
        if line in seen_lines:
            continue
        try:
            label = _normalize_label(match.group("label"))
        except ValueError:
            continue
        claim_text = match.group("text").strip()
        # Colon form is more prone to matching single-word section headers
        # like "Observed:" on its own line followed by bulleted list. Require
        # at least 3 words of claim text to reduce false positives.
        if len(claim_text.split()) < 3:
            continue
        claims.append(LabeledClaim(label=label, text=claim_text, line_num=line))
        seen_lines.add(line)

    return sorted(claims, key=lambda c: c.line_num)


def count_structured_labels(text: str) -> dict[str, int]:
    """Count claims per label using structured parsing.

    Returns the same keys as report.count_labels for drop-in compatibility,
    plus a `weakly_grounded` key (treated as a form of Inferred for legacy
    aggregation — callers that want the 3-way split can use parse_labeled_claims).
    """
    claims = parse_labeled_claims(text)
    return {
        "observed": sum(1 for c in claims if c.label == Label.OBSERVED),
        "inferred": sum(
            1 for c in claims if c.label in (Label.INFERRED, Label.WEAKLY_GROUNDED)
        ),
        "weakly_grounded": sum(1 for c in claims if c.label == Label.WEAKLY_GROUNDED),
    }


def has_structured_labels(text: str) -> bool:
    """Quick check: did the model use structured labels at all?"""
    return bool(parse_labeled_claims(text))
