# BDK cleanup audit

## Scope and baseline

Phase 0 only, audited on 2026-11-16 against fetched `origin/main` at
`6c52da81f37d50dba6318aae5e437a82813b4eb6`
(`fix: separate evidence reassessment from stance changes (#27)`).
The worktree HEAD matched that commit and had no tracked or untracked changes
before inspection. All baseline checks below ran before this report was added.
This report is the only repository change in this phase.

The supplied cleanup brief is a hypothesis list, not evidence or authorization
to run older plans. No prompts, generated distributions, historical evidence,
authored prose, repository settings, or result cells were changed. No live model
calls, tags, releases, or package publications were performed.

## First- and second-level inventory

Inventory source: `git ls-files` at the baseline, 247 tracked files, including
108 Markdown files. Every tracked first- and second-level path is listed below;
directory rows cover their descendants, with mixed trees qualified explicitly.
Git internals and ignored local environments/caches are not distribution paths.
The new report itself is not part of this baseline inventory.

Classes: **source** means maintained code, documentation, configuration, or
fixtures; **generated** means derived output, wholly or in a marked region;
**legacy** means a supported compatibility surface; **authored prose** and
**evidence** identify content to preserve rather than rewrite. Multiple classes
are intentional. "None" means no automatic upstream source, not no intellectual
lineage.

### Root paths and repository configuration

| Path | Class | Upstream source or role |
| --- | --- | --- |
| `.claude-plugin/` | source | Plugin metadata; no generator. |
| `.claude-plugin/plugin.json` | source | Minimal Claude Code manifest; version aligned manually. |
| `.github/` | source | Contribution and automation configuration. |
| `.github/ISSUE_TEMPLATE/` | source | Bug/adverse-effect forms and issue chooser configuration. |
| `.github/PULL_REQUEST_TEMPLATE.md` | source | Required review, checks, evidence, and AI disclosure template. |
| `.github/dependabot.yml` | source | Dependency update configuration. |
| `.github/workflows/` | source | CI and human-gated publication workflows. |
| `.gitignore` | source | Local artifacts and generated-run exclusions. |
| `.zenodo.json` | source | Publication metadata, not proof of publication. |
| `CHANGELOG.md` | source | Product and behavior change history. |
| `CITATION.cff` | source | Citation metadata, manually version-aligned. |
| `CONTRIBUTING.md` | source | Contributor workflow and six required gates. |
| `LICENSE` | source | Distribution license; copied into portable skill. |
| `NOTICE` | source | Attribution; copied into portable skill. |
| `PLAYBOOK.md` | source | Maintained explanation of canonical intervention behavior. |
| `README.md` | source | Project entry point and currently extensive reference material. |
| `ROOT_PROMPT.es.md` | source + generated | Authored wrapper; marked block from Spanish full source. |
| `ROOT_PROMPT.md` | source + generated | Authored wrapper; marked block from English full source. |
| `SECURITY.md` | source | Reporting and privacy policy. |
| `VERSIONING.md` | source | Product/prompt distinction and compatibility policy. |
| `pyproject.toml` | source | Build, dependency, executable, and quality-tool configuration. |

### Documentation, method, and prose

