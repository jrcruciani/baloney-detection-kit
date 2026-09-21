"""Synchronize intervention distributions without rewriting Markdown wrappers.

Only marked prompt regions in the English/Spanish root wrappers and English
skill/SKILL.md are generated. The English skill's plain text prompt and packaged
intervention mirrors are whole-file outputs. The portable skills/ distribution
copies the legacy skill and explicit local resources with rebased paths.
Diagnostic prompts are out of scope.
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
LEGACY_SKILL = Path("skill")
PORTABLE_SKILL = Path("skills/baloney-detection-kit")
REPOSITORY_URL = "https://github.com/jrcruciani/baloney-detection-kit/blob/main"
SKILL_RESOURCES = {
    Path("PLAYBOOK.md"): Path("resources/PLAYBOOK.md"),
    CANONICAL: Path("resources/prompts/intervention/prompt-full.md"),
    Path("docs/second-opinion-operational.md"): Path(
        "resources/docs/second-opinion-operational.md"
    ),
    Path("LICENSE"): Path("LICENSE"),
    Path("NOTICE"): Path("NOTICE"),
}
# Only distribution paths change; the prompt block and frontmatter are untouched.
PORTABLE_REPLACEMENTS = {
    Path("skill/SKILL.md"): {
        "../PLAYBOOK.md": "resources/PLAYBOOK.md",
        "../prompts/intervention/prompt-full.md": "resources/prompts/intervention/prompt-full.md",
        "`scripts/sync_prompts.py`": (
            f"[`scripts/sync_prompts.py`]({REPOSITORY_URL}/scripts/sync_prompts.py)"
        ),
    },
    Path("skill/checklist/review_rubric.md"): {
        "../../docs/second-opinion-operational.md": (
            "../resources/docs/second-opinion-operational.md"
        ),
    },
    Path("PLAYBOOK.md"): {
        "(README.md#scope-and-boundaries)": f"({REPOSITORY_URL}/README.md#scope-and-boundaries)",
        "(docs/related-work.md)": f"({REPOSITORY_URL}/docs/related-work.md)",
        "skill/checklist/review_rubric.md": "../checklist/review_rubric.md",
    },
    Path("docs/second-opinion-operational.md"): {
        "../skill/checklist/review_rubric.md": "../../checklist/review_rubric.md",
        "(../README.md#scope-and-boundaries)": f"({REPOSITORY_URL}/README.md#scope-and-boundaries)",
    },
}
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


def file_inventory(directory: Path) -> list[Path]:
    """Collect one bounded tree, rejecting symlinks rather than following them."""
    if directory.is_symlink():
        raise ValueError(f"{directory}: symlinks are not supported in skill distributions")
    files = []
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"{path}: symlinks are not supported in skill distributions")
        if path.is_file():
            files.append(path)
    return files


def portable_sources(root: Path) -> dict[Path, Path]:
    """Map sources explicitly; never scan the repository or generated skills/."""
    sources = {
        path.relative_to(root): PORTABLE_SKILL / path.relative_to(root / LEGACY_SKILL)
        for path in file_inventory(root / LEGACY_SKILL)
    }
    sources[SKILL_TEXT] = PORTABLE_SKILL / SKILL_TEXT.relative_to(LEGACY_SKILL)
    for source, relative_target in SKILL_RESOURCES.items():
        for path in (source, *source.parents):
            if (root / path).is_symlink():
                raise ValueError(f"{source}: symlinks are not supported in skill resources")
        target = PORTABLE_SKILL / relative_target
        if target in sources.values():
            raise ValueError(f"{source}: portable resource collides with legacy skill: {target}")
        sources[source] = target
    return sources


def outputs(root: Path) -> dict[Path, bytes]:
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
    encoded = {path: text.encode("utf-8") for path, text in generated.items()}
    for source, target in portable_sources(root).items():
        # Use this run's generated prompt, not a stale legacy file on disk.
        content = encoded[source] if source in encoded else (root / source).read_bytes()
        for old, new in PORTABLE_REPLACEMENTS.get(source, {}).items():
            content = content.replace(old.encode("utf-8"), new.encode("utf-8"))
        encoded[target] = content
    return encoded


def synchronize(root: Path, *, check: bool = False) -> list[Path]:
    generated = outputs(root)
    if (root / PORTABLE_SKILL.parent).is_symlink():
        raise ValueError(f"{PORTABLE_SKILL.parent}: symlinked output directory is not supported")
    obsolete = sorted(
        path.relative_to(root)
        for path in file_inventory(root / PORTABLE_SKILL)
        if path.relative_to(root) not in generated
    )
    stale = [
        path
        for path, content in generated.items()
        if not (root / path).exists() or (root / path).read_bytes() != content
    ]
    if not check:
        for path in stale:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(generated[path])
        for path in obsolete:
            target = root / path
            target.unlink()
            parent = target.parent
            while parent != root / PORTABLE_SKILL and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
    return stale + obsolete


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
