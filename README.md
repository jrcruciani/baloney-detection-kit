# Baloney Detection Kit

> Epistemic friction, behavioral diagnosis, and validation for AI conversations.

Baloney Detection Kit (BDK) helps practitioners prevent unsupported confidence
amplification, diagnose why an AI response went wrong, and test whether an
intervention improved behavior without making the assistant reflexively
contrarian.

BDK 3.0 has one operating loop:

```text
Detect risk -> Apply friction -> Diagnose behavior -> Validate outcomes
```

## Scope and boundaries

The project is framework-first. Every layer can be used manually with prompts
and templates. The `bdk` Python CLI is a reference implementation for teams that
need repeatable model runs, cross-checks, scoring, and reports.
LLM judges are review aids, not ground truth.
BDK is not a truth oracle, automatic fact-checker, leaderboard benchmark,
orchestrator, or RAG framework.

## What BDK includes

| Layer | Question | Main artifacts |
|---|---|---|
| Detection | Is confidence misaligned with evidence or consequence? | Trigger rules, claim typing, human checklist |
| Intervention | How should the assistant respond before endorsing the claim? | Compact, full, high-stakes, agent, reviewer, and second-opinion prompts |
| Diagnosis | Why did this output emerge? | Model/runtime/conversation split, 16 diagnostic prompts, nine-step ratchet |
| Validation | Did the intervention help, and what did it damage? | A/B cross-checks, coherence analysis, scoring, scenarios, reports |

BDK does not claim to inspect model weights or reveal hidden reasoning.
Diagnostic explanations are hypotheses constrained by observable behavior.
Behavioral probes and human review carry more weight than model self-report.

## Quick start without installing anything

For prevention:

1. Read [`PLAYBOOK.md`](PLAYBOOK.md).
2. Choose a prompt from [`prompts/intervention/`](prompts/intervention/).
3. Use the checklist in [`skill/checklist/`](skill/checklist/).

For diagnosis:

1. Write the expected outcome, constraints, and verification.
2. Identify the observed symptom.
3. Select a card from
   [`prompts/diagnosis/cards/`](prompts/diagnosis/cards/).
4. Label every diagnostic claim as Observed or Inferred.
5. Escalate through the ratchet only when the consequence justifies it.
6. Preserve the transcript in [`templates/diagnosis/`](templates/diagnosis/).

## Reference CLI

Requires Python 3.11 or newer. The base install supports prompts, templates,
and `bdk apply` without any model-provider SDKs:

```bash
pip install baloney-detection-kit
```

For live model runs, install all provider SDKs:

```bash
pip install "baloney-detection-kit[all]"
```

Or install only the provider you need:

| Provider | Install |
|---|---|
| Anthropic | `pip install "baloney-detection-kit[anthropic]"` |
| OpenAI, OpenAI-compatible APIs, Azure Foundry / Azure OpenAI | `pip install "baloney-detection-kit[openai]"` |
| Gemini (Google Gen AI) | `pip install "baloney-detection-kit[gemini]"` |