| Path | Class | Upstream source or role |
| --- | --- | --- |
| `docs/` | source | Product and integration documentation. |
| `docs/CONTEXT.md` | source | Spanish product-context document; no generator. |
| `docs/RELEASING.md` | source | Human-gated release checklist. |
| `docs/agentic-plan-execute-verify.md` | source | Downstream runtime pattern; not an executable adapter. |
| `docs/deployment-contexts.md` | source | Adoption guidance and measurement definitions. |
| `docs/integration.md` | source | Skill installation and distribution maintenance. |
| `docs/migration.md` | source | Historical v5.0-to-v5.1 diagnostic migration guidance. |
| `docs/plans/` | source | Historical diagnostic-engine plan; not current authorization. |
| `docs/related-work.md` | source | Positioning and methodological cautions. |
| `docs/second-opinion-operational.md` | source | Reviewer operations; copied into portable skill resources. |
| `essay/` | authored prose | Preserve location and wording. |
| `essay/case-studies/` | authored prose | Narrative case studies; no generator. |
| `essay/mini-cultos-ai.md` | authored prose | Spanish essay; no generator. |
| `framework/` | source | Manual diagnostic framework. |
| `framework/README.md` | source | Framework navigation. |
| `framework/diagnosis/` | source | Canonical diagnostic method, guide, taxonomy, scenarios, and limits. |
| `posts/` | authored prose | Publication drafts; preserve wording and location. |
| `posts/blog-impermanente.md` | authored prose | Spanish blog draft. |
| `posts/linkedin.md` | authored prose | Spanish social publication draft. |
| `posts/reddit.md` | authored prose | English publication draft. |
| `research/` | authored prose | Research scaffold, not cleanup source material. |
| `research/diagnosis-paper/` | authored prose | LaTeX paper, bibliography, appendices, and figure placeholder; preserve. |

### Prompts, skills, implementation, and scenarios

| Path | Class | Upstream source or role |
| --- | --- | --- |
| `prompts/` | source | Human-facing intervention and diagnostic texts. |
| `prompts/README.md` | source | Prompt-family navigation. |
| `prompts/diagnosis/` | source + manual mirror | Cards/catalog alongside method guide; packaged catalog parity tested, not generated by sync script. |
| `prompts/intervention/` | source | Six English variants and Spanish compact/full sources. |
| `scenarios/` | source | Mixed diagnostic and intervention fixtures, not measured outcomes. |
| `scenarios/drift.yaml` | source | Unlabeled diagnostic case. |
| `scenarios/hallucination.yaml` | source | Unlabeled diagnostic case. |
| `scenarios/multiturn-pressure.yaml` | source | Synthetic seven-message pressure/corrected-premise case. |
| `scenarios/negative/` | source | Eight labeled non-trigger cases. |
| `scenarios/positive/` | source | Two labeled single-turn trigger cases. |
| `scenarios/refusal.yaml` | source | Unlabeled diagnostic case. |
| `scenarios/sql-injection.yaml` | source | Diagnostic code-review input, not a tool-execution case. |
| `scenarios/sycophancy.yaml` | source | Diagnostic code-review input, not a tool-execution case. |
| `scenarios/tone-shift.yaml` | source | Unlabeled diagnostic case. |
| `scripts/` | source | Offline maintenance tools. |
| `scripts/check_markdown_links.py` | source | Git-inventoried local path checker; no anchor/remote validation. |
| `scripts/sync_prompts.py` | source | Intervention and portable-skill generator. |
| `skill/` | legacy + source + generated | Supported editable skill tree; generated regions/text are exceptions. |
| `skill/SKILL.md` | legacy + source + generated | Maintained frontmatter/wrapper; marked body from English full prompt. |
| `skill/checklist/` | legacy + source | Human checklist and manual review rubric. |
| `skill/examples/` | legacy + source | Maintained scenario/conversation examples, copied into portable skill. |
| `skill/prompts/` | legacy + generated | Plain text extracted from canonical English full block, plus marker. |
| `skills/` | generated | Portable distribution parent. |
| `skills/baloney-detection-kit/` | generated | Entire 12-file tree from legacy skill and explicit resources, with link rebasing. |
| `src/` | source + generated | Reference implementation and package data. |
| `src/bdk/` | source + generated | Python code; intervention data generated from prompt sources; diagnostic catalog manually mirrored. |
| `templates/` | source | Manual worksheets, not installed package data. |
| `templates/diagnosis/` | source | Diagnostic baseline, incident, and ratchet templates. |
| `validation/` | source + evidence | Recipes/tools/fixtures mixed with protected historical outputs. |
| `validation/closed-loop/` | source + evidence | Protocol, six runnable pilot files, expanded matrix, empty RESULTS template; `results/` preserved. |
| `validation/diagnosis/` | source + evidence | Agreement/calibration/runners and case analyses; all nested `artifacts/` preserved; synthetic calibration labeled. |

### Test paths

All rows are **source**: manually maintained offline regression tests unless
marked integration. None is a generated derivative.

