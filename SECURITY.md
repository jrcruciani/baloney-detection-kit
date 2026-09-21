# Security policy

## Supported versions

Security reports are accepted for BDK 3.x. Fixes target the latest 3.x release;
older 3.x installations should upgrade rather than assume a backport.
Pre-3.x releases are not supported by this policy. Include the product version
or commit and, where relevant, the prompt variant and `prompt-vX.Y` marker.
See [versioning](VERSIONING.md).

Support here describes report scope, not a security certification, response-time
commitment, or guarantee that BDK or a model will produce safe or correct output.

## Report vulnerabilities privately

Do not put vulnerability details, exploit transcripts, API keys, or private
data in public issues, pull requests, logs, or attachments.

Check the repository's
[Security advisories page](https://github.com/jrcruciani/baloney-detection-kit/security/advisories).
If **Report a vulnerability** is available, use it to submit a private report
for maintainer review and coordinated disclosure.

Private vulnerability reporting is currently disabled in this repository.
Adding this policy does not enable it; only a maintainer can enable the GitHub
feature. If the reporting button is absent and no verified private maintainer
channel is available, open a
[minimal contact request](https://github.com/jrcruciani/baloney-detection-kit/issues/new)
asking maintainers to enable private reporting or provide a private channel.
For example: "Please provide a private channel for a security report."
Do not include the affected endpoint, reproduction, impact details, or files in
that public request. Wait for a confirmed private route before sharing details.

In the private report, provide the affected version, operating system/runtime,
minimal synthetic reproduction, expected and observed behavior, potential
impact, and any known workaround. Use dummy credentials and redact identifying
data even in a private report. Coordinate publication with maintainers; this
policy does not promise an advisory, bounty, or disclosure timeline.

## In scope

- Vulnerabilities in the reference CLI and its provider integration, including
  API-key handling and custom base URL validation before credentials are sent.
- Unintended disclosure or unsafe handling of generated reports and saved
  session files, which may contain prompts, responses, and sensitive transcripts.
- Other reproducible security defects in code or artifacts distributed by BDK.

Base URL checks are not a trust decision about the destination or a complete
network security boundary. Use only endpoints you trust to receive the API key
and conversation. An explicit insecure/private URL override does not make that
destination safe. BDK's redaction and file-permission helpers are not encryption
or a guarantee that every secret or personal detail has been removed.

Keep report and session files in access-controlled storage. Before sharing,
create a minimal synthetic or manually redacted example; review its prompts,
responses, metadata, paths, URLs, and attachments. Never upload a raw private
transcript or a real API key. If a credential was exposed, revoke or rotate it
through its provider; deleting a public message alone is not sufficient.

## Behavioral adverse effects are a separate reporting path

Over-triggering, under-triggering, stubbornness, false balance, reduced
usefulness, and unsafe model guidance ordinarily belong in the
[adverse-effect report form](.github/ISSUE_TEMPLATE/adverse_effect_report.yml),
available through [New issue](https://github.com/jrcruciani/baloney-detection-kit/issues/new/choose).
Use a minimal REDACTED or synthetic transcript and describe the consequence
without personal or private data. BDK is not a safety guarantee or a substitute
for qualified judgment in high-stakes settings.

If the behavior also reveals a security vulnerability, or you are unsure
whether public details would expose one, use the private route above instead
of publishing a transcript. See [contributing](CONTRIBUTING.md) for ordinary
bugs and questions.
