"""Synchronize intervention distributions without rewriting Markdown wrappers.

Only marked prompt regions in the English/Spanish root wrappers and English
skill/SKILL.md are generated. The English skill's plain text prompt and packaged
intervention mirrors are whole-file outputs. Diagnostic prompts are out of scope.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VERSION_MARKER = "<!-- bdk prompt-v2.0 -->"
START = "<!-- bdk:prompt:start -->"
END = "<!-- bdk:prompt:end -->"
CANONICAL = Path("prompts/intervention/prompt-full.md")
VARIANTS = ("compact", "full", "high-stakes", "agent", "reviewer", "second-opinion")
WRAPPERS = (Path("ROOT_PROMPT.md"), Path("skill/SKILL.md"))
SPANISH_CANONICAL = Path("prompts/intervention/es/prompt-full.md")
SPANISH_VARIANTS = ("compact", "full")
SPANISH_WRAPPERS = (Path("ROOT_PROMPT.es.md"),)
SKILL_TEXT = Path("skill/prompts/critical_investigation_mode.txt")
PACKAGED = Path("src/bdk/data/interventions")
ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    # Preserve newlines outside generated regions, including CRLF wrappers.
    return path.read_bytes().decode("utf-8")


def split_region(text: str, label: str) -> tuple[str, str, str]:
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError(f"{label}: expected exactly one prompt start/end marker")
    prefix, rest = text.split(START)
    if END not in rest:
        raise ValueError(f"{label}: prompt end marker precedes start")
    region, suffix = rest.split(END)
    return prefix + START, region, END + suffix


def check_version(text: str, label: str, *, skill: bool = False) -> None:
    lines = text.splitlines()
    if skill:
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            raise ValueError(f"{label}: expected YAML frontmatter first")
        lines = lines[lines.index("---", 1) + 1 :]
    if not lines or lines[0] != VERSION_MARKER or text.count("<!-- bdk prompt-") != 1:
        placement = "immediately after frontmatter" if skill else "on the first line"
        raise ValueError(f"{label}: expected one {VERSION_MARKER} {placement}")


def outputs(root: Path) -> dict[Path, str]:
    """Validate every source/wrapper before returning any generated writes."""
    generated = {}
    for canonical_path, variants, wrappers, packaged in (
        (CANONICAL, VARIANTS, WRAPPERS, PACKAGED),
        (SPANISH_CANONICAL, SPANISH_VARIANTS, SPANISH_WRAPPERS, PACKAGED / "es"),
    ):
        canonical = read_text(root / canonical_path)
        check_version(canonical, str(canonical_path))
        _, region, _ = split_region(canonical, str(canonical_path))
        block = re.fullmatch(r"\n```text\n(.+\n)```\n", region, flags=re.DOTALL)
        if block is None or "```" in block[1] or not block[1].strip():
            raise ValueError(f"{canonical_path}: expected one nonempty fenced text prompt")

        for wrapper in wrappers:
            text = read_text(root / wrapper)
            check_version(text, str(wrapper), skill=wrapper.name == "SKILL.md")
            prefix, _, suffix = split_region(text, str(wrapper))
            generated[wrapper] = prefix + region + suffix
        if canonical_path == CANONICAL:
            generated[SKILL_TEXT] = VERSION_MARKER + "\n" + block[1]

        for variant in variants:
            source = canonical_path.parent / f"prompt-{variant}.md"
            text = read_text(root / source)
            check_version(text, str(source))
            generated[packaged / source.name] = text
    return generated


def synchronize(root: Path, *, check: bool = False) -> list[Path]:
    generated = outputs(root)
    stale = [
        path
        for path, text in generated.items()
        if not (root / path).exists() or read_text(root / path) != text
    ]
    if not check:
        for path in stale:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(generated[path].encode("utf-8"))
    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without writing files")
    args = parser.parse_args(argv)
    try:
        stale = synchronize(ROOT, check=args.check)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Prompt synchronization failed: {exc}", file=sys.stderr)
        return 2
    if stale:
        print("Out-of-sync prompts:" if args.check else "Synchronized prompts:")
        for path in stale:
            print(f"  {path}")
        if args.check:
            print("Run python scripts/sync_prompts.py to regenerate.", file=sys.stderr)
            return 1
    else:
        print("Intervention prompts are synchronized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
