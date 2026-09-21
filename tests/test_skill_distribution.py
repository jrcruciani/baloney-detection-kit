"""Offline distribution contracts, not evidence of runtime invocation or efficacy."""

import importlib.util
import json
import re
import shutil
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync_prompts", ROOT / "scripts/sync_prompts.py")
assert SPEC and SPEC.loader
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)
LINK_SPEC = importlib.util.spec_from_file_location(
    "check_markdown_links", ROOT / "scripts/check_markdown_links.py"
)
assert LINK_SPEC and LINK_SPEC.loader
links = importlib.util.module_from_spec(LINK_SPEC)
LINK_SPEC.loader.exec_module(links)

PORTABLE = sync.PORTABLE_SKILL
SOURCES = sync.portable_sources(ROOT)
LEGACY_FILES = {
    path.relative_to(ROOT / "skill") for path in (ROOT / "skill").rglob("*") if path.is_file()
}
SUPPORT_FILES = {
    Path("PLAYBOOK.md"): Path("resources/PLAYBOOK.md"),
    Path("prompts/intervention/prompt-full.md"): Path(
        "resources/prompts/intervention/prompt-full.md"
    ),
    Path("docs/second-opinion-operational.md"): Path(
        "resources/docs/second-opinion-operational.md"
    ),
    Path("LICENSE"): Path("LICENSE"),
    Path("NOTICE"): Path("NOTICE"),
}


def snapshot(root):
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


@pytest.fixture
def repository(tmp_path):
    inputs = {
        *SOURCES,
        *sync.WRAPPERS,
        *sync.SPANISH_WRAPPERS,
        *(sync.CANONICAL.parent / f"prompt-{name}.md" for name in sync.VARIANTS),
        *(sync.SPANISH_CANONICAL.parent / f"prompt-{name}.md" for name in sync.SPANISH_VARIANTS),
    }
    for relative in {*inputs, *sync.outputs(ROOT)}:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def test_portable_inventory_is_complete_and_has_no_symlinks():
    expected = {PORTABLE / path for path in LEGACY_FILES | set(SUPPORT_FILES.values())}
    assert set(SOURCES.values()) == expected
    assert {
        path.relative_to(ROOT) for path in (ROOT / PORTABLE).rglob("*") if path.is_file()
    } == expected
    assert sync.SKILL_RESOURCES == SUPPORT_FILES
    assert all(not path.is_symlink() for path in (ROOT / PORTABLE).rglob("*"))
    assert all(not source.is_relative_to(PORTABLE) for source in SOURCES)


@pytest.mark.parametrize("source,target", SOURCES.items())
def test_every_copied_file_matches_its_source_with_only_declared_path_rewrites(source, target):
    content = (ROOT / source).read_bytes()
    for old, new in sync.PORTABLE_REPLACEMENTS.get(source, {}).items():
        content = content.replace(old.encode(), new.encode())
    assert (ROOT / target).read_bytes() == content
    assert sync.outputs(ROOT)[target] == content


def test_skill_frontmatter_prompt_block_and_resource_inventory_are_preserved():
    legacy = sync.read_text(ROOT / "skill/SKILL.md")
    portable = sync.read_text(ROOT / PORTABLE / "SKILL.md")
    assert legacy.split("\n---\n", 1)[0] == portable.split("\n---\n", 1)[0]
    metadata = yaml.safe_load(portable[4:].split("\n---\n", 1)[0])
    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == PORTABLE.name
    assert sync.split_region(legacy, "legacy")[1] == sync.split_region(portable, "portable")[1]
    sync.check_version(portable, "portable", skill=True)
    for relative in (
        Path("prompts/critical_investigation_mode.txt"),
        SUPPORT_FILES[sync.CANONICAL],
    ):
        sync.check_version(sync.read_text(ROOT / PORTABLE / relative), str(relative))
    resources = re.findall(r"^- `([^`]+)` - ", portable.split("## Resources\n", 1)[1], re.M)
    assert len(resources) == 7
    assert resources[0] == "resources/PLAYBOOK.md"
    for resource in resources:
        target = (ROOT / PORTABLE / resource).resolve()
        assert target.is_relative_to(ROOT / PORTABLE)
        assert target.is_file()


def test_all_links_work_after_copying_only_the_portable_directory(tmp_path):
    installed = tmp_path / ".agents/skills/baloney-detection-kit"
    shutil.copytree(ROOT / PORTABLE, installed)
    assert not (tmp_path / "PLAYBOOK.md").exists()
    for path in installed.rglob("*.md"):
        assert links.check_markdown(path, installed) == []
    assert (installed / "resources/docs/second-opinion-operational.md").is_file()
    assert (installed / "resources/prompts/intervention/prompt-full.md").read_bytes() == (
        ROOT / sync.CANONICAL
    ).read_bytes()


def test_offline_link_scanner_includes_portable_markdown():
    scanned = set(links.markdown_files(ROOT))
    assert set((ROOT / PORTABLE).rglob("*.md")) <= scanned