| Path | Role |
| --- | --- |
| `tests/` | Regression suite. |
| `tests/conftest.py` | Shared isolated/mock fixtures. |
| `tests/integration/` | Live-provider tests; excluded and not run. |
| `tests/test_agreement.py` | Agreement math and ratings validation. |
| `tests/test_azure_foundry_provider.py` | Azure adapter. |
| `tests/test_calibration.py` | Synthetic weight sensitivity. |
| `tests/test_ci_workflow.py` | CI contracts. |
| `tests/test_cli.py` | Core CLI behavior. |
| `tests/test_cli_alias.py` | Canonical and legacy executable compatibility. |
| `tests/test_cli_apply.py` | Packaged prompt retrieval. |
| `tests/test_cli_models.py` | Model alias resolution. |
| `tests/test_cli_scenarios.py` | CLI scenario workflows. |
| `tests/test_coherence.py` | Offline coherence analysis. |
| `tests/test_coherence_llm.py` | Mocked judge-based coherence. |
| `tests/test_community_templates.py` | Community/reporting templates. |
| `tests/test_config.py` | Configuration parsing. |
| `tests/test_cross_judge.py` | Cross-family runner behavior with mocks. |
| `tests/test_crosscheck.py` | A/B behavior checks with mocks. |
| `tests/test_engine.py` | Diagnostic engine. |
| `tests/test_interventions.py` | Intervention catalog and languages. |
| `tests/test_labels.py` | Observed/Inferred labeling. |
| `tests/test_markdown_links.py` | Offline Markdown scanner. |
| `tests/test_prompt_catalog_mirror.py` | Diagnostic catalog byte parity. |
| `tests/test_prompt_sync.py` | Generated blocks, variants, markers, and sync behavior. |
| `tests/test_prompts.py` | Diagnostic prompt loading/rendering. |
| `tests/test_providers.py` | Mocked provider routing and SDK behavior. |
| `tests/test_rejudge.py` | Paired judging of saved captures. |
| `tests/test_release_metadata.py` | Version and distribution metadata. |
| `tests/test_report.py` | Report rendering. |
| `tests/test_run_case.py` | Historical case runner with mocks. |
| `tests/test_scenario_checks.py` | Firing proxy and stance assessment. |
| `tests/test_scenarios.py` | Shared scenario preflight validation. |
| `tests/test_scoring.py` | Diagnostic support scoring. |
| `tests/test_security.py` | Existing URL/file safeguards. |
| `tests/test_session.py` | Session persistence. |
| `tests/test_skill_distribution.py` | Portable inventory, parity, links, and manifest. |
| `tests/test_skill_frontmatter.py` | YAML metadata and portable directory-name matching. |

## Verified source-to-distribution contract

`prompts/intervention/prompt-full.md` explicitly declares itself canonical.
`prompts/intervention/README.md` documents the marked full block as the contract;
`scripts/sync_prompts.py` implements that mapping. `docs/integration.md`
describes the legacy-source/portable-output split. There is no competing
canonical full source.

| Maintained source | Derivative | Mechanism |
| --- | --- | --- |
| English full prompt marked block | `ROOT_PROMPT.md`, `skill/SKILL.md` marked regions | `sync_prompts.py`; wrappers retained. |
| English full prompt block contents | `skill/prompts/critical_investigation_mode.txt` | Same generator, with behavior marker. |
| Spanish full prompt marked block | `ROOT_PROMPT.es.md` marked region | Same generator; translation is maintained manually. |
| Six English intervention files | `src/bdk/data/interventions/prompt-*.md` | Same generator, whole-file byte mirrors. |
| Spanish compact/full files | `src/bdk/data/interventions/es/prompt-*.md` | Same generator, whole-file byte mirrors. |
| Every file in `skill/` | Corresponding portable skill path | Same generator; declared link rewrites only. |
| Playbook, full English prompt, operational note | Portable `resources/` paths | Same generator; selected local resources/link rebasing. |
| `LICENSE`, `NOTICE` | Portable attribution files | Same generator, copies. |
| Diagnostic catalog pair | `prompts/diagnosis/catalog.yaml`, `src/bdk/data/prompts.yaml` | Manual synchronization, parity test; no generator or authoritative direction established. |
| Diagnostic method/guide and cards | Human-facing diagnostic toolkit | Maintained related texts, not generated by intervention sync. |

