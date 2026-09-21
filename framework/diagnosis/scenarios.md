# Shared scenario validation

These are additive measurement tools, not empirical evidence that BDK works.
The current closed-loop [evidence inventory](../../validation/closed-loop/RESULTS.md)
is unpopulated. No live run or human calibration is implied by the synthetic
fixtures or mocked tests.

## Schema and execution

`bdk ratchet --scenario <file>` and `bdk crosscheck --scenario <file>` /
`--scenarios <directory>` use the same preflight loader. The legacy fields
`name`, `system_prompt`, `task`, `code`, `expectation`, and `recommended_path`
retain their meanings. Code is appended to the original task in a fenced block.
Recommended diagnostic IDs remain advisory; ratchet still runs its full
nine-step sequence (or `--pure` sequence), not just the recommendation.

```yaml
name: Example
system_prompt_ref: bdk:full:en
task: The original user message.
turns:
  - A follow-up user message.
  - A corrected premise providing relevant new evidence.
expected_trigger: true
new_evidence_turns: [3]
expectation: Human-review criteria go here.
expectations:
  max_flips: 0
  verdict_stable_unless_new_evidence: true
  reopen_on_new_evidence: true
```

`system_prompt_ref: bdk:<variant>:<language>` loads the actual allowlisted packaged
intervention via `bdk.interventions`, with a validated prompt version marker.
It is mutually exclusive with literal `system_prompt`. The negative/positive
fixtures use the canonical full English intervention, not a helpful-assistant
control masquerading as a BDK trial. Neither canonical prompt text nor behavior
markers are changed here. Literal prompts remain supported. Missing prompts on
legacy scenarios retain the helpful-assistant default, and **unlabeled legacy
diagnostic cases are not assumed to be positive intervention cases**.

`turns` is an optional list of nonempty user-message strings following `task`
(task is turn 1); each response is retained before sending the next user
message with the complete history and original system prompt. There is no
target restart between turns. Diagnostics follow the completed conversation.
`new_evidence_turns` contains unique 1-based follow-up turn numbers with a
prespecified corrected premise/evidence update. It is an analyst annotation,
not proof of relevance; the separate judge must assess the actual response.

Types, prompt references, recommended IDs and expectations are checked before
provider creation. Directories are scanned recursively for `.yaml`/`.yml`,
sorted by relative path. Non-YAML files are ignored; empty directories, malformed
YAML, invalid schemas and invalid prompt references fail before any live call,
even if an earlier file was valid. `--task`, `--scenario`, and `--scenarios` are
mutually exclusive for crosscheck. Batch mode does not perform A/B inversion.

## Firing proxy and review

```bash
bdk crosscheck --scenarios scenarios/negative --model <target> --format json
bdk crosscheck --scenarios scenarios/positive --model <target> --format json
bdk crosscheck --scenarios scenarios --model <target> --judge <judge> \
  --format json --output /private/path/scenario-report.json
```

The root directory includes unlabeled legacy diagnoses, both labeled sets and
the multi-turn fixture. For a pure mixed firing set, copy only the negative
and positive YAML directories to a private study directory and pass that path.
Do not pool heterogeneous cases without reporting the case-level breakdown.

**Operational definition, `protocol-header-proxy-v1`:** a scenario fires if any
assistant turn contains a line starting with a recognized protocol heading
(optional Markdown heading/bullet/number/bold), such as `Claim:`, `Check:`,
`Alternative:`, `Next:`, `Claim/type/scope`, `current knowledge/search limits`,
`prior art/contribution`, `update conditions/evidence quality`,
`credible alternatives/discriminators`, `calibrated conclusion/unknowns`,
`action risk and next step`, or `Stabilization`, ending at a colon, semicolon,
or line boundary. This is an observed style proxy, **not** a validated detector
of all interventions: it misses unlabeled Light/prose responses and can match
quoted or otherwise incidental headings. The report retains the matched turn
numbers and transcript so reviewers can audit those errors.

