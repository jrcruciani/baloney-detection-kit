## Summary

Describe the change, why it is needed, and any related issue.
See [contributing](../CONTRIBUTING.md).

## Behavior and version review

- [ ] This PR changes behavior (prompts, triggers, modes, boundaries, output contracts, or runtime behavior).
- [ ] I updated [CHANGELOG.md](../CHANGELOG.md) for behavior changes, or explained why this is not a behavior change.
- [ ] I reviewed the affected `prompt-vX.Y` marker under [VERSIONING.md](../VERSIONING.md), bumped it if the contract changed, and kept affected prompt copies/docs/tests consistent (or explained why no marker change applies).

Behavior-change status, reviewed/bumped marker, and rationale:

## Tests

List commands and results; explain anything not run. Before every commit:

```bash
pytest -m "not integration"
ruff check src/ tests/ scripts/
ruff format --check src/ tests/ scripts/
mypy src/bdk scripts/check_markdown_links.py scripts/sync_prompts.py
python scripts/check_markdown_links.py
python scripts/sync_prompts.py --check
```

- [ ] I added or updated focused regression tests where applicable.
- [ ] I did not run integration tests/live calls without explicit authorization and credentials.

## Evidence and adverse effects

For behavioral claims, identify the baseline, prompt variant/marker, model/runtime,
run counts, reviewer process, uncertainty, and adverse effects. State when live
validation was not performed. Do not treat LLM-judge scores or one transcript as
proof of effectiveness.

- [ ] Evidence is minimal and REDACTED or synthetic; it contains no API keys, personal data, or private transcripts (including attachments).

Report suspected vulnerabilities through [SECURITY.md](../SECURITY.md), not in
this public PR. Use the [adverse-effect form](ISSUE_TEMPLATE/adverse_effect_report.yml)
for ordinary unwanted intervention behavior.

## AI assistance

AI-assisted contributions are welcome. Disclose the tools used, the work they
assisted with, and the human review/verification performed, or state
"No AI assistance". Do not attach private assistant transcripts.
