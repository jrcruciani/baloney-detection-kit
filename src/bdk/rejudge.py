"""Judge-only analysis of captured reports, never fresh target sampling."""

from __future__ import annotations

import json
from dataclasses import asdict

from bdk.coherence_llm import analyze_coherence_auto
from bdk.crosscheck import judge_saved_ab
from bdk.engine import DiagnosticEngine, DiagnosticStep
from bdk.providers import Provider
from bdk.scenario_checks import analyze_stance
from bdk.scenarios import parse_scenario
from bdk.security import safe_exception_message


class _StrictCoherenceJudge(Provider):
    """Reject missing/coerced labels before the legacy scorer can default them."""

    def __init__(self, provider: Provider):
        self.provider = provider
        self.name = provider.name

    def send(
        self,
        messages: list[dict],
        model: str,
        *,
        temperature: float | None = None,
        response_format: dict | None = None,
    ) -> str:
        options: dict = {}
        if temperature is not None:
            options["temperature"] = temperature
        if response_format is not None:
            options["response_format"] = response_format
        raw = self.provider.send(messages, model, **options)
        data = json.loads(raw)
        if not isinstance(data, dict) or not isinstance(data.get("claims"), list):
            raise ValueError("coherence judge requires a claims list")
        for claim in data["claims"]:
            if not isinstance(claim, dict):
                raise ValueError("coherence judge claim must be an object")
            for key in ("text", "contradiction_explanation"):
                if not isinstance(claim.get(key), str):
                    raise ValueError(f"coherence judge requires string {key}")
            if not claim["text"].strip() or type(claim.get("is_fresh_claim")) is not bool:
                raise ValueError("coherence judge requires claim text and boolean freshness")
            for key, labels in (
                ("layer", ("model", "runtime", "conversation", "meta", "other")),
                ("self_label", ("observed", "inferred", "unlabeled")),
                ("severity", ("high", "medium", "low")),
            ):
                if claim.get(key) not in labels:
                    raise ValueError(f"invalid coherence judge {key}")
            for key in ("contradicts_prior_step", "references_prior_step"):
                if key not in claim or (claim[key] is not None and type(claim[key]) is not int):
                    raise ValueError(f"coherence judge requires integer or null {key}")
        return raw


def validate_saved_report(data: object) -> dict:
    if not isinstance(data, dict) or not isinstance(data.get("model"), str):
        raise ValueError("saved report must include its raw target model ID")
    steps = data.get("steps", [])
    if not isinstance(steps, list):
        raise ValueError("steps must be a list")
    for step in steps:
        if not isinstance(step, dict) or any(
            not isinstance(step.get(key), str)
            for key in ("prompt_id", "prompt_name", "prompt_text", "response")
        ):
            raise ValueError("malformed saved diagnostic step")
    pair = data.get("ab_test")
    if pair is None and "original_response" in data:
        pair = data
    if pair is not None and (
        not isinstance(pair, dict)
        or any(
            not isinstance(pair.get(key), str) or not pair[key].strip()
            for key in ("original_task", "inverted_task", "original_response", "inverted_response")
        )
    ):
        raise ValueError("saved A/B pair requires both tasks and both responses")
    items = data.get("scenarios", [])
    if "scenario_validation" in data:
        items = [data["scenario_validation"]]
    if not isinstance(items, list):
        raise ValueError("scenarios must be a list")
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("scenario result must be an object")
        scenario = parse_scenario(item.get("scenario"), saved=True)
        transcript = item.get("transcript")
        if not isinstance(transcript, list) or len(transcript) != 1 + 2 * len(
            scenario.user_messages
        ):
            raise ValueError("saved scenario requires a complete transcript")
        if transcript[0] != {"role": "system", "content": scenario.system_prompt}:
            raise ValueError("saved scenario prompt mismatch")
        for i, user in enumerate(scenario.user_messages):
            if transcript[1 + i * 2] != {"role": "user", "content": user}:
                raise ValueError("saved scenario task mismatch")
            reply = transcript[2 + i * 2]
            if (
                not isinstance(reply, dict)
                or reply.get("role") != "assistant"
                or (not isinstance(reply.get("content"), str) or not reply["content"].strip())
            ):
                raise ValueError("saved scenario response missing")
    if not steps and pair is None and not any(item["scenario"].get("turns") for item in items):
        raise ValueError(
            "report has no diagnostic steps, A/B pair, or multi-turn conversation to judge"
        )
    return {"data": data, "steps": steps, "pair": pair, "scenarios": items}


def rejudge_report(
    validated: dict, provider: Provider, model: str, family: str, source_sha256: str
) -> dict:
    data = validated["data"]
    result: dict = {
        "source_sha256": source_sha256,
        "target_model": data["model"],
        "judge_model": model,
        "judge_family": family,
        "judge_provider": provider.name,
        "label": "Inferred",
        "target_rerun": False,
        "errors": [],
    }
    if validated["pair"] is not None:
        try:
            result["ab_test"] = asdict(judge_saved_ab(validated["pair"], provider, model))
        except Exception as exc:
            result["ab_test"] = None
            result["errors"].append(safe_exception_message(exc))
    if validated["steps"]:
        engine = DiagnosticEngine(provider=provider, model=data["model"])
        engine.steps = [
            DiagnosticStep(
                **{key: row[key] for key in ("prompt_id", "prompt_name", "prompt_text", "response")}
            )
            for row in validated["steps"]
        ]
        engine.initial_response = data.get("initial_response")
        try:
            coherence = analyze_coherence_auto(
                engine, judge_provider=_StrictCoherenceJudge(provider), judge_model=model
            )
            result["coherence"] = asdict(coherence)
            result["errors"].extend(coherence.judge_errors)
            if coherence.judge_errors or not any(c.step_num >= 2 for c in coherence.claims):
                result["coherence"].update(
                    status="unavailable",
                    consistency_score=None,
                    assessment=None,
                    coherence_axes=None,
                )
                if not coherence.judge_errors:
                    result["errors"].append("No eligible judged claims; coherence is unestimable.")
            else:
                result["coherence"]["status"] = "scored"
        except Exception as exc:
            result["coherence"] = None
            result["errors"].append(safe_exception_message(exc))
    result["scenarios"] = []
    for item in validated["scenarios"]:
        scenario = parse_scenario(item["scenario"], saved=True)
        if not scenario.turns:
            continue
        stance = analyze_stance(scenario, item["transcript"], provider, model)
        result["scenarios"].append(
            {"scenario_id": scenario.provenance["scenario_id"], "stance": stance}
        )
        if stance["status"] != "scored":
            result["errors"].append(
                stance.get("error", "Unknown stance transitions or evidence reassessments")
            )
    result["status"] = "incomplete" if result["errors"] else "scored"
    return result
