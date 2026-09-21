"""Offline nominal Cohen kappa. Synthetic claim counts are NOT paired ratings."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

DEFAULT = Path(__file__).parent / "calibration" / "reference_set" / "labels.json"


def kappa(left: dict[str, str], right: dict[str, str]) -> dict:
    shared = sorted(left.keys() & right.keys())
    n = len(shared)
    result = {
        "shared": n,
        "left_only": len(left.keys() - right.keys()),
        "right_only": len(right.keys() - left.keys()),
        "observed_agreement": None,
        "kappa": None,
        "status": "no shared rated items",
    }
    if not n:
        return result
    a = Counter(left[key] for key in shared)
    b = Counter(right[key] for key in shared)
    observed = sum(left[key] == right[key] for key in shared) / n
    expected_numerator = sum(a[label] * b[label] for label in a.keys() | b.keys())
    result["observed_agreement"] = observed
    if expected_numerator == n * n:
        result["status"] = "undefined: chance agreement is 1"
    else:
        expected = expected_numerator / (n * n)
        result["kappa"] = (observed - expected) / (1 - expected)
        result["status"] = "defined"
    return result


def agreement_report(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    if "raters" not in data:
        cases = data.get("cases")
        if (
            isinstance(cases, list)
            and cases
            and all(
                isinstance(c, dict)
                and c.get("source") == "synthetic-boundary-v1"
                and "features" in c
                for c in cases
            )
        ):
            return {
                "status": "unavailable",
                "note": f"{len(cases)} synthetic claim-count fixtures; no human or judge ratings.",
                "pairs": [],
            }
        raise ValueError("missing raters; expected a ratings file, not unpaired labels")
    if data.get("schema_version") != 1 or data.get("data_kind") not in ("empirical", "synthetic"):
        raise ValueError("schema_version=1 and data_kind=empirical|synthetic are required")
    labels = data.get("labels")
    if (
        not isinstance(labels, list)
        or not labels
        or any(not isinstance(label, str) or not label.strip() for label in labels)
        or len(set(labels)) != len(labels)
    ):
        raise ValueError("labels must be a nonempty list of unique nonempty strings")
    raters = data["raters"]
    if not isinstance(raters, list):
        raise ValueError("raters must be a list")
    parsed = {}
    for rater in raters:
        if not isinstance(rater, dict):
            raise ValueError("rater must be an object")
        name = rater.get("id")
        if not isinstance(name, str) or not name.strip() or name in parsed:
            raise ValueError("rater IDs must be nonempty and unique")
        role = rater.get("role")
        if role not in ("judge", "human"):
            raise ValueError("rater role must be judge or human")
        if role == "judge" and any(
            not isinstance(rater.get(key), str) or not rater[key].strip()
            for key in ("model", "family")
        ):
            raise ValueError("judge model and family are required (family is not hosting provider)")
        rows = rater.get("ratings")
        if not isinstance(rows, list):
            raise ValueError("ratings must be a list")
        ratings, seen = {}, set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("rating must be an object")
            item = row.get("item_id")
            if not isinstance(item, str) or not item.strip() or item in seen:
                raise ValueError("item IDs must be nonempty and unique within each rater")
            seen.add(item)
            if "label" not in row:
                raise ValueError("rating requires label; use null for explicitly missing ratings")
            label = row["label"]
            if label is not None:
                if not isinstance(label, str) or label not in labels:
                    raise ValueError("invalid rating label")
                ratings[item] = label
        parsed[name] = (role, ratings)
    pairs = []
    for left, right in combinations(parsed, 2):
        lrole, lratings = parsed[left]
        rrole, rratings = parsed[right]
        if "judge" not in (lrole, rrole):
            continue
        pairs.append(
            {
                "pair": f"{left} / {right}",
                "kind": "judge-judge" if lrole == rrole else "judge-human",
                **kappa(lratings, rratings),
            }
        )
    return {
        "status": "available" if pairs else "unavailable",
        "note": (
            f"{data['data_kind']} input; kappa is agreement, not accuracy or independent evidence."
        ),
        "pairs": pairs,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ratings", type=Path, default=DEFAULT)
    args = parser.parse_args(argv)
    try:
        report = agreement_report(json.loads(args.ratings.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        # Do not echo arbitrary input or exception bodies from private ratings.
        print(
            f"Invalid/unreadable ratings ({type(exc).__name__}); check documented schema.",
            file=sys.stderr,
        )
        return 1
    print(report["note"])
    print("| Pair | Kind | Shared | Left only | Right only | Agreement | Kappa | Status |")
    print("|---|---|---:|---:|---:|---:|---:|---|")
    for row in report["pairs"]:
        agreement = row["observed_agreement"]
        value = row["kappa"]
        print(
            f"| {row['pair']} | {row['kind']} | {row['shared']} | {row['left_only']} | "
            f"{row['right_only']} | {agreement if agreement is not None else 'N/A'} | "
            f"{value if value is not None else 'N/A'} | {row['status']} |"
        )
    for kind in ("judge-human", "judge-judge"):
        if not any(pair["kind"] == kind for pair in report["pairs"]):
            print(f"| N/A | {kind} | N/A | N/A | N/A | N/A | N/A | paired ratings unavailable |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
