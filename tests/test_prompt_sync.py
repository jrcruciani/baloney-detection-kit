"""Structural distribution checks, not tests of live model triggering."""

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from bdk.interventions import list_interventions

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path("scripts/sync_prompts.py")
SPEC = importlib.util.spec_from_file_location("sync_prompts", ROOT / SCRIPT)
assert SPEC and SPEC.loader
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)

PUBLIC = tuple(Path(f"prompts/intervention/prompt-{name}.md") for name in list_interventions())
MIRRORS = tuple(Path("src/bdk/data/interventions") / path.name for path in PUBLIC)
SPANISH_PUBLIC = tuple(
    Path(f"prompts/intervention/es/prompt-{name}.md") for name in list_interventions(lang="es")
)
SPANISH_MIRRORS = tuple(sync.PACKAGED / "es" / path.name for path in SPANISH_PUBLIC)
ALL_PUBLIC = (*PUBLIC, *SPANISH_PUBLIC)
ALL_MIRRORS = (*MIRRORS, *SPANISH_MIRRORS)
ALL_WRAPPERS = (*sync.WRAPPERS, *sync.SPANISH_WRAPPERS)
DISTRIBUTIONS = (*ALL_PUBLIC, *ALL_MIRRORS, *ALL_WRAPPERS, sync.SKILL_TEXT)
PORTABLE_SOURCES = sync.portable_sources(ROOT)


def prompt_body(text):
    match = re.search(
        r"<!-- bdk:prompt:start -->\n```text\n(.*?)```\n<!-- bdk:prompt:end -->", text, re.S
    )
    assert match
    return match[1]


def snapshot(root):
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


@pytest.fixture
def repository(tmp_path):
    for path in {*DISTRIBUTIONS, SCRIPT, *PORTABLE_SOURCES, *PORTABLE_SOURCES.values()}:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, target)
    return tmp_path


def test_full_root_skill_and_plain_text_are_exactly_synchronized():
    canonical = (ROOT / sync.CANONICAL).read_text(encoding="utf-8")
    body = prompt_body(canonical)
    for path in sync.WRAPPERS:
        assert prompt_body((ROOT / path).read_text(encoding="utf-8")) == body
    assert (ROOT / sync.SKILL_TEXT).read_text(encoding="utf-8") == sync.VERSION_MARKER + "\n" + body
    spanish_body = prompt_body((ROOT / sync.SPANISH_CANONICAL).read_text(encoding="utf-8"))
    assert spanish_body != body
    for path in sync.SPANISH_WRAPPERS:
        assert prompt_body((ROOT / path).read_text(encoding="utf-8")) == spanish_body
    for source, mirror in zip(ALL_PUBLIC, ALL_MIRRORS, strict=True):
        assert (ROOT / source).read_bytes() == (ROOT / mirror).read_bytes()
    assert sync.synchronize(ROOT, check=True) == []


def test_distribution_inventory_covers_every_cli_variant_and_only_interventions():
    assert tuple(list_interventions()) == sync.VARIANTS
    assert tuple(list_interventions(lang="es")) == sync.SPANISH_VARIANTS
    assert set((ROOT / "prompts/intervention").rglob("prompt-*.md")) == {
        ROOT / p for p in ALL_PUBLIC
    }
    assert set((ROOT / sync.PACKAGED).rglob("*.md")) == {ROOT / p for p in ALL_MIRRORS}
    assert set(sync.outputs(ROOT)) == {
        *ALL_WRAPPERS,
        sync.SKILL_TEXT,
        *ALL_MIRRORS,
        *PORTABLE_SOURCES.values(),
    }