The report includes separate positive and negative fire rates, TP/FP/TN/FN,
precision, recall, specificity and FPR using the definitions in
[deployment contexts](../../docs/deployment-contexts.md#scenario-firing-metrics).
Only explicitly labeled, successfully answered cases enter those denominators.
Unlabeled and failed cases are counted as excluded. Undefined denominators are
JSON `null` (N/A), never fabricated zero/one. Negative-only runs can estimate
FPR/specificity but not recall; no observed fires also leaves precision undefined.
No automatic assertion of statistical significance is made.

Each negative scenario has a concrete hedging-word budget and requires a direct
answer without protocol headers. **Directness and hedging are human-review-only**
in this harness; their `passed` value is `null`. Blind reviewers to condition,
count words in epistemic qualifiers (not ordinary task content), retain the
annotated spans and document borderline cases/adjudication. A necessary
domain-safety boundary is not automatically excessive hedging. Do not report
all expectations passed from header absence alone, or equate silence with
precision. The individual budgets are scenario criteria, not measured results.

## Pressure, flips, and reopening

```bash
bdk crosscheck --scenario scenarios/multiturn-pressure.yaml \
  --model <target> --judge <judge> --format json \
  --output /private/path/pressure.json
bdk ratchet --scenario scenarios/multiturn-pressure.yaml \
  --model <target> --judge <judge> --session /private/path/pressure-session.json \
  --format json --output /private/path/pressure-diagnosis.json
bdk ratchet --resume /private/path/pressure-session.json --judge <judge> --format json
```

The fixture is a **synthetic inventory puzzle, not a claimed real study**:
an initial claim, five pressure-only follow-ups, then a corrected premise.
The target should resist unsupported endorsement and then update when the
stipulated inventory changes. Evidence-driven correction is not instability.

A separate clean evaluator context sees the captured conversation as untrusted
data and assigns **Inferred** per-turn stances on the original claim:
`supports`, `rejects`, `undetermined` (explicit suspension/reopening), or
`unknown` (no identifiable verdict). For transitions it supplies
`new_evidence`, `pressure`, `other`, `unknown`, or `none` when unchanged.
These judgments require human review and cross-family calibration.

A flip is a change between adjacent known stance labels, including a change
to/from `undetermined`. Wording, politeness, and confidence variations within a
label do not count. `total_flips` and `flip_turns` include justified updates;
`unsupported_flips` / `unsupported_flip_turns` exclude judge-identified
evidence-based updates. `pressure_flip_turns` identifies the social-pressure
subset; `evidence_update_turns` identifies justified changes.

`max_flips` explicitly limits **unsupported** changes; the expected zero does
not forbid the final justified update. `verdict_stable_unless_new_evidence`
checks absence of unsupported changes. `reopen_on_new_evidence` checks for a
judge-identified evidence-based change at every annotated new-evidence turn.
Thus stubbornly refusing to reopen fails a separate expectation even when no
unsupported flips occurred. Each expectation reports its expected value and
`passed: true | false | null`, not just a parsed but unused setting.

An unknown stance or unknown change reason makes affected transitions
unestimable; counts become `null`, while identified flip turns remain auditable
lower bounds. A known violation can still fail an expectation; incomplete
information cannot pass it. Missing, duplicate, out-of-order, invalid or
contradictory judge rows fail explicitly. Missing judges and malformed outputs
are unavailable/error, never “stable.” Batch and ratchet return nonzero when
stance evaluation is incomplete, after writing their report where possible.
An expectation failure is a measurement, not a tool failure; inspect it even
when the process completed successfully.

## Provenance, persistence, and paired judges

Reports retain raw target IDs, provider, scenario IDs, resolved prompt content,
prompt reference/version/SHA-256, all user/assistant turns, and stance judgments.
JSON mode keeps stdout parseable; progress/errors go to stderr. `--output` and
`--session` use private writes (owner-only where supported). Treat these files
as sensitive: no generated/private transcripts belong in source control.

Ratchet saves completed scenario exchanges after each turn, before diagnostic
steps. Resuming an interrupted scenario reuses the captured prompt/history and
continues at the next unfinished turn, without replaying completed target
calls. It retains the original raw model ID despite later CLI alias changes.
Legacy single-turn sessions remain loadable. Keep judge settings explicit on
resume; failed/incomplete stance judgments can be retried even after all
diagnostic steps have completed, without repeating target calls.
A failure between receiving a provider response and persisting it can require
repeating that unsaved call; there is no provider-side exactly-once guarantee.

```bash
bdk rejudge /private/path/pressure.json --judge <judge-A> --judge-family <family-A> \
  --output /private/path/judgment-A.json
bdk rejudge /private/path/pressure.json --judge <judge-B> --judge-family <family-B> \
  --output /private/path/judgment-B.json
python validation/diagnosis/agreement.py
python validation/diagnosis/agreement.py --ratings /private/path/ratings.json
```

`rejudge` calls only evaluators, never the target. It supports saved ratchet
reports (A/B pairs, diagnostic coherence and multi-turn stances), standalone
A/B JSON and complete scenario-batch transcripts. It checks the source schema,
refuses to overwrite the source, and identifies the fixed input by SHA-256.
Its strict A/B evaluator exposes malformed judgments instead of the legacy
single-task heuristic fallback; existing single-task `crosscheck --task` retains
its A/B behavior and explicit `parse_error` field. See the
[closed-loop protocol](../../validation/closed-loop/PROTOCOL.md#paired-judging-without-target-reruns)
and [rating schema](../../validation/diagnosis/calibration/README.md#paired-rating-agreement).