No `.gitattributes` exists. Some generated regions explain their provenance,
but not every whole-file output has a generated header. Future provenance work
must preserve exact retrieval/body contracts rather than prepend text blindly.

## Starting-point hypotheses

| Hypothesis in the brief | Verdict on main | Evidence and consequence |
| --- | --- | --- |
| Closed-loop RESULTS is a template with no real run | Confirmed for committed closed-loop evidence | `RESULTS.md` and protected `results/findings.md` explicitly say missing data; all cells are TODO/pending. Private/uncommitted runs cannot be ruled out. |
| Eight negative, two positive, one multi-turn intervention cases; none with tools | Confirmed | Loaded all 17 root-tree YAML files offline: eight labeled negatives, two single-turn positives, one seven-message positive pressure fixture, six unlabeled diagnostic cases. Code snippets in two diagnostic inputs do not execute tools. |
| Portable skill is English-only; plugin has no hooks/commands/agents | Confirmed | 12-file English distribution, integration guide, and minimal manifest agree. This is a documented scope, not a broken plugin. |
| CONTEXT is Spanish and the rest of the repository English | Partly confirmed; blanket language claim incorrect | `docs/CONTEXT.md` is Spanish. Root/compact/full Spanish distributions and authored Spanish essays/posts also exist intentionally. Preserve translations and protected prose. |
| Gemini dependency uses google-generativeai while README uses google-genai | Already resolved | `pyproject.toml` gemini/all extras use `google-genai>=1.0`; `src/bdk/providers.py:263-265` imports `google.genai` and constructs its client. |
| README recommends PyPI install without established publication | Confirmed at audit time | README recommends package-name installs. `https://pypi.org/pypi/baloney-detection-kit/json` returned HTTP 404. This establishes no package at that endpoint on this date, not permanent unavailability. |
| RESULTS links to issue 11 rather than closed-loop issue 10 | Confirmed | Read both live issues: issue 10 is closed-loop validation; issue 11 is Portuguese/French distributions. PROTOCOL has the same wrong target. |
| Playbook/checklist/skill retain pre-v2.0 rules | Listed contradictions already resolved; adjacent examples still need review | See detailed table below. Do not rewrite the checklist again merely because the external review saw an older copy. |
| PLAYBOOK and VERSIONING deny runner/package/evaluator availability | Already resolved | Both explicitly include the CLI, package, and validation; manual review is distinguished from automation. |
| PROTOCOL uses a sibling robopsych checkout, fixed IDs, one judge | Partly resolved | Commands use in-repository `bdk`, no sibling checkout, and require two judge families with saved-output rejudging. Examples still hard-code target/judge IDs, including rejudge commands. Run count/seed policy is deferred rather than fixed. |
| skill/SKILL.md YAML is unparseable | Already resolved | Both frontmatters parse, descriptions are 349 characters, and CI runs the metadata test. Legacy directory-name compliance remains a separate issue below. |

### Each listed protocol contradiction

| Reported contradiction | Current finding |
| --- | --- |
| Mandatory two alternatives | Resolved in playbook steps/template, human checklist, and generated skill contract: zero, one, or several credible alternatives. |
| Fixed evidence source ladder / 3-2-1-0 scoring | Resolved in those intervention documents: method, relevance, independence, corroboration, recency, provenance; qualitative calibration bands. |
| Universal falsifiability requirement | Resolved: claim-specific checks; normative/interpretive claims are not rejected for failing an empirical test. |
| High stakes or dissent alone trigger Full | Resolved in playbook gates: a claim signal is required, Light defaults, domain alone never forces Full. |
| Preserve verdict unless new evidence, ignoring own errors | Resolved: reassess errors and corrected premises/scope/facts before holding calibration. |
| Checklist calls the user irrational or a cult member | Resolved: non-diagnostic introduction and qualitative calibration bands; no such current checklist labels. |
| Skill always requires exact Full template | Resolved: generated contract contains Light output and Full only when warranted. |
| No package/runner/evaluator | Resolved: current product/reference-implementation boundary is explicit. |

