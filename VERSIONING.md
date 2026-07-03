# Behavior Versioning

BDK is a framework and prompt distribution. It has no package API, but it still
has behavior that users may embed in assistants, classrooms, team rituals, or
evaluation recipes. Version changes should describe behavior, not code.

## What to pin

If you use BDK in a reproducible setting, record:

1. repository commit or release tag;
2. prompt file used, such as `ROOT_PROMPT.md` or `prompts/prompt-agent.md`;
3. any local edits;
4. model and runtime, if relevant;
5. date of use.

## Change categories

| Change type | Examples | Compatibility expectation |
|-------------|----------|---------------------------|
| **Patch wording** | Typos, clearer examples, less awkward phrasing | Same behavior |
| **Prompt tuning** | Better trigger wording, tone calibration, shorter output guidance | Similar behavior, but outputs may shift |
| **Behavior change** | New trigger, new mode, changed high-stakes boundary, changed output contract | Re-test before adopting |
| **Breaking behavior change** | Removing a protocol step, reversing a trigger rule, changing the framework loop | Treat as a new major behavior |

## Current behavior contract

The current contract is:

**Trigger -> Mode -> Protocol -> Output -> Review**

The framework should:

- add friction before validating weak, inflated, high-stakes, suppressed,
  against-consensus, or novel-sounding claims;
- avoid over-triggering on casual creativity, preferences, settled lookups, and
  humble exploration;
- preserve useful re-framings without flattering unsupported novelty;
- say when research tools or evidence are unavailable;
- avoid unsafe guidance in material-risk domains;
- remain a readable prompt/playbook rather than a toolkit, SDK, benchmark, or
  evaluator.

## Suggested release labels

Use release notes or tags like:

- `prompt-v1.0`: first stable prompt behavior;
- `prompt-v1.1`: compatible prompt tuning;
- `prompt-v2.0`: behavior contract changed.

This repo can stay lightweight: tags and release notes are enough unless a
downstream product needs stricter governance.