SDKs load only when their provider is constructed. Set `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, or the corresponding provider credentials, or pass `--api-key`.
Azure Foundry also requires `AZURE_FOUNDRY_API_KEY` and `AZURE_FOUNDRY_ENDPOINT`
(or its chat/GPT-specific endpoint variables).

Set `GEMINI_API_KEY` or `GOOGLE_API_KEY`, or pass `--api-key`. The Gemini
adapter uses `google-genai>=1.0`, with a separate client per provider rather than
global SDK configuration.

For a source checkout (including the example scenarios below), use
`pip install -e .` for the base CLI or `pip install -e ".[all]"` for live runs.
Contributors can use `pip install -e ".[dev]"` to run unit tests without provider SDKs.

CI checks pull requests against any branch, including stacked PRs, on Python
3.11, 3.12, and 3.13. Run the same offline checks locally:

```bash
ruff check src/ tests/ scripts/
ruff format --check src/ tests/ scripts/
mypy src/bdk scripts/check_markdown_links.py scripts/sync_prompts.py
python scripts/check_markdown_links.py
python scripts/sync_prompts.py --check
pytest -m "not integration" --cov=bdk --cov-report=xml --cov-report=term-missing --cov-fail-under=60
```

Use `ruff format src/ tests/ scripts/` to apply formatting. Type checking includes
unannotated function bodies without requiring strict annotations everywhere.
The base-install smoke job separately checks that the CLI works without SDKs.
CI uploads coverage per Python version and runs `pip-audit` against the resolved
development environment in a separate, initially non-blocking job; inspect its
step output and job summary for findings or audit failures. Dependabot checks
Python dependencies and pinned GitHub Actions weekly.

The offline link checker covers tracked and non-ignored new Markdown files
throughout the repository, including images and reference-link definitions.
It checks file and directory paths, accepts URL-encoded paths, fragments and
queries, and skips remote URLs and literal code examples. It does not validate
heading anchors or fetch remote content. Untracked virtual environments and
tool caches are excluded; tracked Markdown is never excluded as tooling.
The [intervention distribution contract](prompts/intervention/README.md#canonical-contract-and-synchronization)
defines the canonical full prompt and wrapper-preserving synchronization.

Retrieve a preventive intervention:

```bash
bdk apply compact
bdk apply high-stakes --output system-prompt.md
bdk apply compact --lang es
bdk apply full --lang es --output system-prompt.es.md
bdk apply compact --format json
bdk apply --list --lang es --format json
```

English (`--lang en`) remains the default for all six variants. Spanish (`es`)
is available only for compact/full, including the self-contained
[`ROOT_PROMPT.es.md`](ROOT_PROMPT.es.md). Unsupported languages and unavailable
variants fail explicitly; they never fall back to English. Spanish prose keeps
English section/output labels for machine parsing. See
[language coverage and review](prompts/intervention/README.md#languages-and-translation-review).

`apply` defaults to plain, exact packaged Markdown, without terminal wrapping or
markup interpretation. `--format json` prints exactly one object with the keys
`variant`, `prompt_version`, `lang`, and `content`; `content` preserves the full
prompt, including Unicode and newlines. The behavior version (currently
`prompt-v2.0`) comes from the prompt's validated marker, not the package version.
`--list` takes no variant and lists only the variants available for `--lang`,
with their versions and language. In JSON mode it returns an array of objects
with `variant`, `prompt_version`, and `lang` (no prompt bodies).
`--output` writes the same selected representation with owner-only permissions
where supported; its confirmation goes to stderr, leaving stdout empty.
Invalid formats, languages, or variant/list combinations fail without writing.

### Model aliases

Pass a raw model ID, or define case-sensitive aliases in `./bdk.toml` or
`~/.config/bdk/config.toml`. Replace these illustrative placeholders with your
actual model IDs before using the aliases:

```toml
[models]
default = "<model-id>"
anthropic = "<anthropic-model-id>"
openai = "<openai-model-id>"
gemini = "<gemini-model-id>"
azure = "azure/<deployment-or-model-id>"
```

The user file is loaded first; the current-directory file overrides individual
aliases and retains other user aliases. There is no parent-directory search or
environment-variable expansion. The only supported top-level table is
`[models]`, containing nonempty alias-to-string mappings without whitespace.
Values are literal raw model IDs, not URLs, credentials, or the reserved name
`default`. Aliases are looked up once: values are never expanded as other aliases.
Keep keys and endpoints in the existing environment variables or CLI flags,
not these files. Both files are validated even when local aliases override user
aliases; malformed TOML/schema, invalid values, and unreadable files fail
explicitly rather than silently falling back.

`--model`, each entry in `compare --models`, `--judge`, and `--coherence-judge`
accept aliases. Resolved IDs reach both provider selection and model requests,
and appear in model/judge report metadata and saved sessions/checkpoints.
`--model default` requires an explicit `[models].default`; it never sends the
literal `default` to an API. Other unconfigured names still pass through as raw
IDs. Omitting `--model` retains the existing CLI default, not the `default` alias.
Provider routing, including Azure deployment handling, is unchanged.

Aliases are CLI-only: Python library APIs still take raw IDs. Resuming a session
uses its saved raw ID without alias lookup, so later config edits cannot retarget
it. Offline `coherence` and `score` analysis likewise leaves historical report
IDs unchanged and does not load alias configuration.

Run diagnosis:

```bash
bdk guided --model "<model-id>"
bdk run 1.2 --model default --response "the suspicious response"
bdk ratchet --scenario scenarios/sycophancy.yaml --model default
bdk compare 1.1 --models anthropic,openai --response "the response"
```

Run behavioral checks and scoring:

```bash
bdk crosscheck --task "Explain the evidence" --model default --judge anthropic
bdk coherence report.json
bdk score report.json
```

Alias-based examples require the [model alias configuration](#model-aliases) above.

## The intervention protocol

First require an actual claim signal: confidence-evidence mismatch, inflated
novelty or importance, endorsement before checks, framing used to evade evidence,
or repeated pressure. Then choose a mode by mismatch and consequence. Full uses:

1. Define and type the smallest reviewable claim.
2. Scope current knowledge and the limits of any search.
3. Separate prior art from truth, importance, and usefulness.
4. State update conditions and assess evidence quality.
5. Compare only credible alternatives and their discriminators.
6. Calibrate the conclusion and recommend one useful next step.

Default to Light's 3-4 lines after a signal; use Full for substantial mismatch or
consequential action needing deeper checks. A high-stakes domain alone never
forces Full. Ordinary no-claim questions and humble exploration need no
intervention. Under repeated pressure, Stabilization first rechecks its own
errors and reopens for changed evidence, premises, or facts. Disagreement with
consensus alone is neither a trigger nor a verdict.

## The diagnostic protocol

BDK separates behavioral hypotheses into three layers:

| Layer | Examples |
|---|---|
| Model | Base-model tendencies, approval-seeking, style defaults |
| Runtime/host | System prompts, policies, tools, memory, workflow rules |
| Conversation | Framing, local assumptions, inferred user preferences |

Five rules keep diagnosis disciplined:

1. Split every diagnosis across model, runtime/host, and conversation.
2. Label substantive claims as Observed or Inferred.
3. Prefer behavioral cross-checks over self-report.
4. Use diagnostic depth as a coherence ratchet.
5. Define baseline intent before diagnosing when possible.

The complete method lives in [`framework/diagnosis/`](framework/diagnosis/).

## Validation

BDK ships two complementary validation surfaces:

- [`validation/diagnosis/`](validation/diagnosis/) contains reproducible
  diagnostic cases, calibration material, and runner scripts.
- [`validation/closed-loop/`](validation/closed-loop/) tests preventive BDK
  prompts against control and generic-critical conditions.

The scenario format is shared by the CLI and the validation recipes:

```yaml
name: example
system_prompt: |
  Optional intervention prompt.