The quoted obsolete phrases searched in tracked Markdown do not recur as
instructions in the named intervention documents. Cult-related vocabulary
remains in protected author prose and explicitly rejected bad-response examples;
those are not instructions to insult a user. A future coherence scan must
distinguish prohibited prescriptions from quotations, negations, and this audit.
Existing synchronization and selected prompt assertions do not constitute a
distributed-Markdown semantic coherence scan.

### Additional coherence issues for later review

- `skill/examples/playbook_scenarios.md:27-33` allows Light for a declared
  non-trigger humble-exploration case; lines 260-270 allow Light for supported
  dissent with no mismatch. Both should answer normally under Gate 1.
  The portable copy inherits the same examples. Several other sketches select
  modes without showing the two-gate decision; review context rather than
  mechanically replacing every Full mention.
- `framework/diagnosis/falsifiability.md:21-36` prescribes a fixed diagnostic
  source hierarchy with human judgment highest. It is not the obsolete
  peer-review ladder from the brief, but its source-ranking language merits
  explicit reconciliation with evidence-quality guidance. The warning against
  treating model self-report as ground truth should be preserved.
- `docs/agentic-plan-execute-verify.md:7-9,194-195` still tells readers to keep
  evaluators/provider-specific code downstream, whereas BDK now includes
  reference implementations. Clarify external orchestration versus bundled
  reference tooling without changing intervention behavior.
- `docs/migration.md` describes historical v5.0/v5.1 diagnostic revisions under
  a 3.0 product tree. Identify the historical version track, not a new release.

## Legacy-name occurrence ledger

Search: case-insensitive `git grep -n -i -E
'robopsych|robopsychology|prompts/prompt-agent\.md|scripts/apply_kit\.py'`
over all baseline tracked files. There are 36 matching lines for `robopsych`
(including substrings) and nine for `robopsychology`, which overlap.
All matching locations follow; no private transcript excerpts are reproduced.
Line numbers refer to the baseline, not to this report.

| Locations | Interpretation / later handling |
| --- | --- |
| `CHANGELOG.md:11`; `README.md:105`; `VERSIONING.md:64` | Required alias/deprecation history; retain. |
| `docs/RELEASING.md:16`; `validation/closed-loop/PROTOCOL.md:90` | Alias compatibility smoke check / note; do not remove executable support. |
| `docs/deployment-contexts.md:9`; `docs/related-work.md:26` | Old product-name migration wording; replace in maintained docs if no longer useful. |
| `framework/diagnosis/guide.md:555`; `framework/diagnosis/method.md:148` | Asimov's fictional concept, not a missing package path; distinguish attribution from stale branding. |
| `pyproject.toml:49`; `src/bdk/cli.py:49` | Supported alias and help-only deprecation notice; retain in 3.x. |
| `src/bdk/security.py:15`; `tests/conftest.py:38`; `tests/test_providers.py:145` | Existing `ROBOPSYCH_ALLOW_INSECURE_BASE_URL` compatibility setting and isolation/tests; renaming is not a documentation-only cleanup. |
| `tests/test_cli_alias.py:20,41,78,80`; `tests/test_release_metadata.py:42` | Alias regression coverage; retain. |
| `validation/diagnosis/reproducible/case-01-sycophancy/artifacts/report.md:1,224,228`; same case `artifacts/session.json:33` | Historical report branding, command, URL, and captured response; preserve verbatim. |
| `validation/diagnosis/reproducible/case-02-host-vs-model/artifacts/report_A_diagnosed.md:1,310,314`; same case `artifacts/session_A.json:43` | Historical report/response; preserve verbatim. |
| `validation/diagnosis/reproducible/case-03-ratchet-coherence/artifacts/report.md:1,131,186,445,611,1708`; same case `artifacts/session.json:14,34,44` | Historical commands, response text, branding, and URL; preserve verbatim. |

