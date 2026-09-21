import os
from pathlib import Path

import yaml


def test_skill_frontmatter():
    root = Path(__file__).resolve().parents[1]
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
            if name not in excluded_dirs
            and not (Path(directory) / name / "pyvenv.cfg").is_file()
        )
        if "SKILL.md" in files:
            skill_paths.append(Path(directory) / "SKILL.md")

    assert skill_paths, "No repository SKILL.md files found"
    for path in skill_paths:
        relative_path = path.relative_to(root)
        lines = path.read_text(encoding="utf-8").splitlines()
        assert lines and lines[0] == "---", (
            f"{relative_path}: missing opening frontmatter delimiter"
        )
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
