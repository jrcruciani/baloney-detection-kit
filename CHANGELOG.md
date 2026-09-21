# Changelog

All notable changes to Baloney Detection Kit are documented here. The project
uses Semantic Versioning for the integrated distribution and explicit behavior
versions for prompt contracts.

## [Unreleased]

### Validation

- Add an explicitly unmeasured closed-loop results inventory linked to the
  original pending findings; require two judge families, paired agreement and
  blinded human calibration where available before outcome claims.
- Add stdlib offline Cohen kappa with shared-item coverage and undefined-value
  handling. The default identifies synthetic claim-count fixtures and reports
  unavailable empirical judge/human agreement; tests are not calibration data.
- Add a shared validated scenario loader, eight intervention-enabled negative
  cases, two explicitly positive cases, and additive `crosscheck --scenario` /
  `--scenarios` reports with limited header-proxy firing metrics. Preserve
  single-task A/B behavior; directness/hedging remain human-review-only.
- Add real sequential user turns, isolated Inferred stance/flip analysis,
  evaluated stability/reopening expectations, and private report/session
  capture with interrupted-conversation resume. Include a synthetic pressure
  and corrected-premise fixture, not a real study.
- Add `bdk rejudge` to evaluate captured outputs without target reruns and keep
  JSON report stdout free of progress formatting. No canonical intervention
  prompt text, behavior marker, preregistered prediction, or historical evidence
  is changed. No live runs were performed; empirical and human review are pending.

### Added

- Compatibility alias for the previous diagnostic CLI command.
- **Additive CLI tooling:** support validated TOML model aliases in user and
  current-directory config, with local per-alias precedence and resolved IDs
  used for model/judge calls and persisted provenance. Keep raw-model library
  APIs, existing defaults, and saved-session model identity unchanged.
- Add exact `bdk apply --format json` output and language-aware `bdk apply --list`
  (plain or JSON), deriving behavior versions from packaged prompt markers.
  Plain retrieval preserves literal Markdown; file output uses the same
  representation and private permissions. Prompt content and behavior markers
  are unchanged by this CLI addition; no live model validation is implied.

### Intervention

- **Additive BEHAVIOR distribution:** add Spanish compact/full translations,
  self-contained `ROOT_PROMPT.es.md`, synchronized package mirrors, and
  `bdk apply <variant> --lang es`. English stays canonical and the default;
  unsupported languages and unavailable variants fail explicitly without
  fallback. Keep English section/output labels for machine parsing and retain
  `prompt-v2.0` alignment. **Human Spanish-language review and maintainer
  behavior/version sign-off are required before merge**; translation can change
  model behavior even with an unchanged intended contract. New tests cover
  structure, synchronization, and CLI wiring, not semantic quality or efficacy.
  No live validation was performed, and historical evidence is unchanged.
  Portuguese/French remain deferred in
  [#10](https://github.com/jrcruciani/baloney-detection-kit/issues/10);
  Spanish skill/plugin copies are out of scope.
- **Distributed BEHAVIOR CHANGE, not a mechanical fix:** refine intervention into
  two gates: require an actual claim signal, then choose a proportionate mode by
  mismatch and consequence. High-stakes domains alone no longer force Full;
  ordinary no-claim questions and the stated exclusions receive normal answers.
  Light has an explicit 3-4-line output; Stabilization corrects its own errors
  and reopens for changed evidence, premises, scope, or facts.
- Make `prompts/intervention/prompt-full.md` canonical and synchronize its exact
  full block into root and skill instructions, its text into the skill prompt,
  and all six variants into packaged mirrors. Preserve wrappers, skill
  frontmatter/resources, claim typing, fitting update methods, evidence-quality
  checks, novelty/truth/importance/usefulness separation, no false balance,
  reviewer critique diversity, high-stakes boundaries, and humility.
- Retain `prompt-v2.0` alignment as explicitly requested for this change, rather
  than silently bumping it. The two-gate/Light-output refinement still requires
  **maintainer behavior/version sign-off before merge** under `VERSIONING.md`;
  retaining the marker is not a claim of unchanged behavior. Record the exact
  commit and prompt for runs. Historical calibration, scientific evidence, and
  preregistration remain unchanged and do not validate these revised prompts.
  New checks are structural/deterministic, not live model-firing validation.

## [3.0.0] - 2026-08-23

### Product

- Establish one BDK lifecycle: detect risk, apply epistemic friction, diagnose
  behavior, and validate outcomes.
- Adopt MIT as the license for the complete integrated distribution.
- Unify documentation, citation metadata, issue tracking, CI, and release
  metadata under `baloney-detection-kit`.

### Intervention

- Package compact, full, high-stakes, agent, reviewer, and second-opinion
  prompts for CLI access through `bdk apply`.
- Keep the `prompt-v2.0` behavior contract as the preventive baseline.

### Diagnosis

- Add the model/runtime/conversation diagnostic split.
- Add 16 diagnostic prompts, prompt cards, manual templates, and a nine-step
  diagnostic ratchet.
- Add cross-model comparison, behavioral A/B tests, coherence analysis,
  scoring, session persistence, and Markdown/JSON reports.

### Validation

- Use one scenario schema across intervention calibration and behavioral
  diagnosis.
- Add reproducible cases, calibration data, and Python 3.11-3.13 CI.

### Packaging

- Add the `baloney-detection-kit` Python distribution and `bdk` executable.
- Keep a temporary executable alias for compatibility with earlier CLI
  installations.
