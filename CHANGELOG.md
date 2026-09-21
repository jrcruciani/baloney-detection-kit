# Changelog

All notable changes to Baloney Detection Kit are documented here. The project
uses Semantic Versioning for the integrated distribution and explicit behavior
versions for prompt contracts.

## [Unreleased]

### Added

- Compatibility alias for the previous diagnostic CLI command.

### Intervention

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
