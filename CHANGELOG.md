# Changelog

All notable changes to Baloney Detection Kit are documented here. The project
uses Semantic Versioning for the integrated distribution and explicit behavior
versions for prompt contracts.

## [Unreleased]

### Added

- Compatibility alias for the previous diagnostic CLI command.

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
