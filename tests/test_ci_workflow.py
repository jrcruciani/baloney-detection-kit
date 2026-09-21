"""Offline checks for enforced dependency SCA and SDK-free test environments."""

import os
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
JOBS = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))["jobs"]
AUDIT = JOBS["audit"]
AUDIT_STEP = next(step for step in AUDIT["steps"] if step.get("id") == "audit")
SUMMARY = next(step for step in AUDIT["steps"] if step.get("name") == "Summarize audit outcome")


def test_audit_installs_all_provider_and_development_extras():
    install = next(
        step for step in AUDIT["steps"] if step.get("name") == "Install the environment to audit"
    )
    assert install["run"].splitlines() == [
        "python -m pip install --upgrade pip",
        'pip install -e ".[all,dev]"',
    ]
    assert AUDIT["steps"].index(install) < AUDIT["steps"].index(AUDIT_STEP)


def test_audit_is_unconditional_and_cannot_allow_failure():
    assert "continue-on-error" not in AUDIT
    assert "if" not in AUDIT
    for step in AUDIT["steps"]:
        assert "continue-on-error" not in step
    assert "if" not in AUDIT_STEP
    assert AUDIT_STEP["run"].strip() == "pip-audit"


@pytest.mark.parametrize("exit_code", [0, 1, 2], ids=["clean", "findings", "operational-error"])
def test_audit_command_preserves_exit_status_offline(tmp_path, exit_code):
    stub = tmp_path / "pip-audit"
    stub.write_text(f"#!/bin/sh\nexit {exit_code}\n", encoding="utf-8")
    stub.chmod(0o700)
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", AUDIT_STEP["run"]],
        env={**os.environ, "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == exit_code


@pytest.mark.parametrize("outcome", ["success", "failure", "skipped", "cancelled"])
def test_summary_always_reports_actual_outcome_and_scope(tmp_path, outcome):
    assert SUMMARY["if"] == "always()"
    assert AUDIT["steps"].index(SUMMARY) > AUDIT["steps"].index(AUDIT_STEP)
    expression = "${{ steps.audit.outcome }}"
    assert expression in SUMMARY["run"]
    summary_file = tmp_path / "summary.md"
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", SUMMARY["run"].replace(expression, outcome)],
        env={**os.environ, "GITHUB_STEP_SUMMARY": str(summary_file)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    summary = summary_file.read_text(encoding="utf-8")
    assert "Dependency audit (enforced)" in summary
    assert f"Outcome: {outcome}." in summary
    assert "findings or audit errors fail the job" in summary
    assert "unpublished baloney-detection-kit" in summary
    assert "cannot-audit-package warning" in summary
    assert "not an audit of application logic" in summary


def test_base_and_test_jobs_keep_sdk_free_installs():
    base_install = next(
        step
        for step in JOBS["base-install"]["steps"]
        if step.get("name") == "Install only the base package in an isolated environment"
    )
    assert base_install["run"].splitlines() == [
        "python -m venv .venv-base",
        ".venv-base/bin/python -m pip install .",
    ]
    sdk_check = next(
        step
        for step in JOBS["base-install"]["steps"]
        if step.get("name") == "Check the CLI without provider SDKs"
    )
    assert 'for module in ("anthropic", "openai", "google"):' in sdk_check["run"]
    assert "assert find_spec(module) is None" in sdk_check["run"]
    test_install = next(
        step for step in JOBS["test"]["steps"] if step.get("name") == "Install dependencies"
    )
    assert test_install["run"].splitlines() == [
        "python -m pip install --upgrade pip",
        'pip install -e ".[dev]"',
    ]
    assert JOBS["test"]["strategy"]["matrix"]["python-version"] == ["3.11", "3.12", "3.13"]