task: |
  Task sent to the target model.
expectation: >
  Observable behavior expected from the response.
recommended_path:
  - "1.2"
  - "3.2"
```

LLM judges are review aids, not ground truth. Any product claim should report
cases, models, prompts, run counts, reviewer process, uncertainty, and adverse
effects.

## Repository map

```text
baloney-detection-kit/
├── PLAYBOOK.md                    Preventive operating protocol
├── ROOT_PROMPT.md                 Self-contained intervention prompt
├── docs/
│   ├── agentic-plan-execute-verify.md  Agentic runtime integration pattern
│   ├── deployment-contexts.md     Adoption and deployment guidance
│   ├── related-work.md            Intellectual lineage and positioning
│   └── second-opinion-operational.md  External-review practice notes
├── framework/
│   └── diagnosis/                 Behavioral diagnostic method
├── prompts/
│   ├── intervention/              Preventive prompt variants
│   └── diagnosis/                 Diagnostic cards and catalog
├── skill/                         Runtime-friendly agent skill
├── src/bdk/                       Reference CLI and analysis engine
├── tests/                         Unit and integration tests
├── scripts/                       Offline repository checks
├── scenarios/                     Runnable scenario examples
├── templates/diagnosis/           Human diagnostic worksheets
├── validation/
│   ├── closed-loop/               Intervention calibration
│   └── diagnosis/                 Diagnostic validation
└── research/diagnosis-paper/      Research scaffold
```

## Evidence status

BDK is a testable intervention and diagnostic method, not a proven treatment,
automatic fact-checker, benchmark, or truth oracle. The current repository
contains versioned behavior contracts and validation recipes. Results must be
interpreted within the tested cases, models, prompts, and review criteria.

## Security and privacy

Generated reports and session files can contain complete prompts, model
responses, and private transcripts. Treat them as sensitive. The CLI validates
custom base URLs before sending API keys and marks live-provider tests as
integration tests.

For vulnerability scope and private reporting guidance, see
[`SECURITY.md`](SECURITY.md). Do not publish vulnerabilities or private
transcripts in ordinary issues.

## Contributing and reporting

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for development checks, behavior-version
review, and AI-assisted contributions. Use
[New issue](https://github.com/jrcruciani/baloney-detection-kit/issues/new/choose)
for bug and adverse-effect reports; use existing issues or a blank issue for
questions (Discussions are not enabled).

## Versioning

BDK 3.0 unifies the framework, prompt distributions, diagnostic engine, and
validation surfaces under one product version. See
[`VERSIONING.md`](VERSIONING.md) and [`CHANGELOG.md`](CHANGELOG.md).

## License

MIT. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

Use it, fork it, embed it, test it, and report where it over-validates,
over-triggers, becomes stubborn, creates false balance, or reduces usefulness.
