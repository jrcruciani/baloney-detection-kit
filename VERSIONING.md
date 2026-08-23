# Versioning

BDK versions the complete distribution while preserving explicit prompt
behavior contracts.

## Product version

The product version covers:

- framework and terminology;
- preventive and diagnostic prompts;
- Python package and CLI;
- scenario and report formats;
- validation recipes and packaged data.

Semantic Versioning applies:

- **Patch:** fixes that preserve public behavior and formats.
- **Minor:** backward-compatible commands, prompts, providers, or reports.
- **Major:** changed behavior contracts, removed commands, incompatible scenario
  or report formats, or material method changes.

The version appears in `pyproject.toml`, `src/bdk/__init__.py`,
`CITATION.cff`, and release notes.

## Prompt behavior version

Prompt changes can alter model behavior without changing a Python API. A
reproducible run must record:

1. product release or commit;
2. prompt file and behavior version;
3. local edits;
4. model and runtime;
5. date, run count, and seed policy where available.

The preventive baseline in BDK 3.0 is `prompt-v2.0`:

```text
Trigger -> Mode -> Protocol -> Output -> Review
```

A new trigger, mode, protocol step, high-stakes boundary, or output contract
requires explicit behavior-version review even when the package change would
otherwise be minor.

## Compatibility

The canonical executable is `bdk`. The legacy diagnostic executable remains an
alias during the BDK 3.x compatibility window. New integrations must not depend
on that alias.
