"""Check repository Markdown file/directory links offline, using only the stdlib.

Git supplies tracked and non-ignored untracked files; tooling exclusions apply
only to untracked files, never to committed documentation. Fragments and queries
are allowed but not validated. Remote URLs and literal code are not checked.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

_UNTRACKED_TOOL_DIRS = (
    ".venv",
    ".venv-*",
    "venv",
    ".tox",
    ".nox",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    "site-packages",
    "node_modules",
)


def markdown_files(root: Path) -> list[Path]:
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
            *(f"--exclude={name}/" for name in _UNTRACKED_TOOL_DIRS),
        ],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return sorted(
        {
            root / os.fsdecode(name)
            for name in result.stdout.split(b"\0")
            if name
            and Path(os.fsdecode(name)).suffix.lower() in {".md", ".markdown"}
            and (root / os.fsdecode(name)).exists()
        }
    )


def _blank(text: str) -> str:
    return re.sub(r"[^\n]", " ", text)


def _without_code_blocks(text: str) -> str:
    lines = []
    fence: tuple[str, int, int] | None = None
    list_indents: list[int] = []
    indented_code = False
    previous_blank = True
    for line in text.splitlines(keepends=True):
        quote = re.match(r"^(?: {0,3}>[ \t]?)*", line)
        assert quote is not None
        quote_depth = quote[0].count(">")
        body = line[quote.end() :].expandtabs(4)
        if fence and quote_depth < fence[2]:
            fence = None
        indent = len(body) - len(body.lstrip(" "))
        item = re.match(r" *([-+*]|\d+[.)]) +", body)
        if body.strip():
            while list_indents and indent < list_indents[-1]:
                list_indents.pop()
            if item:
                list_indents.append(item.end())
        content = body[item.end() :] if item else body.lstrip(" ")
        marker = re.match(r"(`{3,}|~{3,})(.*)", content)
        if fence:
            lines.append(_blank(line))
            if (
                marker
                and marker[1][0] == fence[0]
                and len(marker[1]) >= fence[1]
                and not marker[2].strip()
            ):
                fence = None
            previous_blank = True
            continue
        code_indent = (list_indents[-1] if list_indents else 0) + 4
        if not item and indent >= code_indent and (previous_blank or indented_code):
            lines.append(_blank(line))
            indented_code = True
        elif marker and (marker[1][0] != "`" or "`" not in marker[2]):
            fence = (marker[1][0], len(marker[1]), quote_depth)
            lines.append(_blank(line))
            indented_code = False
        else:
            lines.append(line)
            if body.strip():
                indented_code = False
        previous_blank = not body.strip()
    text = "".join(lines)
    text = re.sub(r"<!--.*?(?:-->|$)", lambda match: _blank(match[0]), text, flags=re.S)
    return re.sub(
        r"<(pre|script|style)\b[^>]*>.*?(?:</\1\s*>|$)",
        lambda match: _blank(match[0]),
        text,
        flags=re.S | re.I,
    )


def _escaped(text: str, index: int) -> bool:
    start = index
    while start > 0 and text[start - 1] == "\\":
        start -= 1
    return (index - start) % 2 == 1


def _code_span_end(text: str, start: int) -> int:
    runs = re.finditer(r"`+", text[start:])
    opening = next(runs)
    for closing in runs:
        if len(closing[0]) == len(opening[0]):
            return start + closing.end()
    return start + opening.end()


def _closing(text: str, start: int, opening: str, closing: str) -> int | None:
    depth = 0
    index = start
    while index < len(text):
        if _escaped(text, index):
            index += 1
            continue
        if opening == "[" and text[index] == "`":
            index = _code_span_end(text, index)
            continue
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def _destination(text: str, start: int) -> tuple[str, int] | None:
    while start < len(text) and text[start].isspace():
        start += 1
    if start == len(text):
        return None
    if text[start] == "<":
        end = start + 1
        while end < len(text) and text[end] != "\n":
            if text[end] == ">" and not _escaped(text, end):
                return text[start + 1 : end], end + 1
            end += 1
        return None
    end, depth = start, 0
    while end < len(text):
        char = text[end]
        if not _escaped(text, end):
            if char.isspace() or (char == ")" and depth == 0):
                break
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
        end += 1
    return (text[start:end], end) if depth == 0 else None


def _title_end(text: str, start: int) -> int | None:
    original = start
    while start < len(text) and text[start].isspace():
        start += 1
    if start < len(text) and text[start] in "\"'(":
        quote = text[start]
        if quote == "(":
            end = _closing(text, start, "(", ")")
        else:
            end = start + 1
            while end < len(text) and (text[end] != quote or _escaped(text, end)):
                end += 1
        if end is None:
            return None
        return end + 1 if end < len(text) else None
    return original


def _inline_end(text: str, start: int) -> int | None:
    end = _title_end(text, start)
    if end is None:
        return None
    while end < len(text) and text[end].isspace():
        end += 1
    return end if end < len(text) and text[end] == ")" else None


def _decode_destination(raw: str) -> str:
    return html.unescape(re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", raw))


class _HTMLLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if value is not None and key in {"href", "src", "poster"}:
                self.links.append((self.getpos()[0], value))


def destinations(text: str) -> list[tuple[int, str]]:
    text = _without_code_blocks(text)
    links = []
    skipped: dict[int, int] = {}
    definitions: dict[int, tuple[int, str]] = {}
    # Checking definitions covers full, collapsed, shortcut, and image references,
    # including unused definitions, without treating ordinary [brackets] as links.
    for match in re.finditer(
        r"(?m)^(?: {0,3}>[ \t]?)* *(?:(?:[-+*]|\d+[.)]) +)?"
        r"\[(?:\\.|[^\]\\\n])+\]:[ \t]*(?:\n[ \t]*)?",
        text,
    ):
        destination = _destination(text, match.end())
        if destination:
            end = _title_end(text, destination[1])
            if end is None or text[end:].split("\n", 1)[0].strip():
                continue
            definitions[match.start()] = (end, _decode_destination(destination[0]))
    index = 0
    while index < len(text):
        if index in skipped:
            index = skipped[index]
            continue
        if index in definitions:
            end, target = definitions[index]
            links.append((text.count("\n", 0, index) + 1, target))
            skipped[index] = end
            index = end
            continue
        if _escaped(text, index):
            index += 1
            continue
        if text[index] == "`":
            end = _code_span_end(text, index)
            skipped[index] = end
            index = end
            continue
        if text[index] == "[":
            end = _closing(text, index, "[", "]")
            if end is not None and text[end + 1 : end + 2] == "(":
                destination = _destination(text, end + 2)
                finish = _inline_end(text, destination[1]) if destination else None
                if destination is not None and finish is not None:
                    links.append(
                        (text.count("\n", 0, index) + 1, _decode_destination(destination[0]))
                    )
                    skipped[end + 1] = finish + 1
        index += 1
    html_text = list(text)
    for start, end in skipped.items():
        html_text[start:end] = _blank(text[start:end])
    parser = _HTMLLinks()
    parser.feed("".join(html_text))
    links.extend(parser.links)
    return sorted(set(links))


def path_problem(destination: str, source: Path, root: Path) -> str | None:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", destination) or destination.startswith("//"):
        return None
    path = unquote(urlsplit(destination).path)
    if not path:
        return None
    target = (root / path.lstrip("/") if path.startswith("/") else source.parent / path).resolve()
    if not target.is_relative_to(root):
        return "path escapes the repository"
    if not target.exists():
        return "missing file or directory"
    if path.endswith("/") and not target.is_dir():
        return "expected a directory"
    return None


def check_markdown(source: Path, root: Path) -> list[str]:
    errors = []
    for line, destination in destinations(source.read_text(encoding="utf-8")):
        problem = path_problem(destination, source, root)
        if problem:
            errors.append(f"{source.relative_to(root)}:{line}: {destination}: {problem}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root.resolve()
    try:
        files = markdown_files(root)
        errors = [error for source in files for error in check_markdown(source, root)]
    except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Markdown link check failed: {error}", file=sys.stderr)
        return 2
    if errors:
        print("\n".join(errors), file=sys.stderr)
        print(f"Found {len(errors)} broken relative link(s) in {len(files)} Markdown files.")
        return 1
    print(f"Checked {len(files)} Markdown files: all relative link paths exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
