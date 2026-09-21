"""Offline Markdown path checks use temporary repositories, never the network."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _ROOT / "scripts" / "check_markdown_links.py"
_SPEC = importlib.util.spec_from_file_location("check_markdown_links", _SCRIPT)
assert _SPEC and _SPEC.loader
links = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(links)


@pytest.fixture
def repository(tmp_path):
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    (tmp_path / "docs").mkdir()
    for filename in (
        "target.md",
        "space name.md",
        "paren(nested).md",
        "hash#query?.md",
        "image.png",
        "bracket[label](version).md",
        "tick`(special)`.md",
    ):
        (tmp_path / filename).touch()
    return tmp_path


@pytest.mark.parametrize(
    "markdown",
    [
        "[file](../target.md)",
        "[directory](../docs/)",
        "[fragment](../target.md#heading)",
        "[query](../target.md?raw=1#heading)",
        "[encoded](../space%20name.md)",
        "[encoded punctuation](../hash%23query%3F.md?raw=1#heading)",
        "[angle](<../space name.md>)",
        '[title](../target.md "A title")',
        '[title](../target.md "Example [not a link](missing.md)")',
        '[ref]: ../target.md "Example [not a link](missing.md)"\n\n[ref]',
        "[title](../target.md 'A title')",
        "[title](../target.md (A title))",
        "[nested [label]](../paren(nested).md)",
        "[brackets](../bracket[label](version).md)",
        "[backticks](../tick`(special)`.md)",
        r"[escaped](../paren\(nested\).md)",
        "![image](../image.png)",
        "[![image](../image.png)](../target.md)",
        "[full][id]\n\n[id]: ../target.md",
        "[collapsed][]\n\n[collapsed]: <../space name.md> 'Title'",
        "[shortcut]\n\n[shortcut]:\n  ../target.md",
        "![image][id]\n\n[id]: ../image.png",
        "[anchor](#heading) [query](?raw=1) [empty]()",
        "[root](/target.md)",
        "[html](../target.md?first=1&amp;second=2)",
        '<a href="../target.md#heading">file</a><img src="../image.png" />',
        "[remote](https://example.invalid/missing.md) ![remote](//example.invalid/image.png)",
        "[mail](mailto:person@example.invalid) [scheme](custom:missing)",
    ],
)
def test_valid_paths(repository, markdown):
    source = repository / "docs" / "source.md"
    source.write_text(markdown, encoding="utf-8")
    assert links.check_markdown(source, repository) == []


@pytest.mark.parametrize(
    "markdown, destination",
    [
        ("[file](missing.md)", "missing.md"),
        ("[directory](missing/)", "missing/"),
        ("[image](../image.png/)", "../image.png/"),
        ("![image](missing.png)", "missing.png"),
        ("[![image](missing.png)](../target.md)", "missing.png"),
        ("[![image](../image.png)](missing.md)", "missing.md"),
        ("[reference][id]\n\n[id]: missing.md", "missing.md"),
        ("[reference][]\n\n[reference]: missing.md", "missing.md"),
        ("[reference]\n\n[reference]: missing.md", "missing.md"),
        ("![image][id]\n\n[id]: missing.png", "missing.png"),
        ("[reference][id]\n\n[id]:\n  <missing name.md>", "missing name.md"),
        ("[missing](missing%20name.md?raw=1#heading)", "missing%20name.md?raw=1#heading"),
        ("[outside](../../outside.md)", "../../outside.md"),
        ("[nested](missing(nested).md)", "missing(nested).md"),
        ("[`code label`](missing.md)", "missing.md"),
        ('<a href="missing.md">file</a>', "missing.md"),
        ('<img src="missing.png">', "missing.png"),
        ("- item\n\n    [list continuation](missing.md)", "missing.md"),
        ("> [quoted](missing.md)", "missing.md"),
        (r"\` [real](missing.md) \`", "missing.md"),
        ("\\```\n[real](missing.md)\n\\```", "missing.md"),
        ("- item\n\n    [ref]: missing.md\n\n    [ref]", "missing.md"),
        ("> ```\n> [example](not-a-link.md)\n\n[real](missing.md)", "missing.md"),
        ("`` unmatched [real](missing.md) `", "missing.md"),
    ],
)
def test_broken_paths(repository, markdown, destination):
    source = repository / "docs" / "source.md"
    source.write_text(markdown, encoding="utf-8")
    errors = links.check_markdown(source, repository)
    assert len(errors) == 1
    assert destination in errors[0]
    assert errors[0].startswith("docs/source.md:")


@pytest.mark.parametrize(
    "literal",
    [
        "`[example](missing.md)`",
        "``[example](missing.md) with ` a backtick``",
        "`![image](missing.png)`",
        "`\n[ref]: missing.md\n`",
        '`<img src="missing.png">`',
        "```markdown\n[example](missing.md)\n```",
        "~~~markdown\n![example](missing.png)\n~~~",
        "````markdown\n```\n[example](missing.md)\n```\n````",
        "```markdown\n[id]: missing.md\n```",
        "```markdown\n[example](missing.md)",
        "> ```markdown\n> [example](missing.md)\n> ```",
        "- ```markdown\n  [example](missing.md)\n  ```",
        "    [example](missing.md)\n    ![image](missing.png)",
        "\t[example](missing.md)",
        "<!-- [example](missing.md) -->",
        "<pre>\n[example](missing.md)\n</pre>",
        r"\[escaped](missing.md)",
    ],
)
def test_literal_examples_are_not_links(repository, literal):
    source = repository / "docs" / "source.md"
    source.write_text(literal + "\n\n[real](../target.md)", encoding="utf-8")
    assert links.check_markdown(source, repository) == []
    source.write_text(literal + "\n\n[real](missing-real.md)", encoding="utf-8")
    if literal.startswith("```markdown") and not literal.endswith("```"):
        assert links.check_markdown(source, repository) == []
    else:
        errors = links.check_markdown(source, repository)
        assert len(errors) == 1
        assert "missing-real.md" in errors[0]


def test_diagnostics_preserve_line_numbers(repository):
    source = repository / "docs" / "source.md"
    source.write_text("```\n[example](missing.md)\n```\n\n[real](missing.md)\n", encoding="utf-8")
    assert links.check_markdown(source, repository) == [
        "docs/source.md:5: missing.md: missing file or directory"
    ]


def test_git_inventory_covers_new_and_tracked_docs_without_tool_caches(repository):
    (repository / ".gitignore").write_text("ignored/\n", encoding="utf-8")
    paths = (
        "new/deep/guide.md",
        ".github/guide.MD",
        "more/guide.markdown",
        ".venv/ignored.md",
        ".venv-base/ignored.md",
        "venv/ignored.md",
        ".cache/ignored.md",
        ".mypy_cache/ignored.md",
        "nested/site-packages/ignored.md",
        ".git/ignored.md",
        "ignored/ignored.md",
    )
    for name in paths:
        path = repository / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[bad](missing.md)", encoding="utf-8")
    subprocess.run(
        ["git", "add", "-f", ".cache/ignored.md", "ignored/ignored.md"], cwd=repository, check=True
    )
    found = {path.relative_to(repository).as_posix() for path in links.markdown_files(repository)}
    assert found == {
        "target.md",
        "space name.md",
        "paren(nested).md",
        "hash#query?.md",
        "bracket[label](version).md",
        "tick`(special)`.md",
        "new/deep/guide.md",
        ".github/guide.MD",
        "more/guide.markdown",
        ".cache/ignored.md",
        "ignored/ignored.md",
    }
    assert links.markdown_files(repository) == sorted(links.markdown_files(repository))


def test_cli_fails_on_new_broken_doc_then_passes_after_repair(repository):
    source = repository / "docs" / "new.md"
    source.write_text("[bad](missing.md)", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(repository)], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "docs/new.md:1: missing.md" in result.stderr
    source.write_text("[good](../target.md)", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(repository)], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "all relative link paths exist" in result.stdout


def test_cli_reports_non_repository_error(tmp_path):
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(tmp_path)], capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "Markdown link check failed" in result.stderr


def test_repository_markdown_links():
    files = links.markdown_files(_ROOT)
    assert {
        _ROOT / "SECURITY.md",
        _ROOT / "CONTRIBUTING.md",
        _ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
    } <= set(files)
    errors = [error for source in files for error in links.check_markdown(source, _ROOT)]
    assert not errors, "\n".join(errors)