@pytest.mark.parametrize("source,target", SOURCES.items())
def test_each_copy_detects_drift_and_regenerates_without_touching_sources(
    repository, source, target
):
    original = (repository / target).read_bytes()
    before_sources = {path: (repository / path).read_bytes() for path in SOURCES}
    (repository / target).write_bytes(b"stale output")
    assert sync.synchronize(repository, check=True) == [target]
    assert (repository / target).read_bytes() == b"stale output"
    assert sync.synchronize(repository) == [target]
    assert (repository / target).read_bytes() == original
    assert {path: (repository / path).read_bytes() for path in SOURCES} == before_sources
    assert sync.synchronize(repository, check=True) == []


@pytest.mark.parametrize("source,target", SOURCES.items())
def test_source_edits_reach_every_corresponding_copy(repository, source, target):
    original = (repository / source).read_bytes()
    if source == sync.SKILL_TEXT:
        # This legacy file is itself generated from the canonical prompt.
        source = sync.CANONICAL
        original = (repository / source).read_bytes()
        changed = original.replace(b"Admit unknowns.", b"Disclose unknowns.")
    else:
        changed = original + b"\nSource resource edit.\n"
    (repository / source).write_bytes(changed)
    assert target in sync.synchronize(repository, check=True)
    assert target in sync.synchronize(repository)
    assert sync.synchronize(repository, check=True) == []


def test_source_additions_deletions_and_obsolete_outputs_converge_without_recursion(repository):
    source = Path("skill/assets/new/nested.bin")
    target = PORTABLE / source.relative_to("skill")
    (repository / source).parent.mkdir(parents=True)
    (repository / source).write_bytes(b"\x00\xff\r\n")
    before = snapshot(repository)
    assert sync.synchronize(repository, check=True) == [target]
    assert snapshot(repository) == before
    assert sync.synchronize(repository) == [target]
    assert (repository / target).read_bytes() == b"\x00\xff\r\n"

    (repository / source).unlink()
    orphan = PORTABLE / "skills/baloney-detection-kit/orphan.md"
    (repository / orphan).parent.mkdir(parents=True)
    (repository / orphan).write_text("Do not collect the generated copy into itself.")
    outside = repository / "skills/another-skill/SKILL.md"
    outside.parent.mkdir(parents=True)
    outside.write_text("Unrelated skill must survive.")
    before = snapshot(repository)
    assert set(sync.synchronize(repository, check=True)) == {target, orphan}
    assert snapshot(repository) == before
    assert set(sync.synchronize(repository)) == {target, orphan}
    assert not (repository / PORTABLE / "assets").exists()
    assert not (repository / PORTABLE / "skills").exists()
    assert outside.read_text() == "Unrelated skill must survive."
    after = snapshot(repository)
    mtimes = {path: (repository / path).stat().st_mtime_ns for path in after}
    assert sync.synchronize(repository) == []
    assert sync.synchronize(repository, check=True) == []
    assert snapshot(repository) == after
    assert {path: (repository / path).stat().st_mtime_ns for path in after} == mtimes


@pytest.mark.parametrize("source", SUPPORT_FILES)
def test_missing_required_resource_fails_before_any_writes(repository, source):
    (repository / source).unlink()
    (repository / PORTABLE / "SKILL.md").write_text("stale copy")
    before = snapshot(repository)
    with pytest.raises(FileNotFoundError):
        sync.synchronize(repository)
    assert snapshot(repository) == before


def test_legacy_resource_collision_fails_before_writes(repository):
    (repository / "skill/LICENSE").write_text("Do not replace the distribution license.")
    before = snapshot(repository)
    with pytest.raises(ValueError, match="collides"):
        sync.synchronize(repository)
    assert snapshot(repository) == before


@pytest.mark.parametrize("parent", [Path("skill"), PORTABLE])
@pytest.mark.parametrize("directory", [False, True])
def test_symlinked_files_and_directories_fail_before_writes(repository, parent, directory):
    target = repository / ("prompts" if directory else "PLAYBOOK.md")
    link = repository / parent / "linked-resource"
    link.symlink_to(target, target_is_directory=directory)
    before = snapshot(repository)
    with pytest.raises(ValueError, match="symlink"):
        sync.synchronize(repository)
    assert snapshot(repository) == before
    assert link.is_symlink()


def test_plugin_manifest_uses_verified_minimal_schema_and_default_skill_layout():
    manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    # Verified subset of the official manifest schema; not a substitute for runtime validation.
    assert set(manifest) == {"name", "version", "description", "repository", "license"}
    assert all(isinstance(value, str) and value for value in manifest.values())
    assert manifest["name"] == "baloney-detection-kit"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", manifest["name"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert manifest["version"] == project["version"]
    assert manifest["repository"] == project["urls"]["Repository"]
    assert manifest["license"] == project["license"]
    assert (ROOT / "skills" / manifest["name"] / "SKILL.md").is_file()
    assert not (ROOT / ".claude-plugin/skills").exists()
    for implicit_component in (
        "commands",
        "agents",
        "hooks",
        ".mcp.json",
        ".lsp.json",
        "monitors",
    ):
        assert not (ROOT / implicit_component).exists()
