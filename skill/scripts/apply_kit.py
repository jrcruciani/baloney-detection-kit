#!/usr/bin/env python3
"""
apply_kit.py — Apply the Baloney Detection Kit programmatically.

Usage:
  python apply_kit.py "I think I just discovered that language structures knowledge"
  python apply_kit.py --interactive
  echo "my claim" | python apply_kit.py --stdin

This script does NOT call any LLM by itself. It builds the prompt that you
should feed into the LLM of your choice (OpenAI, Anthropic, local, etc.).

The point: the script makes it trivial to wrap any user input with the
6-step protocol so the LLM cannot easily skip to validation.
"""

import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = SKILL_DIR / "prompts" / "critical_investigation_mode.txt"


def load_system_prompt() -> str:
    if not PROMPT_FILE.exists():
        sys.stderr.write(f"ERROR: prompt file not found at {PROMPT_FILE}\n")
        sys.exit(1)
    return PROMPT_FILE.read_text(encoding="utf-8")


def build_payload(claim: str) -> dict:
    system = load_system_prompt()
    return {
        "system": system,
        "user": (
            "Apply the Baloney Detection Kit 6-step protocol to the following "
            "claim. Do not skip steps. Do not flatter. Be honest, kind, and "
            "specific. Cite sources when possible.\n\n"
            f"CLAIM: {claim}"
        ),
    }


def render_text(payload: dict) -> str:
    return (
        "===== SYSTEM PROMPT =====\n"
        f"{payload['system']}\n\n"
        "===== USER PROMPT =====\n"
        f"{payload['user']}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Wrap a claim in the Baloney Detection Kit prompt."
    )
    parser.add_argument(
        "claim",
        nargs="?",
        help="The claim to evaluate. If omitted, use --stdin or --interactive.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read the claim from stdin.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for the claim interactively.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text).",
    )
    args = parser.parse_args()

    if args.stdin:
        claim = sys.stdin.read().strip()
    elif args.interactive:
        sys.stderr.write("Enter your claim (single line, ENTER to submit):\n> ")
        sys.stderr.flush()
        claim = sys.stdin.readline().strip()
    elif args.claim:
        claim = args.claim.strip()
    else:
        parser.print_help()
        return 1

    if not claim:
        sys.stderr.write("ERROR: empty claim.\n")
        return 1

    payload = build_payload(claim)

    if args.format == "json":
        import json
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(payload))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
