import os
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
LEGACY_NAMES = {Path("skill/SKILL.md"): "baloney-detection-kit"}


def validate_frontmatter(text, relative_path):
    lines = text.splitlines()
    assert lines and lines[0] == "---", f"{relative_path}: missing opening frontmatter delimiter"
    end = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
    assert end is not None, f"{relative_path}: missing closing frontmatter delimiter"
    metadata = yaml.safe_load("\n".join(lines[1:end]))
    assert isinstance(metadata, dict), f"{relative_path}: frontmatter must be a mapping"
    for field in ("name", "description"):
        value = metadata.get(field)
        assert isinstance(value, str) and value.strip(), (
            f"{relative_path}: {field} must be a nonempty string"
        )
    assert len(metadata["description"]) <= 1024, (
        f"{relative_path}: description must be at most 1024 characters"
    )
    assert len(metadata["name"]) <= 64, f"{relative_path}: name must be at most 64 characters"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"]), relative_path
    expected = LEGACY_NAMES.get(relative_path, relative_path.parent.name)
    assert metadata["name"] == expected, (
        f"{relative_path}: expected name {expected!r}; "
        "see docs/architecture.md for legacy exception"
    )


def test_skill_frontmatter():
    root = ROOT
    excluded_dirs = {
        ".git",
        ".nox",
        ".tox",
        ".venv",
        "__pycache__",
        "env",
        "node_modules",
        "site-packages",
        "vendor",
        "venv",
    }
    skill_paths = []
    for directory, subdirs, files in os.walk(root):
        subdirs[:] = sorted(
            name
            for name in subdirs
            if name not in excluded_dirs and not (Path(directory) / name / "pyvenv.cfg").is_file()
        )
        if "SKILL.md" in files:
            skill_paths.append(Path(directory) / "SKILL.md")

    assert skill_paths, "No repository SKILL.md files found"
    assert root / "skill/SKILL.md" in skill_paths
    assert root / "skills/baloney-detection-kit/SKILL.md" in skill_paths
    for path in skill_paths:
        validate_frontmatter(path.read_text(encoding="utf-8"), path.relative_to(root))


@pytest.mark.parametrize("relative", ["skills/baloney-detection-kit/SKILL.md", "skill/SKILL.md"])
@pytest.mark.parametrize(
    "metadata",
    [
        "name: [broken",
        "- not-a-mapping",
        "name: baloney-detection-kit\ndescription: 123",
        "name: baloney-detection-kit\ndescription: ''",
        "name: baloney-detection-kit\ndescription: " + "x" * 1025,
        "name: " + "x" * 65 + "\ndescription: test",
        "name: bad--name\ndescription: test",
        "name: different-name\ndescription: test",
    ],
)
def test_invalid_metadata_is_rejected_for_both_entry_points(relative, metadata):
    with pytest.raises((AssertionError, yaml.YAMLError)):
        validate_frontmatter(f"---\n{metadata}\n---\nBody\n", Path(relative))


def test_directory_matching_has_only_the_documented_legacy_exception():
    text = "---\nname: baloney-detection-kit\ndescription: " + "x" * 1024 + "\n---\n"
    validate_frontmatter(text, Path("skill/SKILL.md"))
    validate_frontmatter(text, Path("skills/baloney-detection-kit/SKILL.md"))
    for relative in ("another/SKILL.md", "skills/skill/SKILL.md"):
        with pytest.raises(AssertionError, match="expected name"):
            validate_frontmatter(text, Path(relative))