`prompts/prompt-agent.md` and `scripts/apply_kit.py` have **zero** tracked
occurrences and do not exist. Do not reintroduce them to "repair" old references.
The current public agent path is `prompts/intervention/prompt-agent.md`;
the brief's `prompts/intervention/agent.md` does not exist either.

### Other absent-path references and false positives

The offline link checker found no broken relative Markdown file/directory
destinations. An additional read-only scan of inline-code path strings found
the following absent or context-dependent paths. This extends, but does not
replace, the checker: literal commands, generated outputs, remote URLs, and
heading anchors require separate interpretation.

| Reference locations | Finding / disposition |
| --- | --- |
| `docs/plans/2026-05-26-diagnostic-engine-v1.0.md:262` | Proposed `artifacts/runs/score_runN.json` layout is absent; current runner documents `artifacts/run-{i}/`. Historical proposal, not a missing checked-in result. |
| Same plan `:277` | `validation/diagnosis/reproducible/aggregate_runs.py` absent; plan proposes creating it. Do not pretend it exists or execute the plan. |
| Same plan `:327,435` | Case 3 `artifacts/distribution.json` absent; prerequisite measurements remain pending. |
| Same plan `:339`; `validation/diagnosis/reproducible/README.md:42` | Case 3 `cross_judge_agreement.json` is described/proposed but not committed; historical `cross_judge_comparison.json` exists instead. |
| Same plan `:632` | Proposed `.github/workflows/paper.yml` absent. |
| Same plan `:742,744,746` | Proposed `research/diagnosis-paper/announcements/{microblog,linkedin,mastodon}.md` absent. |
| Same plan `:144,387,639` | `cd paper` uses an absent old directory; the paper is under `research/diagnosis-paper/`. |
| Same plan `:656,723`; `:12,146,148,151,619,640,661,762` | Proposed `research/diagnosis-paper/RELEASE_NOTES.md` and built `main.pdf` are absent; not checked-in deliverables. |
| Same plan `:768` | A later verification step assumes the proposed `paper.yml` exists and is green; it does not exist in this baseline. |
| `README.md:141`; `docs/integration.md:23-26,233` | User-created `bdk.toml`, installed skill-relative resource paths, and an example target-project instruction file: intentional, not stale repository paths. |
| Historical plan `:304,501,593`; reproducible README `:48,59`; runner `:14,702` | Context-relative case paths, runner-generated artifacts, or example output layouts; do not invent root-level `artifacts/`. |

This is not a claim that every absent path was deleted: planned outputs may
never have existed. Authored prose, paper contents, and protected artifacts were
not rewritten to make historical names or paths disappear.

## Baseline execution

The initial shell had no `python` or `mypy` command. Its existing global
`pytest` ran on Python 3.14.10: 1,220 passed, two deselected; global ruff lint
and formatting passed. The three missing-command invocations exited 127.
These were environment failures, not repository failures.

After those failures, created an ignored local `.venv` with Python 3.11 and
installed `-e ".[dev]"` as documented, without provider extras. No tracked files
changed. Authoritative baseline environment: macOS, Python 3.11.15,
pytest 9.2.0, ruff 0.17.4, mypy 2.4.1.
All six exact required commands then ran on the unchanged baseline:

| Command | Result |
| --- | --- |
| `pytest -m "not integration"` | PASS, exit 0; 1,220 passed, two integration tests deselected. |
| `ruff check src/ tests/ scripts/` | PASS, exit 0. |
| `ruff format --check src/ tests/ scripts/` | PASS, exit 0; 64 files already formatted. |
| `mypy src/bdk scripts/check_markdown_links.py scripts/sync_prompts.py` | PASS, exit 0; 20 source files. |
| `python scripts/check_markdown_links.py` | PASS, exit 0; 108 Markdown files. |
| `python scripts/sync_prompts.py --check` | PASS, exit 0; no generated drift. |

Command output, with per-file pytest progress omitted:

