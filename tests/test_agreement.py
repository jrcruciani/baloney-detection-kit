"""Synthetic mathematical fixtures, not empirical judge/human calibration."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

PATH = Path(__file__).parents[1] / "validation" / "diagnosis" / "agreement.py"
spec = importlib.util.spec_from_file_location("agreement", PATH)
assert spec and spec.loader
agreement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agreement)


def ratings():
    return {
        "schema_version": 1,
        "data_kind": "synthetic",
        "labels": ["yes", "no"],
        "raters": [
            {
                "id": name,
                "role": role,
                "model": "synthetic-judge",
                "family": family,
                "ratings": [{"item_id": str(i), "label": label} for i, label in enumerate(labels)],
            }
            for name, role, family, labels in [
                ("j1", "judge", "synthetic-A", ["yes", "yes", "no", "no"]),
                ("human-fixture", "human", "", ["yes", "no", "yes", "no"]),
                ("j2", "judge", "synthetic-B", ["yes", "yes", "no", "no"]),
            ]
        ],
    }


def test_known_kappa():
    pairs = agreement.agreement_report(ratings())["pairs"]
    assert [row["kappa"] for row in pairs] == [0, 1, 0]
    assert [row["kind"] for row in pairs] == ["judge-human", "judge-judge", "judge-human"]
    assert all(row["shared"] == 4 for row in pairs)
    assert agreement.kappa({"1": "a", "2": "b"}, {"1": "b", "2": "a"})["kappa"] == -1
    # 7/8 observed agreement, 1/2 chance agreement => 3/4 kappa.
    a = dict(enumerate("aaaabbbb"))
    b = dict(enumerate("aaaaabbb"))
    assert agreement.kappa(a, b)["kappa"] == 0.75


def test_missing_and_differing_items():
    data = ratings()
    data["raters"][0]["ratings"][0]["label"] = None
    data["raters"][1]["ratings"].append({"item_id": "extra", "label": "yes"})
    row = agreement.agreement_report(data)["pairs"][0]
    assert row["shared"] == 3 and row["right_only"] == 2 and row["left_only"] == 0
    assert row["kappa"] == pytest.approx(-0.5)


@pytest.mark.parametrize(
    "left,right,status",
    [
        ({}, {}, "no shared"),
        ({"a": "yes"}, {"b": "yes"}, "no shared"),
        ({"a": "yes"}, {"a": "yes"}, "chance agreement"),
    ],
)
def test_undefined(left, right, status):
    row = agreement.kappa(left, right)
    assert row["kappa"] is None
    assert status in row["status"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["raters"].append(copy.deepcopy(d["raters"][0])),
        lambda d: d["raters"][0]["ratings"].append({"item_id": "0", "label": None}),
        lambda d: d["raters"][0]["ratings"][0].update(label="maybe"),
        lambda d: d["raters"][0]["ratings"][0].update(label=[]),
        lambda d: d["raters"][0]["ratings"][0].pop("label"),
        lambda d: d["raters"][0]["ratings"][0].update(item_id=""),
        lambda d: d["raters"][0].update(role="synthetic-pretending-human"),
        lambda d: d["raters"][0].pop("family"),
        lambda d: d.update(labels=["yes", "yes"]),
        lambda d: d.update(data_kind=""),
        lambda d: d.update(raters={}),
    ],
)
def test_invalid_ratings(mutate):
    data = ratings()
    mutate(data)
    with pytest.raises(ValueError):
        agreement.agreement_report(data)


def test_default_is_honest_and_offline(capsys):
    assert agreement.main([]) == 0
    output = capsys.readouterr().out
    assert "24 synthetic claim-count fixtures" in output
    assert "no human or judge ratings" in output
    assert output.count("paired ratings unavailable") == 2


def test_empty_ratings_are_not_agreement():
    data = ratings()
    for rater in data["raters"]:
        rater["ratings"] = []
    assert all(row["kappa"] is None for row in agreement.agreement_report(data)["pairs"])


def test_real_input_schema_and_cli_failure(tmp_path, capsys):
    path = tmp_path / "synthetic-ratings.json"
    path.write_text(json.dumps(ratings()))
    assert agreement.main(["--ratings", str(path)]) == 0
    assert "synthetic input" in capsys.readouterr().out
    path.write_text("{broken")
    assert agreement.main(["--ratings", str(path)]) == 1
    assert "Invalid/unreadable" in capsys.readouterr().err
