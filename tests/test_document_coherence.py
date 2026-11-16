"""Offline tripwires for known obsolete prescriptions, not a semantic oracle."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_ROOTS = ("essay/", "posts/", "research/diagnosis-paper/", "docs/plans/")
RULES = {
    "mandatory-alternatives": (
        r"\b(?:at least|minimum of|must (?:include|provide|offer)|always (?:include|provide|offer))"
        r" (?:two|2) (?:credible )?alternatives\b|\balternative [12]\s*:"
    ),
    "fixed-source-ladder": (
        r"\bpeer[- ]reviewed\s*>\s*expert(?: synthesis| opinion)?\s*>"
        r"|\buse (?:this|the following) (?:evidence |source )?hierarchy\b"
    ),
    "category-scoring": (
        r"\b3\s*[/,]\s*2\s*[/,]\s*1\s*[/,]\s*0\b"
        r"|\bpeer[- ]reviewed\s*(?:=|:)\s*3\b"
    ),
    "universal-falsifiability": (
        r"\bunfalsifiable\s*\(?and therefore not scientific\)?"
        r"|\b(?:unfalsifiable|non[- ]falsifiable) claims? (?:must|always|should) "
        r"(?:get|receive|score|be (?:scored|assigned)) (?:a )?(?:zero|0)\b"
        r"|\bif (?:a claim is )?unfalsifiable, (?:score|assign|give) (?:it )?(?:zero|0)\b"
    ),
    "domain-or-dissent-trigger": (
        r"\b(?:high[- ]stakes (?:domain|content)|(?:consensus )?dissent|disagreement)"
        r" alone (?:is (?:a|the) trigger|triggers? (?:intervention|full)|"
        r"(?:forces?|requires?) full)\b"
        r"|\b(?:always|must) (?:use|apply) full (?:mode )?(?:for|in) "
        r"(?:high[- ]stakes|medical|political|financial) (?:domains?|topics?|questions?)\b"
    ),
    "verdict-inertia": r"\bkeep the prior verdict unless new evidence appears\b",
    "user-label": r"\byou(?:'re| are) likely in a personal cult\b|\byou might be in a mini-cult\b",
    "forced-full-template": r"\buse this exact structure\b",
    "obsolete-tooling-denial": (
        r"\b(?:it|bdk|this (?:repo(?:sitory)?|project)) (?:has|ships|provides|includes) no "
        r"(?:package(?: api)?|runner|benchmark|evaluator)\b"
        r"|\bno runner,\s*no benchmark,\s*no package(?: api)?,\s*no evaluator\b"
        r"|\bkeep (?:all )?(?:automated )?(?:evaluators|provider[- ]specific code)"
        r" (?:outside this repo(?:sitory)?|downstream)\b"
    ),
    "obsolete-product-or-path": (
        r"\brobopsychology now ships\b|\bjrcruciani/robopsychology\b"
        r"|\bprompts/prompt-agent\.md\b|\bscripts/apply_kit\.py\b"
    ),
}


def distributed(path):
    name = path.as_posix()
    return (
        path.suffix.lower() in {".md", ".markdown"}
        and not name.startswith(HISTORICAL_ROOTS)
        and name != "CHANGELOG.md"
        and "results" not in path.parts
        and not (path.parts[0] == "validation" and "artifacts" in path.parts)
    )


def contradictions(text):
    # Keep quoted instructions and code examples unless explicitly identified as
    # rejected responses. Quotation marks alone are not a safe exemption.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    paragraphs = re.split(r"\n\s*\n", text)
    rejected_quote = False
    found = set()
    for paragraph in paragraphs:
        normalized = " ".join(paragraph.split())
        if re.fullmatch(r"\*\*(?:also )?bad(?: response)?:\*\*", normalized, re.I):
            rejected_quote = True
            continue
        if rejected_quote and normalized.startswith(">"):
            continue
        rejected_quote = False
        for sentence in re.split(r"(?<=[.!?;])\s+", normalized):
            for rule, pattern in RULES.items():
                for match in re.finditer(pattern, sentence, flags=re.I):
                    prefix = sentence[: match.start()]
                    if re.search(
                        r"\b(?:do not|does not|must not|never|avoid|reject|rather than|"
                        r"instead of|no longer)"
                        r"(?:\s+(?:require|say|saying|write|writing|include|mandate|"
                        r"that|the|rule|instruction|obsolete|claim))*[\s:\"'`]*$",
                        prefix,
                        flags=re.I,
                    ):
                        continue
                    found.add(rule)
    return found


def test_distributed_markdown_has_no_known_protocol_contradictions():
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = sorted({Path(name.decode()) for name in result.stdout.split(b"\0") if name})
    scanned = [path for path in paths if distributed(path) and (ROOT / path).is_file()]
    assert {
        Path("PLAYBOOK.md"),
        Path("skill/checklist/seven_questions.md"),
        Path("skill/examples/playbook_scenarios.md"),
        Path("skills/baloney-detection-kit/SKILL.md"),
        Path("src/bdk/data/interventions/prompt-full.md"),
    } <= set(scanned)
    failures = {
        str(path): sorted(issues)
        for path in scanned
        if (issues := contradictions((ROOT / path).read_text(encoding="utf-8")))
    }
    assert not failures, (
        "Distributed docs contradict prompts/intervention/prompt-full.md; "
        f"review context, edit sources, then regenerate: {failures}"
    )


@pytest.mark.parametrize(
    "rule,text",
    [
        ("mandatory-alternatives", "Include at least two alternatives."),
        ("mandatory-alternatives", "Alternative 1: [required]\nAlternative 2: [required]"),
        ("fixed-source-ladder", "Rank peer-reviewed > expert synthesis > anecdotes > intuition."),
        ("fixed-source-ladder", "Use this hierarchy when weighing diagnostic support."),
        ("category-scoring", "Assign evidence categories 3/2/1/0."),
        ("universal-falsifiability", "Unfalsifiable (and therefore not scientific)."),
        ("universal-falsifiability", "Unfalsifiable claims must receive zero."),
        ("universal-falsifiability", "If unfalsifiable, score 0."),
        ("domain-or-dissent-trigger", "A high-stakes domain alone forces Full."),
        ("domain-or-dissent-trigger", "Consensus dissent alone is a trigger."),
        ("domain-or-dissent-trigger", "Always use Full mode for medical questions."),
        ("verdict-inertia", "Keep the prior verdict unless new evidence appears."),
        ("user-label", "You're likely in a personal cult."),
        ("user-label", "You might be in a mini-cult."),
        ("forced-full-template", "Use this exact structure: [full template]."),
        ("obsolete-tooling-denial", "It has no package API."),
        ("obsolete-tooling-denial", "This project has no package."),
        ("obsolete-tooling-denial", "BDK has no package."),
        ("obsolete-tooling-denial", "No runner, no benchmark, no package, no evaluator."),
        ("obsolete-tooling-denial", "BDK includes no runner."),
        ("obsolete-tooling-denial", "Keep automated evaluators outside this repo."),
        ("obsolete-product-or-path", "Robopsychology now ships as the diagnostic layer."),
        ("obsolete-product-or-path", "Copy prompts/prompt-agent.md."),
    ],
)
def test_obsolete_prescriptions_fail_even_inside_quotes_or_copyable_blocks(rule, text):
    for wrapper in ("{}", "> {}", "```text\n{}\n```"):
        assert rule in contradictions(wrapper.format(text))


@pytest.mark.parametrize(
    "text",
    [
        "Do not require at least two alternatives.",
        "Never use this exact structure for every response.",
        "Reject the rule: Keep the prior verdict unless new evidence appears.",
        "Avoid saying you're likely in a personal cult.",
        "**Bad response:**\n\n> You might be in a mini-cult.\n\n**Why bad:** humiliating.",
        "There is no universal falsifiability requirement.",
        "A high-stakes domain alone never forces Full.",
        "Disagreement alone is not a verdict or trigger.",
        "The framework is not a fact-checker or benchmark. BDK includes reference evaluators.",
        "This framework is not a benchmark or fact-checker.",
        "Do not say: No runner, no benchmark, no package, no evaluator.",
        "Reject the claim: This project has no package.",
        "Require at least two judge model families, not two explanations.",
        "Include only credible alternatives, zero, one, or several.",
        "Credible alternatives:\n\n1. Generalized representation.\n2. Surface statistics.",
        "A claim can be unfalsifiable without being an empirical scientific claim.",
    ],
)
def test_negations_rejected_examples_and_legitimate_protocol_language_pass(text):
    assert contradictions(text) == set()


def test_bad_example_exemption_does_not_leak_into_subsequent_instructions():
    text = "**Bad response:**\n\n> You might be in a mini-cult.\n\nUse this exact structure."
    assert contradictions(text) == {"forced-full-template"}
    assert contradictions("Do not fabricate sources, and include at least two alternatives.") == {
        "mandatory-alternatives"
    }


def test_nontrigger_sketches_do_not_offer_an_intervention_mode():
    text = (ROOT / "skill/examples/playbook_scenarios.md").read_text(encoding="utf-8")
    for number in (2, 11, 14):
        section = text.split(f"## {number}. ", 1)[1].split("\n## ", 1)[0]
        mode = section.split("**Mode:** ", 1)[1].split("\n\n", 1)[0].casefold()
        assert "ordinary" in mode
        assert "no intervention" in mode
        assert not re.search(r"\b(?:light|full|stabilization)\b", mode)


@pytest.mark.parametrize(
    "path,expected",
    [
        ("essay/mini-cultos-ai.md", False),
        ("posts/reddit.md", False),
        ("research/diagnosis-paper/README.md", False),
        ("docs/plans/cleanup-audit.md", False),
        ("CHANGELOG.md", False),
        ("validation/diagnosis/case/artifacts/report.md", False),
        ("validation/closed-loop/results/findings.md", False),
        ("results/summary.md", False),
        ("validation/closed-loop/PROTOCOL.md", True),
        ("skill/examples/complete_conversations.md", True),
        ("templates/diagnosis/incident-diagnosis.md", True),
        ("docs/integration.md", True),
    ],
)
def test_inventory_excludes_protected_prose_and_history_not_current_guidance(path, expected):
    assert distributed(Path(path)) == expected
