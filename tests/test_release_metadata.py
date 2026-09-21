"""Offline release alignment; metadata is not evidence of publication."""

import json
import re
import tomllib
from datetime import date
from pathlib import Path

import pytest
import yaml

from bdk import __version__

ROOT = Path(__file__).resolve().parents[1]
PROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
CITATION = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
PLUGIN = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
ZENODO = json.loads((ROOT / ".zenodo.json").read_text(encoding="utf-8"))
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "version",
    [__version__, CITATION["version"], PLUGIN["version"], ZENODO["version"]],
    ids=["package", "citation", "plugin", "zenodo"],
)
def test_distribution_versions_agree(version):
    assert version == PROJECT["version"]


def test_changelog_version_and_software_date_match_citation():
    releases = re.findall(r"^## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})$", CHANGELOG, re.M)
    assert releases, "A dated software release must follow Unreleased"
    version, released = releases[0]
    assert version == PROJECT["version"]
    assert released == str(CITATION["date-released"])
    assert date.fromisoformat(released).isoformat() == released
    assert CHANGELOG.index("## [Unreleased]") < CHANGELOG.index(f"## [{version}]")


def test_canonical_and_compatibility_entry_points_are_preserved():
    assert PROJECT["scripts"] == {"bdk": "bdk.cli:app", "robopsych": "bdk.cli:app"}


def test_release_guide_is_short_and_lists_all_alignment_locations():
    guide = (ROOT / "docs/RELEASING.md").read_text(encoding="utf-8")
    assert 0 < len(guide.splitlines()) <= 30
    for path in (
        "pyproject.toml",
        "src/bdk/__init__.py",
        "CITATION.cff",
        ".claude-plugin/plugin.json",
        ".zenodo.json",
        "CHANGELOG.md",
    ):
        assert f"`{path}`" in guide
