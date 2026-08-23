# Versioning Model

Robopsychology now separates three tracks that used to be easy to conflate.

| Track | What changes it | Example artifact |
|-------|-----------------|------------------|
| Framework spec | Changes to the diagnostic method, rules, taxonomy, ratchet, or epistemic limits | `framework/*.md` |
| Prompt toolkit | Changes to prompt semantics, prompt cards, or the machine-readable catalog | `prompts/`, `src/robopsych/data/prompts.yaml` |
| Reference CLI | Changes to automation, providers, output formats, packaging, or API integrations | `src/robopsych/`, `pyproject.toml` |

## Practical rule

- If a change affects how a human diagnoses behavior manually, it is a framework
  or prompt-toolkit change.
- If a change affects how `robopsych` automates an existing method, it is a
  reference CLI change.
- If a change only fixes package publication, provider routing, or command-line
  behavior, it should not be described as a framework evolution.

## Changelog convention

`CHANGELOG.md` should group unreleased items under:

- **Framework**
- **Prompt toolkit**
- **Reference CLI**
- **Validation**
- **Packaging/metadata**

The Python package version remains the CLI implementation version. The canonical
essay and framework documents are the stable reference for the method.
