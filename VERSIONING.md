# Versioning

BDK versions the complete distribution while preserving explicit prompt
behavior contracts.
See the README's [Scope and boundaries](README.md#scope-and-boundaries) for
what the distribution does and does not cover.

## Product version

Distribution releases use `vX.Y.Z` labels, such as `v3.0.0`; package metadata
stores the corresponding `X.Y.Z` version.

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
`CITATION.cff`, `.claude-plugin/plugin.json`, and release notes. Keep plugin
metadata aligned when preparing a distribution release; its presence does not
mean a release or marketplace listing has been published.
See [`CHANGELOG.md`](CHANGELOG.md) for the
distribution's release history.

## Prompt behavior version

Prompt behavior labels use `prompt-vX.Y`, such as `prompt-v2.0`. They identify
behavior contracts, not distribution releases, and evolve independently of the
product version.

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
