# Agent skill integrations

BDK's preventive skill is **advisory instruction text**, not a security boundary,
automatic fact-checker, or proof of effectiveness. Runtime discovery makes the
skill available; it does not prove that a model invokes it or follows its gates.
Explicit invocation requests the skill; it does not require Full mode. The
unchanged skill still checks for an actual claim signal before choosing a
proportionate mode, including answering normally when no intervention is needed.

## What to copy

Use the complete generated
[`skills/baloney-detection-kit/`](../skills/baloney-detection-kit/) directory,
not just `SKILL.md`. The legacy [`skill/`](../skill/) remains the editable
compatibility source and retains its original repository-relative links.
Copying only that legacy directory omits some of its dependencies.

The portable directory contains 12 files:

| Content | Installed paths |
|---|---|
| Skill entry point | `SKILL.md` |
| Drop-in prompt | `prompts/critical_investigation_mode.txt` |
| Checklists | `checklist/seven_questions.md`, `checklist/review_rubric.md` |
| Examples | `examples/case_saussure.md`, `examples/complete_conversations.md`, `examples/playbook_scenarios.md` |
| Required source resources | `resources/PLAYBOOK.md`, `resources/prompts/intervention/prompt-full.md`, `resources/docs/second-opinion-operational.md` |
| Attribution | `LICENSE`, `NOTICE` |

All required resources are self-contained; no symlinks, Python package, model
SDK, credentials, hooks, or executable tools are needed to read the skill.
Optional links to the source repository's scope, related work, and generator
remain HTTPS references, not installed dependencies or instructions to run code.
These `blob/main` links track current repository documentation; pin a checkout
commit when reproducing the bundled text.

This is an English skill. The existing English and Spanish root prompts and
CLI prompt variants remain separate; no Spanish skill is generated.

## Choose one installation scope

Project skills belong to a target repository; commit them there only if you want
to share them with its collaborators. Personal skills live in your home directory
and can apply across local projects. Avoid installing duplicate copies under
several discovered directories in the same runtime.

| Runtime | Project skill roots | Personal skill roots |
|---|---|---|
| GitHub Copilot CLI | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` |
| Claude Code (plain skill) | `.claude/skills/` | `~/.claude/skills/` |
| Cursor | `.agents/skills/`, `.cursor/skills/` | `~/.agents/skills/`, `~/.cursor/skills/` |

Append `baloney-detection-kit/` to a root above. Cursor also documents Claude
compatibility directories, including `.claude/skills/` and `~/.claude/skills/`.
Local personal skills are not automatically available in every remote/cloud
environment; follow the runtime's documentation for that environment.

**Plain repository-root `skills/` is a plugin distribution convention, not an
arbitrary directory that all runtimes discover.** Cloning this repository alone
does not install its skill. The `.claude-plugin/plugin.json` manifest is for
Claude Code, not a Copilot or Cursor marketplace listing.

## Copy instructions

Review a trusted checkout (preferably a recorded commit) of
[`jrcruciani/baloney-detection-kit`](https://github.com/jrcruciani/baloney-detection-kit).
Run the copy commands below from that checkout's root. Replace the absolute
project path with your target repository, not this distribution's `skills/`
directory. The commands deliberately require a fresh destination: if it already
exists, stop and review it rather than merging folders and leaving stale files.
For updates, review the new checkout and replace the entire old copy yourself.

### GitHub Copilot CLI

Project copy (Bash):

```bash
target="/absolute/path/to/project/.github/skills/baloney-detection-kit"
test ! -e "$target" && mkdir -p "$(dirname "$target")" && cp -R skills/baloney-detection-kit "$target"
```

For a personal copy, use this target with the same copy command instead:

```bash
target="$HOME/.copilot/skills/baloney-detection-kit"
test ! -e "$target" && mkdir -p "$(dirname "$target")" && cp -R skills/baloney-detection-kit "$target"
```

Start Copilot CLI in the target project, or enter these commands **inside an
existing interactive CLI session**:

```text
/skills reload
/skills info baloney-detection-kit
```

The info command lets you check the discovered location. To explicitly request
the skill, enter a prompt such as:

```text
Use the /baloney-detection-kit skill to assess this claim: [claim and evidence].
```

Copilot can also select it from its description when relevant. That selection is
model/runtime-dependent, not guaranteed by installation. See the official
[Copilot skill concepts](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
and [CLI skill instructions and commands](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills).

### Claude Code: copied skill

Project copy (Bash):

```bash
target="/absolute/path/to/project/.claude/skills/baloney-detection-kit"
test ! -e "$target" && mkdir -p "$(dirname "$target")" && cp -R skills/baloney-detection-kit "$target"
```

For a personal copy instead:

```bash
target="$HOME/.claude/skills/baloney-detection-kit"
test ! -e "$target" && mkdir -p "$(dirname "$target")" && cp -R skills/baloney-detection-kit "$target"
```

Start Claude Code in the target project. Explicitly invoke the plain skill with:

```text
/baloney-detection-kit Assess this claim: [claim and evidence].
```

Claude may also load it when its description matches the task. The full
[Claude Code skills guide](https://code.claude.com/docs/en/skills) documents
scope, discovery, supporting files, and explicit versus model invocation.

### Claude Code: repository as a plugin

This is an alternative to copying a plain skill, not an additional required
installation. The repository's
[`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json) supplies the
`baloney-detection-kit` namespace and distribution version `3.0.0`.
It relies on default plugin discovery of `skills/<name>/SKILL.md`; it declares
no hooks, commands, agents, MCP/LSP servers, tool permissions, or dependencies.
The behavior marker remains `prompt-v2.0`, independently of the product version.

