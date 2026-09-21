# Contributing to BDK

Bug fixes, documentation, reproducible adverse-effect reports, and
AI-assisted contributions are welcome. Keep changes focused and preserve the
framework-first [scope and boundaries](README.md#scope-and-boundaries).

## Choose a reporting path

Use [New issue](https://github.com/jrcruciani/baloney-detection-kit/issues/new/choose)
and select **Bug report** for implementation defects or **Adverse-effect report**
for unwanted intervention behavior. The form sources are
[bug_report.yml](.github/ISSUE_TEMPLATE/bug_report.yml) and
[adverse_effect_report.yml](.github/ISSUE_TEMPLATE/adverse_effect_report.yml).

For usage questions or proposals, search
[existing issues](https://github.com/jrcruciani/baloney-detection-kit/issues)
first, then open a blank issue with a clear question and non-sensitive context.
Discussions are not enabled; no Discussions account or link is required.
Do not label ordinary adverse effects as security vulnerabilities by default.
For suspected vulnerabilities, follow [SECURITY.md](SECURITY.md) and do not
post details publicly.

## Development setup

Use Python 3.11 or newer (CI covers 3.11, 3.12, and 3.13). From a source checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell.
The `dev` extra supplies the test and quality tools; it does not require a
provider SDK or real API credentials for the offline suite.
For maintainer-only publication steps, see the [release checklist](docs/RELEASING.md).

## Required checks

Run the complete nonintegration suite and quality checks before every commit:

```bash
pytest -m "not integration"
ruff check src/ tests/ scripts/
ruff format --check src/ tests/ scripts/
mypy src/bdk scripts/check_markdown_links.py scripts/sync_prompts.py
python scripts/check_markdown_links.py
python scripts/sync_prompts.py --check
```

Use `ruff format src/ tests/ scripts/` when formatting needs correction.
The link checker is offline and covers repository Markdown, including
`SECURITY.md`, `CONTRIBUTING.md`, and the pull request template; it does not
fetch URLs or validate heading anchors.
For intervention changes, edit the canonical full block or specialized source
variants, then run `python scripts/sync_prompts.py` before checking. See the
[prompt distribution contract](prompts/intervention/README.md#canonical-contract-and-synchronization).

CI also measures coverage with:

```bash
pytest -m "not integration" --cov=bdk --cov-report=xml --cov-report=term-missing --cov-fail-under=60
```

Do not run integration tests or live model calls without explicit authorization
and credentials supplied for that purpose. They can transmit prompts and incur
provider charges. Do not copy another developer's credentials or use real keys
in fixtures. Keep ordinary regression tests deterministic and offline with
mocks or synthetic examples.

## Markdown-only formatting

Build the formatter inventory from `git ls-files`, not a recursive directory
walk; never include dependencies, virtual environments, Git internals, or caches.
Exclude authored prose in `essay/`, `posts/`, and `research/diagnosis-paper/`,
and historical evidence in `validation/**/artifacts/` or any `results/` directory.
Preserve copyable code blocks, prompt instruction bodies and markers exactly;
keep `skill/SKILL.md` instructions and its first YAML block intact.
Format canonical documentation before running `python scripts/sync_prompts.py`
to update derived root regions, `skills/baloney-detection-kit/`, and packaged
mirrors. Keep `docs/RELEASING.md` at most 30 lines. Check semantic and prompt-body
invariants as well as the required gates, and commit formatting separately
without wording or link changes.

## Behavioral changes and evidence

Changes to prompts, triggers, modes, high-stakes boundaries, output contracts,
or runtime behavior need explicit review, not an incidental documentation edit.
Follow [VERSIONING.md](VERSIONING.md): product versions and `prompt-vX.Y`
behavior markers are distinct.

For a behavior change, update [CHANGELOG.md](CHANGELOG.md), review the affected
prompt behavior version, and bump it when the behavior contract changes.
Keep the reviewed or bumped marker consistent across the affected source
prompts, packaged copies, documentation, and regression tests. If no prompt
marker changes, explain why in the PR; do not silently change the behavior
policy or imply that a product-version bump replaces prompt-version review.

Describe expected versus observed outcomes, the baseline, prompt variant and
marker, product version/commit, local edits, model/runtime, run counts, reviewer
process, uncertainty, and adverse effects for behavioral evidence. Add focused
tests for changed behavior. LLM-judge scores and a single successful transcript
are not proof of effectiveness; say when live validation was not performed.

## Protect reports and transcripts

Generated reports and saved sessions can contain complete prompts and responses.
Never commit or paste API keys, personal data, or private transcripts into
issues, PRs, test fixtures, logs, or attachments. Use the smallest synthetic or
manually REDACTED excerpt that demonstrates the issue and inspect metadata,
paths, and URLs as well as text. Do not assume automated redaction, ignored
paths, or local file permissions make an artifact safe to publish.
Follow [SECURITY.md](SECURITY.md) for suspected disclosure vulnerabilities.

## Pull requests and commits

Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md). State the scope,
behavior-change status, checks run and their results, evidence limitations, and
any adverse effects. Include changelog and prompt-marker review where required.

Write commit messages in English using Conventional Commits, for example
`docs: clarify adverse-effect reporting` or `fix: preserve report metadata`.
Keep commits and PRs focused; avoid unrelated formatting or authored-content
rewrites.

AI-assisted contributions are welcome. Disclose in the PR whether AI tools
were used, which tools and for what work, and what you personally reviewed or
verified (or state "No AI assistance"). You remain responsible for correctness,
provenance, privacy, and the evidence supporting the contribution. Do not
publish private assistant transcripts as proof of review.
