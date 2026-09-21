"""Offline regression checks for the repository's supported issue-form subset."""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / ".github" / "ISSUE_TEMPLATE"
REPOSITORY_URL = "https://github.com/jrcruciani/baloney-detection-kit"
FORM_FIELDS = {
    "bug_report.yml": {
        "safe-report": "checkboxes",
        "bdk-version": "input",
        "environment": "textarea",
        "reproduction": "textarea",
        "expected": "textarea",
        "observed": "textarea",
    },
    "adverse_effect_report.yml": {
        "safe-report": "checkboxes",
        "bdk-version": "input",
        "prompt-variant": "input",
        "prompt-version": "input",
        "model-runtime": "textarea",
        "transcript": "textarea",
        "expected": "textarea",
        "observed": "textarea",
        "category": "dropdown",
        "severity": "dropdown",
        "consequence-domain": "dropdown",
        "consequence": "textarea",
    },
}


@pytest.mark.parametrize("filename", FORM_FIELDS)
def test_issue_form_schema_and_required_fields(filename):
    form = yaml.safe_load((TEMPLATES / filename).read_text(encoding="utf-8"))
    assert isinstance(form, dict)
    assert set(form) == {"name", "description", "title", "body"}
    for key in ("name", "description", "title"):
        assert isinstance(form[key], str) and form[key].strip()
    assert isinstance(form["body"], list) and form["body"]

    fields = {}
    labels = []
    for field in form["body"]:
        assert isinstance(field, dict)
        attributes = field["attributes"]
        assert isinstance(attributes, dict)
        if field["type"] == "markdown":
            assert set(field) == {"type", "attributes"}
            assert set(attributes) == {"value"}
            assert isinstance(attributes["value"], str) and attributes["value"].strip()
            continue

        identifier = field["id"]
        assert isinstance(identifier, str) and re.fullmatch(r"[A-Za-z0-9_-]+", identifier)
        assert identifier not in fields, f"Duplicate field id: {identifier}"
        fields[identifier] = field["type"]
        assert isinstance(attributes["label"], str) and attributes["label"].strip()
        labels.append(attributes["label"])

        if field["type"] == "checkboxes":
            assert set(field) == {"type", "id", "attributes"}
            assert set(attributes) == {"label", "options"}
            options = attributes["options"]
            assert isinstance(options, list) and options
            for option in options:
                assert isinstance(option, dict) and set(option) == {"label", "required"}
                assert isinstance(option["label"], str) and option["label"].strip()
                assert option["required"] is True
            assert len({option["label"] for option in options}) == len(options)
            continue

        assert set(field) == {"type", "id", "attributes", "validations"}
        assert set(field["validations"]) == {"required"}
        assert field["validations"]["required"] is True
        allowed = {"label", "description"}
        if field["type"] == "dropdown":
            allowed |= {"options", "multiple"}
            options = attributes["options"]
            assert isinstance(options, list) and options
            assert all(isinstance(option, str) and option.strip() for option in options)
            assert len(set(options)) == len(options)
            if "multiple" in attributes:
                assert isinstance(attributes["multiple"], bool)
        else:
            assert field["type"] in {"input", "textarea"}
            allowed.add("placeholder")
            if field["type"] == "textarea":
                allowed.add("render")
        assert set(attributes) <= allowed
        for key in set(attributes) - {"options", "multiple"}:
            assert isinstance(attributes[key], str) and attributes[key].strip()
    assert fields == FORM_FIELDS[filename]
    assert len(set(labels)) == len(labels)


def test_adverse_effect_choices_and_redacted_transcript():
    form = yaml.safe_load((TEMPLATES / "adverse_effect_report.yml").read_text(encoding="utf-8"))
    fields = {field["id"]: field for field in form["body"] if "id" in field}
    assert fields["category"]["attributes"]["options"] == [
        "over-trigger",
        "under-trigger",
        "stubbornness",
        "false balance",
        "reduced usefulness",
        "unsafe guidance",
    ]
    assert fields["category"]["attributes"]["multiple"] is True
    assert fields["severity"]["attributes"]["options"] == [
        "Low - minor friction",
        "Moderate - materially reduced usefulness",
        "High - plausible serious consequence",
        "Critical - actual or imminent serious consequence",
        "Uncertain",
    ]
    assert fields["consequence-domain"]["attributes"]["options"] == [
        "Not high-stakes",
        "Health",
        "Legal",
        "Financial",
        "Physical safety",
        "Employment or education",
        "Privacy or security",
        "Other high-stakes domain (describe below)",
        "Uncertain",
    ]
    assert fields["consequence-domain"]["attributes"]["multiple"] is True
    assert fields["transcript"]["attributes"]["render"] == "text"
    assert "REDACTED" in fields["transcript"]["attributes"]["label"]
    assert "prompt-v2.0" in fields["prompt-version"]["attributes"]["placeholder"]


@pytest.mark.parametrize("filename", FORM_FIELDS)
def test_issue_forms_warn_before_collecting_public_evidence(filename):
    form = yaml.safe_load((TEMPLATES / filename).read_text(encoding="utf-8"))
    notice = form["body"][0]
    assert notice["type"] == "markdown"
    warning = notice["attributes"]["value"]
    for phrase in ("Never paste API keys", "personal data", "private transcripts", "REDACTED"):
        assert phrase in warning
    assert f"{REPOSITORY_URL}/blob/main/SECURITY.md" in warning
    assert "vulnerabilities" in warning
    consent = form["body"][1]
    assert consent["id"] == "safe-report"
    assert "not a vulnerability disclosure" in consent["attributes"]["options"][0]["label"]


def test_issue_chooser_has_working_questions_fallback_not_discussions():
    config = yaml.safe_load((TEMPLATES / "config.yml").read_text(encoding="utf-8"))
    assert isinstance(config, dict)
    assert set(config) == {"blank_issues_enabled", "contact_links"}
    assert config["blank_issues_enabled"] is True
    contacts = config["contact_links"]
    assert isinstance(contacts, list) and len(contacts) == 2
    for contact in contacts:
        assert set(contact) == {"name", "url", "about"}
        assert all(isinstance(value, str) and value.strip() for value in contact.values())
        assert "/discussions" not in contact["url"]
    assert contacts[0]["url"] == f"{REPOSITORY_URL}/issues"
    assert "blank issue" in contacts[0]["about"]
    assert contacts[1]["url"] == f"{REPOSITORY_URL}/blob/main/SECURITY.md"


def test_pr_template_preserves_review_and_privacy_checklist():
    template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    for heading in (
        "Summary",
        "Behavior and version review",
        "Tests",
        "Evidence and adverse effects",
        "AI assistance",
    ):
        assert f"## {heading}" in template
    checkboxes = re.findall(r"^- \[ \] (.+)$", template, flags=re.MULTILINE)
    for phrase in (
        "This PR changes behavior",
        "CHANGELOG.md",
        "prompt-vX.Y",
        "focused regression tests",
        "explicit authorization and credentials",
        "API keys, personal data, or private transcripts",
    ):
        assert any(phrase in checkbox for checkbox in checkboxes), phrase
    for command in (
        'pytest -m "not integration"',
        "ruff check src/ tests/ scripts/",
        "ruff format --check src/ tests/ scripts/",
        "mypy src/bdk scripts/check_markdown_links.py",
        "python scripts/check_markdown_links.py",
    ):
        assert command in template
    assert "(../SECURITY.md)" in template
    assert "(ISSUE_TEMPLATE/adverse_effect_report.yml)" in template
    assert "Disclose the tools used" in template
    assert "No AI assistance" in template