With Claude Code already installed, the documented validation and session-local
loading commands are:

```bash
claude plugin validate /absolute/path/to/baloney-detection-kit
claude --plugin-dir /absolute/path/to/baloney-detection-kit
```

Then use the **namespaced** invocation in that session:

```text
/baloney-detection-kit:baloney-detection-kit Assess this claim: [claim and evidence].
```

`--plugin-dir` loads a local plugin for that session; it is not a persistent
marketplace installation. Use the copied-skill instructions above for simple
project or personal persistence. Claude's separate marketplace installation
system supports user (default), project, and local scopes, but this repository
does not publish a marketplace here; do not infer an install command or listing
from the manifest alone.

See the official [plugin creation guide](https://code.claude.com/docs/en/plugins)
for `--plugin-dir` and namespacing, and the
[plugin reference](https://code.claude.com/docs/en/plugins-reference) for the
manifest schema, default directories, validation, and installation scopes.
These commands are reference instructions; repository checks do not launch or
install a runtime plugin.

### Cursor

Project copy (Bash):

```bash
target="/absolute/path/to/project/.cursor/skills/baloney-detection-kit"
test ! -e "$target" && mkdir -p "$(dirname "$target")" && cp -R skills/baloney-detection-kit "$target"
```

For a personal copy instead:

```bash
target="$HOME/.cursor/skills/baloney-detection-kit"
test ! -e "$target" && mkdir -p "$(dirname "$target")" && cp -R skills/baloney-detection-kit "$target"
```

Open the target project in Cursor and start a fresh Agent session. In **Customize
> Skills**, check the discovered skill. Type `/` in Agent chat and select
`baloney-detection-kit` to explicitly attach it to a message, then provide the
claim and evidence. Cursor can also select skills from their descriptions.

This is a filesystem skill copy, not a Cursor plugin install. Cursor's
repository/marketplace plugin import has its own manifest requirements; the
Claude manifest does not satisfy those. See the official
[Cursor skills guide](https://cursor.com/docs/skills) for directories,
discovery, slash invocation, and cloud/personal-skill limitations.

### Windows (PowerShell)

The same full directory works without symlinks. From the source checkout, set
`$target` to the desired project root from the table above (this example uses
Copilot), or to a personal path such as
`"$HOME/.copilot/skills/baloney-detection-kit"`:

```powershell
$target = "C:/path/to/project/.github/skills/baloney-detection-kit"
if (Test-Path -LiteralPath $target) { throw "Destination exists; review before replacing it." }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
Copy-Item -LiteralPath "skills/baloney-detection-kit" -Destination $target -Recurse
```

For Claude or Cursor, change the destination to the corresponding table entry;
the copied files and runtime invocation steps are the same.

## Optional repository instruction snippets

These are examples to review and paste into **your target project**, not new
always-on files in BDK. They refer to the Copilot project-copy path above; adjust
the path if you chose another root. A reference is not installation, and an
always-on instruction is not the same as conditional skill discovery.

Example in a root `AGENTS.md`:

```markdown
When a task calls for claim/evidence review, consult the
[BDK skill](.github/skills/baloney-detection-kit/SKILL.md).
Follow its two gates; do not force Full mode or intervene without a claim signal.
Treat its guidance as advisory, not as a security control or proof of correctness.
```

Example in `.github/copilot-instructions.md` (path relative to that file):

```markdown
For claim/evidence review, use the
[baloney-detection-kit skill](skills/baloney-detection-kit/SKILL.md).
Keep its no-intervention cases and proportional modes; do not equate discovery
or model agreement with verified evidence.
```

## Maintainer synchronization and review

Edit the legacy skill and canonical sources, then run:

```bash
python scripts/sync_prompts.py
python scripts/sync_prompts.py --check
python scripts/check_markdown_links.py
pytest -m "not integration" tests/test_prompt_sync.py tests/test_skill_frontmatter.py tests/test_skill_distribution.py
```

The generator copies every legacy skill file, adds the explicit local resources,
and rewrites only the distribution paths. The generated tree is never an input.
Check mode reports missing, changed, or obsolete files without writing; normal
mode removes obsolete files only in `skills/baloney-detection-kit/`. Do not keep
manual edits there. Regeneration is idempotent and preserves existing root and
packaged prompt mirrors byte-for-byte when their sources have not changed.

Offline tests cover inventory, byte synchronization, path correction after
isolated copying, frontmatter, behavior markers, and the minimal manifest
contract. They do not prove runtime discovery, automatic firing, model behavior,
or efficacy. Runtime smoke checks require a separate, authorized manual review;
no live/model calls are part of generation. Preserve human review gates for
behavior and translation changes inherited from other layers.

Before a distribution release, include `.claude-plugin/plugin.json` in the
[version metadata checklist](../VERSIONING.md). Topic badges in the README are
neutral subject labels; repository topics remain maintainer settings. No release,
package publication, marketplace submission, or DOI registration is implied.
