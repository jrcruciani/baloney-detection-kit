"""Tests for coherence weight calibration artifacts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "validation" / "calibration" / "weight_sensitivity.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("weight_sensitivity", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_reference_set_has_expected_shape():
    module = _load_module()
    cases = module.load_reference_set()
    labels = {case.label for case in cases}
    assert len(cases) >= 20
    assert labels == {"genuine", "mixed", "performed"}
    assert all(case.claims for case in cases)


def test_sensitivity_report_shape(tmp_path):
    module = _load_module()
    report = module.analyze_sensitivity(module.load_reference_set())
    assert report["case_count"] >= 20
    assert report["baseline"]["accuracy"] == 1.0
    assert report["summary"]["max_classification_flip_rate"] >= 0.0

    output = tmp_path / "sensitivity.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    written = json.loads(output.read_text(encoding="utf-8"))
    assert written["variations"]
    assert {"classification_flip_rate", "max_score_delta"} <= set(written["variations"][0])