def test_spanish_full_preserves_machine_headings_labels_and_six_step_shape():
    english = prompt_body((ROOT / sync.CANONICAL).read_text(encoding="utf-8"))
    spanish = prompt_body((ROOT / sync.SPANISH_CANONICAL).read_text(encoding="utf-8"))
    heading_pattern = r"^[A-Z][A-Z 1-6:,-]+$"
    assert re.findall(heading_pattern, spanish, re.M) == re.findall(heading_pattern, english, re.M)
    light = spanish.split("LIGHT OUTPUT: 3-4 LINES, NOT THE FULL TEMPLATE\n", 1)[1]
    light = light.split("\n\nSTABILIZATION", 1)[0].splitlines()
    assert len(light) == 4
    assert [line.split(":", 1)[0] for line in light] == ["Claim", "Check", "Alternative", "Next"]
    assert re.findall(r"^([1-6])\. ", spanish, re.M) == list("123456")
    for body in (english, spanish):
        assert "Trigger -> Mode -> Protocol -> Output -> Review." in body
    heading = "FULL OUTPUT ONLY WHEN WARRANTED\n"
    assert spanish.split(heading)[1].split("\n\n")[0] == english.split(heading)[1].split("\n\n")[0]


def test_spanish_compact_preserves_gate_and_mode_identifiers():
    text = (ROOT / SPANISH_PUBLIC[0]).read_text(encoding="utf-8")
    assert re.findall(r"^(GATE [12]):", text, re.M) == ["GATE 1", "GATE 2"]
    assert re.findall(r"^- (Light|Full|Stabilization)\b", text, re.M) == [
        "Light",
        "Full",
        "Stabilization",
    ]