```text
BASELINE: 6c52da81f37d50dba6318aae5e437a82813b4eb6
Python 3.11.15
collected 1222 items / 2 deselected / 1220 selected
====================== 1220 passed, 2 deselected in 9.74s ======================
pytest exit=0
All checks passed!
ruff check exit=0
64 files already formatted
ruff format exit=0
Success: no issues found in 20 source files
mypy exit=0
Checked 108 Markdown files: all relative link paths exist.
links exit=0
Intervention prompts are synchronized.
sync exit=0
```

Final baseline `git status --short` produced no output; comparison against
fetched `origin/main` was empty. These results establish a local Python 3.11
baseline, not a new Linux/Windows or full CI run. The separate coverage,
dependency-audit, publication, and base-install jobs were not run here.

Additional offline execution: both skill frontmatters parsed, all 17 scenario
YAML files loaded, and `python validation/diagnosis/agreement.py` reported
24 synthetic claim-count fixtures with judge-human/judge-judge agreement and
kappa **N/A**. Those are not measured intervention effects.

## Remaining work, defaults, and handoff

Phase 1 should preserve resolved wording and target actual residual drift,
add a distributed-document coherence test, document architecture/provenance,
and mark generated files. Existing CI already parses both skill YAML blocks,
requires nonempty names/descriptions, and limits descriptions to 1,024
characters. It checks directory/name equality **only for `skills/`**.
The legacy `skill/SKILL.md` declares `baloney-detection-kit`, not `skill`.
Therefore requiring literal name equality for both paths conflicts with
preserving the legacy path and identical generated frontmatter. Make that
compatibility exception explicit in review rather than silently renaming the
public path or the installed skill.

Phase 2 still needs the newcomer README (currently 436 lines), source-install
guidance, single check command, first-contribution flow, docs index, English
CONTEXT, scenario documentation/JSON Schema and approved directory split,
community files/forms, roadmap, and correct issue links.
Neither `CODE_OF_CONDUCT.md` nor a tracked `CODEOWNERS` exists.
Translation deferral links in `docs/CONTEXT.md:48` and
`prompts/intervention/README.md:51` incorrectly target issue 10 instead of 11.
Link existence checks cannot detect a valid URL pointing to the wrong issue.

Phase 3 can reuse shared scenario preflight, sequential history/persistence,
fixed-capture rejudging, family metadata, synthetic fixtures, and nominal
Cohen kappa. Still missing are the fourth question-only arm, fixed
preregistration counts/hash/analysis, balanced/matched cases, actual tool
environments, adaptive 5/25-turn pressure and long-history variants,
judge-presentation normalization, kappa intervals, human calibration template
and result cards, Bloom seeds, and a complete simulated-provider experiment
entry point exercised in CI. Existing mocked unit coverage is not that
end-to-end experiment. No result should be backfilled from those mocks.

For phase 4, the actual agent prompt already covers neutral intake, tools,
review separation, and verification, but does not explicitly require checking
an order's embedded premise against the environment before acting or a
diminishing-return stop. The integration doc is a conceptual downstream
pattern, not installed hooks. The supplied 2026 research references and current
runtime hook formats have not been independently reviewed in phase 0;
no claims from their summaries are adopted as verified evidence.

Apply the brief's defaults: retain `skill/` and generated `skills/` throughout
3.x; announce any unification for 4.0; retain root prose/research locations;
translate CONTEXT; move scenarios only in the dedicated later block with a
changelog entry. The requested separate checklist-scoring rewrite is already
present in main; do not duplicate it.

The three explicit approval gates remain unchanged: **no merging candidate
prompt-v2.1, no real-model runs without approved models/budget, and no repository
settings changes**. Future behavioral proposals belong in a draft PR, not the
cleanup PRs. Phase 5 contribution issues may be drafted under the authorized
`docs/plans/issues/` path if remote issue creation is not authorized.

This audit is delivered as its own documentation-only PR before phases 1-5.
No behavior changed, so neither CHANGELOG nor `prompt-v2.0` changes in phase 0.
Human review of this audit and later behavior/translation proposals is still
pending; local software checks do not substitute for that review.
