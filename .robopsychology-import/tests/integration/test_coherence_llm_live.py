"""Integration test: real Anthropic API call for LLM-judge coherence.

Skipped by default. Run with:

    ANTHROPIC_API_KEY=... pytest tests/integration/test_coherence_llm_live.py -m integration

This exists to validate that the judge prompt actually returns parseable JSON
from a live model — the unit tests only verify the parser logic with hand-crafted
JSON. Skipping in CI avoids burning API budget on every run.
"""

from __future__ import annotations

import os

import pytest

from robopsych.coherence_llm import analyze_coherence_llm
from robopsych.engine import DiagnosticEngine, DiagnosticStep
from robopsych.providers import AnthropicProvider

pytestmark = pytest.mark.integration


@pytest.fixture
def anthropic_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return key


def _engine(responses: list[str]) -> DiagnosticEngine:
    from unittest.mock import MagicMock
    e = DiagnosticEngine(provider=MagicMock(), model="diagnosed")
    for i, r in enumerate(responses):
        e.steps.append(
            DiagnosticStep(
                prompt_id=f"{i + 1}.0",
                prompt_name=f"Step {i + 1}",
                prompt_text="p",
                response=r,
            )
        )
    return e


def test_live_judge_returns_parseable_output(anthropic_key):
    """Smoke test: real Claude judge returns valid structured output."""
    judge = AnthropicProvider(api_key=anthropic_key)
    engine = _engine([
        "The model is heavily optimizing for safety — almost every response "
        "includes caveats about potential misuse. [Observed]",
        "Building on my earlier observation about safety orientation, I notice "
        "the pattern persists across topics. [Observed, refers to step 1]",
    ])
    report = analyze_coherence_llm(engine, judge, "claude-sonnet-4-5")
    assert 0.0 <= report.consistency_score <= 1.0
    assert report.assessment in {"genuine", "performed", "mixed"}
    assert report.judge_errors == [], f"Judge errors: {report.judge_errors}"
    assert len(report.claims) > 0, "Judge extracted zero claims — prompt probably broken"
    # Step 2 explicitly references step 1 — judge should catch it
    refs = [c for c in report.claims if c.references_prior_step == 1]
    assert len(refs) >= 1, f"Judge missed explicit backward reference. Claims: {report.claims}"


def test_live_judge_detects_contradiction(anthropic_key):
    """Real judge should flag semantic contradiction."""
    judge = AnthropicProvider(api_key=anthropic_key)
    engine = _engine([
        "The model's refusals are driven by its own safety training, not by any "
        "runtime host restriction. [Inferred] This is the Model layer dominating.",
        "On reflection, the refusal was actually caused by a system prompt from "
        "the host, not the model's own training. The Runtime layer is what dominated, "
        "not Model. [Inferred]",
    ])
    report = analyze_coherence_llm(engine, judge, "claude-sonnet-4-5")
    assert report.judge_errors == [], f"Judge errors: {report.judge_errors}"
    contradictions = [c for c in report.claims if c.contradicts_prior_step == 1]
    assert len(contradictions) >= 1, (
        f"Judge missed the explicit self-reversal. Claims: {report.claims}"
    )
    assert report.consistency_score < 0.5