@pytest.mark.parametrize("path", DISTRIBUTIONS)
def test_intervention_markers_match_with_frontmatter_exception(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    assert text.count(sync.VERSION_MARKER) == 1
    if path == Path("skill/SKILL.md"):
        assert text.startswith("---\n")
        metadata, body = text[4:].split("\n---\n", 1)
        assert yaml.safe_load(metadata)["name"] == "baloney-detection-kit"
        assert body.startswith(sync.VERSION_MARKER + "\n")
    else:
        assert text.startswith(sync.VERSION_MARKER + "\n")


def test_size_budget_is_explicitly_an_estimate_not_model_tokenization():
    text = (ROOT / "ROOT_PROMPT.md").read_text(encoding="utf-8")
    body = prompt_body(text)
    # English characters / 4 is only a proxy; wrappers are measured separately.
    assert len(body) / 4 <= 1200
    assert len(text) / 4 <= 1450


def test_canonical_documents_safeguards_and_exact_light_output_shape():
    body = prompt_body((ROOT / sync.CANONICAL).read_text(encoding="utf-8"))
    normalized = " ".join(body.split())
    for phrase in (
        "ordinary how-to/explanatory questions with no claim",
        "fiction/casual creative speculation",
        "settled lookups",
        "preferences",
        "explicitly tentative brainstorming",
        "humble exploration seeking counter-evidence",
        "personal reports not generalized",
        "well-supported dissent",
        "empirical, causal/predictive, normative/policy, interpretive/historical, "
        "personal/experiential, or creative/hypothetical",
        "Separate novelty from truth, importance, and usefulness",
        "No universal falsifiability requirement",
        "relevance, directness, method quality, independence, replication/corroboration, "
        "recency, provenance, incentives, and missing data",
        "zero, one, or several",
        "Do not manufacture false balance",
        "Reopen for changed evidence, premises, scope, or facts",
        "testable, not established, effectiveness",
    ):
        assert phrase in normalized
    light = body.split("LIGHT OUTPUT: 3-4 LINES, NOT THE FULL TEMPLATE\n", 1)[1]
    light = light.split("\n\nSTABILIZATION", 1)[0].splitlines()
    assert len(light) == 4
    assert [line.split(":", 1)[0] for line in light] == ["Claim", "Check", "Alternative", "Next"]
    assert "otherwise omit this line" in light[2]
    assert re.findall(r"^([1-6])\. ", body, re.M) == list("123456")


@pytest.mark.parametrize("path", PUBLIC)
def test_variants_document_two_gates_modes_and_shared_boundaries(path):
    text = " ".join((ROOT / path).read_text(encoding="utf-8").split())
    for phrase in (
        "GATE 1",
        "GATE 2",
        "confidence-evidence mismatch",
        "novelty",
        "importance",
        "endorsement/persuasion/action before checks",
        "against-consensus/suppression/",
        "evade evidence",
        "repeated pressure",
        "Disagreement alone",
        "high-stakes domain alone never forces Full",
        "threshold when evaluating a claim",
        "3-4 lines",
        "Stabilization",
        "premises",
        "facts",
        "stubbornness",
        "false balance",
        "critique diversity",
        "independent evidence",
        "qualified human expertise",
    ):
        assert phrase.casefold() in text.casefold(), (path, phrase)


def test_skill_resources_exist_and_invalid_legacy_reference_is_absent():
    text = (ROOT / "skill/SKILL.md").read_text(encoding="utf-8")
    resources = re.findall(r"^- `([^`]+)` - ", text.split("## Resources\n", 1)[1], re.M)
    assert len(resources) == 7
    for resource in resources:
        assert (ROOT / "skill" / resource).is_file(), resource
    forbidden_hierarchy = " > ".join(("peer-reviewed", "expert opinion", "anecdote"))
    files = [ROOT / "ROOT_PROMPT.md"]
    for folder in ("prompts/intervention", "skill"):
        files.extend(p for p in (ROOT / folder).rglob("*") if p.suffix in {".md", ".txt"})
    for path in files:
        content = path.read_text(encoding="utf-8")
        assert forbidden_hierarchy not in content
        assert "apply_kit" not in content


def test_sync_preserves_wrapper_prose_frontmatter_resources_and_is_idempotent(repository):
    expected_wrappers = {}
    for path in ALL_WRAPPERS:
        text = sync.read_text(repository / path)
        prefix, _, suffix = sync.split_region(text, str(path))
        prefix = prefix.replace(sync.START, "Outside prose: preserve me.\n\n" + sync.START)
        suffix += "\nOutside footer: preserve me too.\n"
        if path.name == "SKILL.md":
            prefix = prefix.replace(
                "name: baloney-detection-kit", "name: custom-name\ncustom: keep"
            )
        else:
            prefix = prefix.replace("\n", "\r\n")
            suffix = suffix.replace("\n", "\r\n")
        expected_wrappers[path] = (prefix, suffix)
        (repository / path).write_bytes((prefix + "\nStale generated region.\n" + suffix).encode())

    untouched = (
        "prompts/diagnosis/card.md",
        "src/bdk/data/diagnostic-sentinel.md",
        "validation/closed-loop/historical.md",
        "skill/examples/historical.md",
        "skill/checklist/review_rubric.md",
    )
    for name in untouched:
        target = repository / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("Unrelated/historical content; do not assign intervention versions.\n")

    before = snapshot(repository)
    expected = {
        *ALL_WRAPPERS,
        sync.PORTABLE_SKILL / "SKILL.md",
        sync.PORTABLE_SKILL / "examples/historical.md",
        sync.PORTABLE_SKILL / "checklist/review_rubric.md",
    }
    assert set(sync.synchronize(repository, check=True)) == expected
    assert snapshot(repository) == before
    assert set(sync.synchronize(repository)) == expected
    for path, (expected_prefix, expected_suffix) in expected_wrappers.items():
        prefix, _, suffix = sync.split_region(sync.read_text(repository / path), str(path))
        assert (prefix, suffix) == (expected_prefix, expected_suffix)
    for name in untouched:
        assert (repository / name).read_bytes() == before[Path(name)]
    after = snapshot(repository)
    mtimes = {path: (repository / path).stat().st_mtime_ns for path in after}
    assert sync.synchronize(repository) == []
    assert sync.synchronize(repository, check=True) == []
    assert snapshot(repository) == after
    assert {path: (repository / path).stat().st_mtime_ns for path in after} == mtimes


def test_canonical_and_specialized_edits_propagate_to_exact_targets(repository):
    spanish_before = {
        path: (repository / path).read_bytes()
        for path in (*SPANISH_PUBLIC, *SPANISH_MIRRORS, *sync.SPANISH_WRAPPERS)
    }
    canonical = repository / sync.CANONICAL
    canonical.write_text(sync.read_text(canonical).replace("Admit unknowns.", "Disclose unknowns."))
    specialized = repository / PUBLIC[0]
    specialized.write_text(sync.read_text(specialized) + "\nNew specialized wrapper.\n")
    expected = {
        *sync.WRAPPERS,
        sync.SKILL_TEXT,
        MIRRORS[0],
        MIRRORS[1],
        PORTABLE_SOURCES[Path("skill/SKILL.md")],
        PORTABLE_SOURCES[sync.SKILL_TEXT],
        PORTABLE_SOURCES[sync.CANONICAL],
    }
    assert set(sync.synchronize(repository)) == expected
    body = prompt_body(sync.read_text(canonical))
    for path in sync.WRAPPERS:
        assert prompt_body(sync.read_text(repository / path)) == body
    assert sync.read_text(repository / sync.SKILL_TEXT) == sync.VERSION_MARKER + "\n" + body
    assert {path: (repository / path).read_bytes() for path in spanish_before} == spanish_before
    assert sync.synchronize(repository, check=True) == []


def test_spanish_edits_only_propagate_to_spanish_root_and_mirrors(repository):
    before = snapshot(repository)
    canonical = repository / sync.SPANISH_CANONICAL
    canonical.write_text(
        sync.read_text(canonical).replace("Reconoce las incógnitas.", "Declara las incógnitas."),
        encoding="utf-8",
    )
    compact = repository / SPANISH_PUBLIC[0]
    compact.write_text(sync.read_text(compact) + "\nWrapper de prueba.\n", encoding="utf-8")
    expected = {*sync.SPANISH_WRAPPERS, *SPANISH_MIRRORS}
    assert set(sync.synchronize(repository, check=True)) == expected
    assert set(sync.synchronize(repository)) == expected
    after = snapshot(repository)
    assert {path for path in before if before[path] != after[path]} == {*expected, *SPANISH_PUBLIC}
    assert prompt_body(sync.read_text(repository / sync.SPANISH_WRAPPERS[0])) == prompt_body(
        sync.read_text(canonical)
    )
    assert sync.synchronize(repository, check=True) == []


@pytest.mark.parametrize("path", (*ALL_MIRRORS, sync.SKILL_TEXT, *PORTABLE_SOURCES.values()))
def test_missing_whole_file_outputs_are_reported_and_recreated(repository, path):
    expected = (repository / path).read_bytes()
    (repository / path).unlink()
    assert sync.synchronize(repository, check=True) == [path]
    assert not (repository / path).exists()
    assert sync.synchronize(repository) == [path]
    assert (repository / path).read_bytes() == expected


@pytest.mark.parametrize("path", (*ALL_PUBLIC, *ALL_WRAPPERS))
def test_missing_source_or_wrapper_fails_before_any_writes(repository, path):
    (repository / path).unlink()
    (repository / sync.SKILL_TEXT).write_text("stale output")
    before = snapshot(repository)
    with pytest.raises(FileNotFoundError):
        sync.synchronize(repository)
    assert snapshot(repository) == before


@pytest.mark.parametrize(
    "malformed",
    [
        sync.START + "\nno end",
        sync.END + "\n" + sync.START,
        sync.START + sync.START + sync.END,
        sync.START + sync.END + sync.END,
    ],
)
def test_invalid_region_fails_explicitly(malformed):
    with pytest.raises(ValueError, match="marker"):
        sync.split_region(malformed, "fixture")


@pytest.mark.parametrize("path", [sync.CANONICAL, sync.SPANISH_CANONICAL, *ALL_WRAPPERS])
@pytest.mark.parametrize("defect", ["missing", "duplicate", "reversed"])
def test_invalid_marked_sources_and_wrappers_fail_before_any_writes(repository, path, defect):
    target = repository / path
    text = sync.read_text(target)
    prefix, region, suffix = sync.split_region(text, str(path))
    if defect == "missing":
        text = text.replace(sync.START, "")
    elif defect == "duplicate":
        text = text.replace(sync.START, sync.START * 2)
    else:
        text = prefix.replace(sync.START, sync.END) + region + suffix.replace(sync.END, sync.START)
    target.write_text(text, encoding="utf-8")
    (repository / sync.SKILL_TEXT).write_text("stale output")
    before = snapshot(repository)
    with pytest.raises(ValueError, match="marker"):
        sync.synchronize(repository)
    assert snapshot(repository) == before


@pytest.mark.parametrize("canonical", [sync.CANONICAL, sync.SPANISH_CANONICAL])
@pytest.mark.parametrize(
    "region",
    [
        "\n```text\n```\n",
        "\n```text\n\n```\n",
        "\n```\nprompt\n```\n",
        "\n```text\nprompt\n```\n```text\nanother\n```\n",
        "\nnot a fenced prompt\n",
    ],
)
def test_malformed_canonical_block_fails_before_writes(repository, region, canonical):
    source = repository / canonical
    prefix, _, suffix = sync.split_region(sync.read_text(source), str(source))
    source.write_text(prefix + region + suffix)
    (repository / sync.SKILL_TEXT).write_text("stale output")
    before = snapshot(repository)
    with pytest.raises(ValueError, match="fenced text prompt"):
        sync.synchronize(repository)
    assert snapshot(repository) == before


@pytest.mark.parametrize("path", (*ALL_PUBLIC, *ALL_WRAPPERS))
@pytest.mark.parametrize("replacement", ["", "<!-- bdk prompt-v1.0 -->", sync.VERSION_MARKER * 2])
def test_bad_source_or_wrapper_version_fails_before_writes(repository, path, replacement):
    target = repository / path
    target.write_text(sync.read_text(target).replace(sync.VERSION_MARKER, replacement))
    (repository / sync.SKILL_TEXT).write_text("stale")
    before = snapshot(repository)
    with pytest.raises(ValueError, match="expected one"):
        sync.synchronize(repository)
    assert snapshot(repository) == before


def test_skill_marker_must_follow_valid_frontmatter(repository):
    skill = repository / "skill/SKILL.md"
    text = sync.read_text(skill)
    for malformed in (
        sync.VERSION_MARKER + "\n" + text.replace(sync.VERSION_MARKER + "\n", ""),
        text.replace("\n---\n", "\n", 1),
        text.replace("\n---\n", "\n---\n\n", 1),
    ):
        skill.write_text(malformed)
        with pytest.raises(ValueError, match="frontmatter"):
            sync.synchronize(repository)


def test_cli_checks_without_writes_and_runs_from_another_working_directory(repository):
    command = [sys.executable, str(repository / SCRIPT)]
    target = repository / sync.SKILL_TEXT
    target.write_text("stale output")
    before = snapshot(repository)
    result = subprocess.run(command + ["--check"], cwd=repository.parent, capture_output=True)
    assert result.returncode == 1
    assert str(sync.SKILL_TEXT).encode() in result.stdout
    assert b"regenerate" in result.stderr
    assert snapshot(repository) == before
    assert subprocess.run(command, cwd=repository.parent, capture_output=True).returncode == 0
    result = subprocess.run(command + ["--check"], cwd=repository.parent, capture_output=True)
    assert result.returncode == 0
    assert b"are synchronized" in result.stdout

    (repository / "ROOT_PROMPT.md").write_text("Missing markers and version")
    before = snapshot(repository)
    result = subprocess.run(command, cwd=repository.parent, capture_output=True)
    assert result.returncode == 2
    assert b"Prompt synchronization failed" in result.stderr
    assert snapshot(repository) == before
