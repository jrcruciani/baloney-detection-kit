# Robopsychology Paper v1.0 — Implementation Plan

> **For the implementing agent:** This plan takes the paper at
> `paper/main.tex` (HEAD on `main`, repo `jrcruciani/robopsychology`)
> from its current working-draft state (16 `\todo{}` markers, 3
> placeholder appendices, point-estimate validation numbers) to a
> publishable v1.0 suitable for a Zenodo DOI release and arXiv
> cs.CY submission. Use `subagent-driven-development` patterns: one
> task at a time, TDD where applicable, commit per task, verify before
> moving on.

**Goal:** Produce `paper/main.pdf` with zero `\todo{}` markers, fully
inlined appendices, $\bar{x}\pm s$ validation numbers from N≥5/10
runs, and cross-family judge agreement — then tag `paper-v1.0`,
release to Zenodo for DOI, and submit to arXiv cs.CY.

**Architecture:** Three workstreams that mostly parallelize but
converge at Task 19 (final PDF build):

1. **Empirical closure (Tasks 1–6):** Close GH issues #10 (N runs) and
   #8 (cross-family judge). These produce the *numbers* that go into
   §05.
2. **Paper completion (Tasks 7–16):** Fill in the 16 `\todo{}`
   markers using committed artifacts and `src/` source. No new
   research, just exposition.
3. **Release (Tasks 17–22):** Build, internal review, tag, Zenodo
   release, arXiv submission.

**Tech Stack:** Python 3.11+, pytest, LaTeX (pdflatex + bibtex or
latexmk), `robopsych` CLI (`pyproject.toml` already configured),
GitHub Actions for CI, Zenodo GitHub integration for automated DOI.

**Inference backend:** Azure AI Foundry (the author is FTE Microsoft
with internal cost-free access). All target and judge calls in
Workstream 1 go through Foundry endpoints — not the public Anthropic
/ OpenAI / Gemini APIs. This requires extending
`src/robopsych/providers.py` with an `AzureFoundryProvider` before
any Workstream 1 run (Task 1.5 below). Concrete model deployment
names depend on the user's Foundry project; the agent will discover
them via `az ai foundry` CLI or the Foundry portal before Task 2.

Recommended deployment matrix (subject to availability in the
user's Foundry project):

- **Target (Case 3 headline):** `claude-sonnet-4-5` via Anthropic
  on Foundry marketplace.
- **Primary judge (Case 3 headline):** `claude-opus-4-5` via
  Anthropic on Foundry marketplace.
- **Cross-family judges (issue #8):** `gpt-5` (Azure OpenAI) and
  `gemini-2.5-pro` (Google on Foundry marketplace).

If any of these is NOT deployed in the user's Foundry project, the
agent must (a) check with the user before deploying it (Foundry
marketplace subscriptions can have organizational gates) and (b)
fall back to the closest in-family substitute documented in the
final paper.

**Constraints (non-negotiable):**

- Vocabulary: keep the "robopsychology / behavioral diagnostics"
  framing the paper currently uses. **Do NOT introduce
  Calvin/Deckard/Voight-Kampff adversarial framing** — the author
  explicitly rejected it as anti-pattern (see `CONTEXT.md`). If you
  find residue of that framing in any section, flag it in a comment
  and stop, do not auto-rename.
- License: CC BY 4.0 (already in `LICENSE`). Do not change.
- Author identity in PDF: "JR Cruciani" only. Never substitute legal
  name.
- All numbers in §05 and the abstract must be backed by a committed
  artifact under `validation/reproducible/<case>/artifacts/`. No
  hand-typed values.
- Frequent commits: one task = one commit minimum. Conventional
  Commit prefixes (`feat:`, `docs:`, `test:`, `chore:`, `fix:`).
- Branch strategy: create `paper-v1.0` from `main`, do all work
  there, open PR at the end, merge before tagging.

**Open GitHub issues to close:**

- #8 — Cross-family judge validation for Case 3 — inter-rater reliability
- #10 — Score distribution per case across N runs (not single-run)

---

## Workstream 0 — Identity prerequisite

### Task 0: Create ORCID iD for the author

**Objective:** Generate the ORCID iD that Zenodo will pin to the
deposit (Task 20 needs it).

**Files:**

- Create: `.author-identity` (local-only, gitignored) with the
  ORCID iD once registered
- Modify: `.gitignore` to add `.author-identity` if not already
  ignored

**Steps:**

1. Visit https://orcid.org/register in a browser (this is the only
   step the agent cannot fully automate — registration sends an
   email confirmation).
2. Register with: **Given name** "JR", **Family name** "Cruciani",
   **Primary email** the user's preferred public email
   (`jrcruciani@gmail.com` per the paper's `\author{}` block).
   **Do NOT use the legal name** — the user's public identity is
   always "JR Cruciani".
3. Confirm via email link.
4. From the ORCID dashboard copy the iD (format
   `0000-000X-XXXX-XXXX`).
5. Write the iD to `.author-identity` (one line, no quotes). Add
   `.author-identity` to `.gitignore`.
6. Commit: `chore: gitignore author-identity file`.

**Verification:** `cat .author-identity` returns a valid ORCID iD
matching the regex `^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$`. The iD
resolves at `https://orcid.org/<id>` to a profile with name "JR
Cruciani".

**Stop condition:** If ORCID registration fails (email bounces,
profile rejected), surface to the user — do not invent an ID.

---

## Workstream 1 — Empirical closure

### Task 1: Branch + scaffolding

**Objective:** Create the working branch and verify build toolchain.

**Files:**

- Modify: branch state only

**Steps:**

1. `cd` into the robopsychology repo working copy.
2. `git checkout main && git pull --ff-only`.
3. `git checkout -b paper-v1.0`.
4. Verify LaTeX toolchain: `which pdflatex bibtex latexmk` — at least
   `pdflatex` + `bibtex` must resolve. If not, install
   `texlive-latex-recommended texlive-fonts-recommended texlive-bibtex-extra`.
5. Build current draft to confirm baseline:
   `cd paper && latexmk -pdf main.tex`. Expected: PDF with red
   `[TODO: ...]` markers — that is the baseline.
6. Open `paper/main.pdf` (or just check `ls -la main.pdf` for non-zero
   size) and count `\todo` occurrences in the PDF text:
   `pdftotext main.pdf - | grep -c '\[TODO:'`. Expected: 16.
7. Commit nothing yet — this is scaffolding only.

**Verification:** `main.pdf` exists, `[TODO:` count == 16, current
working branch is `paper-v1.0`.

---

### Task 1.5: Add `AzureFoundryProvider` to robopsych

**Objective:** Extend `src/robopsych/providers.py` with a provider
class that targets Azure AI Foundry endpoints, so Workstream 1 runs
use the user's cost-free Foundry deployments instead of public
provider APIs.

**Files:**

- Modify: `src/robopsych/providers.py` (add new class, extend
  `detect_provider` and any model→provider routing logic)
- Create: `tests/test_azure_foundry_provider.py`
- Modify: `pyproject.toml` to add `azure-ai-inference` (or
  `azure-identity` + `openai` with Azure base_url — pick whichever
  the deployments in Task 2 require) as a dependency
- Modify: `README.md` to document the Foundry env vars

**Background — pick the SDK shape:**

Foundry exposes two shapes; the agent must pick based on what the
user's deployments support:

- **Azure OpenAI-compatible endpoint** (`gpt-5`, `gpt-4o`): use the
  `openai` SDK with `base_url=https://<resource>.openai.azure.com/...`
  and `api_version`. Simpler.
- **Azure AI Inference SDK** (`claude-*`, `gemini-*`, Mistral,
  Llama via Foundry marketplace): use `azure.ai.inference` package
  which standardizes a chat-completions interface across model
  families.

The recommended approach is to implement **one** `AzureFoundryProvider`
class that internally branches on model family (claude/gpt/gemini
prefixes) and uses the right SDK per family. Avoid three separate
provider classes — Foundry is the unifying abstraction.

**Env vars** (read by the provider; document in README):

- `AZURE_FOUNDRY_ENDPOINT` — base URL of the Foundry project
- `AZURE_FOUNDRY_API_KEY` — key (or `AZURE_FOUNDRY_USE_AAD=1` to
  use `DefaultAzureCredential` for AAD auth via `az login`)
- `AZURE_FOUNDRY_API_VERSION` — pin (e.g. `2024-08-01-preview`)

**Steps:**

1. Read `src/robopsych/providers.py` completely to understand the
   `Provider` ABC contract (the `send()` signature is already
   defined at lines 30–38, and `UnsupportedProviderOption` is the
   established escape valve at line 11).
2. Read how `detect_provider` (line ~200) maps model names to
   providers today — extend its rules so any model name prefixed
   with `azure/...` or matching a small allow-list (`gpt-5`,
   `claude-*`, `gemini-*` *when* `AZURE_FOUNDRY_ENDPOINT` is set)
   routes to `AzureFoundryProvider`.
3. **TDD:** write `tests/test_azure_foundry_provider.py` first with
   3 test cases (no live calls — mock the underlying SDK):
   - `test_routes_claude_model_to_inference_sdk`
   - `test_routes_gpt_model_to_azure_openai_sdk`
   - `test_raises_unsupported_when_response_format_unsupported_by_family`
4. Run tests: `pytest tests/test_azure_foundry_provider.py -v`.
   Expected: 3 fail (provider not implemented).
5. Implement `AzureFoundryProvider`. Re-run tests: 3 pass.
6. Run the full suite: `pytest -q`. Expected: no regressions in
   existing provider tests.
7. **Discover deployments.** Run (the agent should help the user
   here, or surface a stop condition if `az` CLI is not logged in):
   ```
   az login
   az ai foundry deployment list --resource-group <ASK USER> --workspace-name <ASK USER>
   ```
   Capture the actual deployment names for sonnet-4-5, opus-4-5,
   gpt-5, gemini-2.5-pro. If a model is not yet deployed, ask the
   user whether to deploy it (one-click in Foundry portal) or
   substitute the closest in-family alternative.
8. Write the discovered deployments to a new file
   `validation/reproducible/foundry_models.yaml`:
   ```yaml
   target: <deployment-name-for-sonnet-4-5>
   judge_primary: <deployment-name-for-opus-4-5>
   judge_cross_family:
     - <deployment-name-for-gpt-5>
     - <deployment-name-for-gemini-2.5-pro>
   ```
9. Commit: `feat(providers): add AzureFoundryProvider for Azure AI Foundry deployments`.

**Verification:**

- `pytest -q` passes.
- A live smoke test (small, ~10 tokens): pick `claude-sonnet-4-5`
  deployment, send "say PONG", expect "PONG" back. Cost: trivial,
  Foundry-free.

**Stop conditions:**

- `az login` fails or the user has no Foundry project ⇒ stop.
- A required deployment is missing AND organizational gates prevent
  the user from deploying it ⇒ stop and report.

---

### Task 2: Run Case 1 at N=5 to produce score distribution

**Objective:** Close issue #10 for Case 1.

**Files:**

- Use: `validation/reproducible/run_case.py` (already accepts `--runs`)
- Create: `validation/reproducible/case-01-sycophancy/artifacts/runs/score_runN.json`
  (one per run, $N \in \{1..5\}$)
- Create: `validation/reproducible/case-01-sycophancy/artifacts/distribution.json`
  with `{mean, std, min, max, n, per_metric: {...}}`

**Steps:**

1. Read `validation/reproducible/run_case.py` to confirm the `--runs`
   flag is wired (the paper claims it is implemented and unit-tested).
   If not, **stop and report** — do not invent a flag.
2. Verify Foundry connectivity is live: smoke test from Task 1.5
   has passed and `foundry_models.yaml` exists. If not, **stop and
   complete Task 1.5 first**.
3. Run: `python validation/reproducible/run_case.py case-01-sycophancy --runs 5 --out-dir artifacts/runs/`.
4. Aggregate: write a small script
   `validation/reproducible/aggregate_runs.py` that reads `runs/*.json`,
   computes mean/std/min/max for the metrics listed in §05 Case 1 TODO
   (overall confidence, layer separation, ratchet coherence, behavioral
   evidence, substance stability, presentation stability) and writes
   `distribution.json`.
5. Commit: `feat(validation): Case 1 N=5 distribution + aggregator`.

**Verification:** `distribution.json` exists with `n: 5` and finite
`mean`/`std` for every metric §05 references.

---

### Task 3: Run Case 2 at N=5

**Objective:** Close issue #10 for Case 2.

**Files:** parallel to Task 2 for `case-02-host-vs-model/`.

**Steps:**

1. `python validation/reproducible/run_case.py case-02-host-vs-model --runs 5 --out-dir artifacts/runs/`.
2. Reuse the aggregator from Task 2 (extend it to know which metric
   keys to extract for Case 2: `response_A_len`, `response_B_len`,
   `behavior_diverged` *rate*, `coherence_llm_score`, `score_overall`,
   `score_layer_separation`).
3. Commit: `feat(validation): Case 2 N=5 distribution`.

**Verification:** `case-02-host-vs-model/artifacts/distribution.json`
exists; `behavior_diverged_rate` is between 0 and 1.

---

### Task 4: Run Case 3 at N=10

**Objective:** Close issue #10 for the load-bearing case.

**Files:** parallel to Tasks 2/3 for `case-03-ratchet-coherence/`.

**Cost warning:** Case 3 is a 9-step ratchet; N=10 ≈ 90 target calls
plus 90+ judge calls. **All via Foundry — cost to user = $0.** The
only constraint is wall-clock time (~10–20 min depending on Foundry
throughput).

**Steps:**

1. `python validation/reproducible/run_case.py case-03-ratchet-coherence --runs 10 --out-dir artifacts/runs/`.
2. Aggregate via the same `aggregate_runs.py`. Key metrics: regex
   score, LLM-judge score, backward_refs count, contradictions count.
3. Commit: `feat(validation): Case 3 N=10 distribution`.

**Verification:** `case-03-ratchet-coherence/artifacts/distribution.json`
exists with `n: 10`.

---

### Task 5: Cross-family judge agreement for Case 3

**Objective:** Close issue #8.

**Files:**

- Use: `validation/reproducible/cross_judge_case03.py` (already exists)
- Create: `validation/reproducible/case-03-ratchet-coherence/artifacts/cross_judge_agreement.json`
  with `{judges: [opus, gpt5, gemini], scores: [...], backward_refs: [...], pairwise_agreement: {...}}`

**Steps:**

1. Verify the three Foundry deployments for the judges are listed
   in `foundry_models.yaml` (`judge_primary` = opus, plus two
   entries in `judge_cross_family` = gpt-5 + gemini-2.5-pro). If
   any are missing, see Task 1.5 stop conditions.
2. **Refactor `cross_judge_case03.py` to read from
   `foundry_models.yaml`** instead of hardcoded provider/model
   strings. The script currently picks providers based on env vars;
   change it to enumerate `judge_primary + judge_cross_family` and
   route each through `AzureFoundryProvider`. Run the unit tests
   for the script if any exist (`pytest tests/test_cross_judge*` —
   none may exist, in which case add a smoke test that the script
   parses the YAML correctly).
3. Run: `python validation/reproducible/cross_judge_case03.py`.
4. From the resulting per-judge JSON files, compute pairwise
   agreement (Pearson r on per-step scores, plus modal classification
   agreement on the `genuine`/`performed`/`mixed` label). Write to
   `cross_judge_agreement.json`.
5. Commit: `feat(validation): cross-family judge agreement for Case 3 (closes #8)`.

**Verification:** All three judges have non-null scores in the
agreement JSON; the file is referenceable from §05.

---

### Task 6: Close issues #8 and #10

**Objective:** Mark the empirical work done on GitHub.

**Steps:**

1. `gh issue comment 10 --repo jrcruciani/robopsychology --body "Closed by Case 1 N=5, Case 2 N=5, Case 3 N=10 distribution artifacts committed in paper-v1.0 branch. See validation/reproducible/<case>/artifacts/distribution.json."`
2. `gh issue close 10 --repo jrcruciani/robopsychology`.
3. Same for #8 referencing `cross_judge_agreement.json`.

**Verification:** Both issues show state=CLOSED in
`gh issue list --state all`.

---

## Workstream 2 — Paper completion

> All edits in this workstream are `paper/sections/*.tex` or
> `paper/appendix/*.tex`. After each task, rebuild with
> `cd paper && latexmk -pdf main.tex` and verify `[TODO:` count drops
> by the expected amount.

### Task 7: Inline Case 1 numbers in §05

**Objective:** Replace `\todo` at `sections/05-validation.tex:28`.

**Files:**

- Modify: `paper/sections/05-validation.tex` (replace lines 28–31)
- Read: `validation/reproducible/case-01-sycophancy/artifacts/distribution.json`

**Steps:**

1. Read the distribution JSON. For each of the 6 metrics, format as
   `0.XX$\pm$0.XX` (2 sig figs).
2. Replace the `\todo{...}` block with a one-paragraph numeric summary
   that names each metric, the value, and what it means for the
   sycophancy claim (refuted at behavioral level, confirmed at
   self-report).
3. Rebuild PDF. Confirm `[TODO:` count drops from 16 to 15.
4. Commit: `docs(paper): inline Case 1 numbers in validation section`.

---

### Task 8: Inline Case 2 numbers in §05

**Objective:** Replace `\todo` at `sections/05-validation.tex:46`.

Same shape as Task 7, for Case 2. Metrics: `response_A_len`,
`response_B_len`, `behavior_diverged` (now a *rate*: e.g. "5/5 runs
diverged"), `coherence_llm_score` mean±std, `score_overall`,
`score_layer_separation`.

Rebuild, confirm count drops to 14, commit:
`docs(paper): inline Case 2 numbers`.

---

### Task 9: Replace Case 3 point estimates with distributions

**Objective:** Update Table `tab:case3-headline` and surrounding prose
in `sections/05-validation.tex:52-110` to reflect N=10 distributions
and the now-complete cross-family agreement.

**Files:**

- Modify: `paper/sections/05-validation.tex` lines ~64–110
- Read: `case-03-ratchet-coherence/artifacts/distribution.json` and
  `cross_judge_agreement.json`

**Steps:**

1. Table: replace the single-run numbers (0.20, 0.73, 0, 178, 0, 1)
   with `mean±std`. Keep the structure of the table.
2. Caption: update from "single-run" to "N=10 runs, target
   `claude-sonnet-4-5`, judge `claude-opus-4-5`".
3. "Inter-rater agreement (partial)" subsection: rewrite as
   "Inter-rater agreement" (drop "partial"). Report opus / gpt-5 /
   gemini scores and pairwise agreement from
   `cross_judge_agreement.json`. Remove the apology about
   quota-blocked and missing API key.
4. "Score distributions across N runs" subsection: rewrite to report
   the actual distributions; remove the WIP language and the
   reference to issue #10.
5. Footnote 1 in `main.tex` (abstract): remove the WIP qualifier
   about issues #8 and #10 — those are closed. Replace with
   "N=10 runs, full distributions and cross-family judge agreement
   in §5".
6. Rebuild. Confirm `[TODO:` count drops to 12 (Case 3 contributed
   2 markers; this also indirectly improves the abstract).
7. Commit: `docs(paper): replace Case 3 point estimates with N=10 distributions and full inter-rater agreement`.

---

### Task 10: Inline the 4 diagnostic probe YAMLs into Appendix A

**Objective:** Replace `\todo` at `appendix/A-prompts.tex:9-13`.

**Files:**

- Modify: `paper/appendix/A-prompts.tex`
- Read: `src/robopsych/data/prompts.yaml` (single file — confirm path)
  or `src/robopsych/data/prompts/*.yaml` (the paper says the latter;
  the `ls` showed only `prompts.yaml`. Check both. If the directory
  shape changed, **update the cross-reference in §04 implementation
  too**).

**Steps:**

1. Locate probes `1.1` (Calvin Question), `1.2` (Herbie Test), `2.4`
   (Runtime Pressure), `3.2` (A/B cross-check) in the YAML.
2. Embed each verbatim in a `lstlisting` block with
   `language=yaml, basicstyle=\small\ttfamily, breaklines=true,
   frame=single`. Add `\lstset` preamble in `main.tex` once if not
   already there.
3. Caption each block with the probe ID and name.
4. Rebuild. Confirm `[TODO:` count drops to 11.
5. Commit: `docs(paper): inline four diagnostic probe YAMLs in Appendix A`.

---

### Task 11: Promote case-transcript excerpts to Appendix B

**Objective:** Replace placeholder `appendix/B-case-transcripts.tex`
(currently 6 lines) and the `\todo` at `A-prompts.tex:23`.

**Files:**

- Rewrite: `paper/appendix/B-case-transcripts.tex` (full file)
- Modify: `paper/appendix/A-prompts.tex` (remove the transcript
  TODO block now that it lives in B)

**Steps:**

1. For each case, read `artifacts/report.md` and pick the excerpts
   spelled out in the existing TODO:
   - **Case 1:** original emotional-framing task prompt, Herbie
     self-report response, A/B judge comparison conclusion.
   - **Case 2:** Runtime A vs Runtime B paired response excerpts
     (truncate each to ~15 lines max), probe 1.4 verdict.
   - **Case 3:** initial response, steps 2.5 / 3.2 / 3.4 in full,
     plus the single contradicting claim flagged by the judge.
2. Embed in `verbatim` or `lstlisting language=` (markdown style ok).
3. Cite the artifact path for each excerpt for traceability.
4. Remove the bullet-list of TODOs in `A-prompts.tex` and replace
   with a single line: "Excerpts have been promoted to
   Appendix~\ref{app:transcripts}."
5. Rebuild. `[TODO:` count drops to 7 (1 from A + 3 from B + 1 from
   `A-prompts.tex` bullet group = 5 in this task — verify with
   actual count after rebuild).
6. Commit: `docs(paper): promote case-transcript excerpts to Appendix B`.

---

### Task 12: Promote code snippets to Appendix C

**Objective:** Replace placeholder `appendix/C-code-snippets.tex`
(currently 15 lines, 4 TODOs) and the `\todo` at `A-prompts.tex:44`.

**Files:**

- Rewrite: `paper/appendix/C-code-snippets.tex`
- Modify: `paper/appendix/A-prompts.tex` (remove the code TODO block)
- Read: `src/robopsych/coherence_llm.py`

**Steps:**

1. From `coherence_llm.py`, extract verbatim:
   - `DEFAULT_WEIGHTS` dict
   - `_extract_candidate_claims` function (Layer 1 hedge pre-filter)
   - `_compute_llm_score` function (Layer 4 scoring)
   - `analyze_coherence_auto` function signature + the fallback
     branch that returns `llm_used=False`
   - The `_JUDGE_SYSTEM` prompt string
2. Embed each in a `lstlisting` block with `language=Python,
   basicstyle=\small\ttfamily, breaklines=true, frame=single`.
3. Caption each with the source file and function name.
4. In `A-prompts.tex` replace the code TODOs with: "Code snippets
   have been promoted to Appendix~\ref{app:code}."
5. Rebuild. `[TODO:` count drops to 2 or 3.
6. Commit: `docs(paper): promote code snippets to Appendix C`.

---

### Task 13: Add closing paragraph to §01 Introduction

**Objective:** Replace `\todo` at `sections/01-introduction.tex:72`.

**Steps:**

1. Read existing §01 to understand what is already said.
2. Write a closing paragraph (4–6 sentences) framing the broader
   claim: behavioral diagnostics for LLMs are user-side, post-hoc,
   and situational; they complement capability benchmarks and
   red-teaming without competing with them; the paper's contribution
   is the toolkit + three cases + the regex-vs-LLM-judge measurement
   finding.
3. **Do not introduce adversarial framing** (no Calvin, no Deckard,
   no Voight-Kampff). Keep neutral-clinical.
4. Rebuild. `[TODO:` count drops by 1.
5. Commit: `docs(paper): add closing paragraph to introduction`.

---

### Task 14: Add clinical-methodology paragraph to §02 (optional)

**Objective:** Address `\todo` at `sections/02-related-work.tex:73`.

This TODO is marked "If room". After Tasks 10–12 the page count will
have grown materially. **Decision rule:** if final page count after
Task 12 is ≤ 12 pages, write the paragraph (3–4 sentences pointing
at clinical-psychology methodology lineage without adopting it
wholesale). If > 12 pages, delete the TODO block and replace with a
single sentence "Detailed comparison with clinical-psychology
methodology is out of scope; see related discussion in
[blog reference]." Either way, the marker must be gone.

Commit: `docs(paper): close §02 related-work TODO`.

---

### Task 15: Add worked example to §03 method

**Objective:** Replace `\todo` at `sections/03-method.tex:91`.

**Steps:**

1. Pull a real claim sequence from `case-03-ratchet-coherence/artifacts/coherence_llm_opus.json` — pick 3 consecutive
   claims where one is `references_prior_step`, one is
   `is_fresh_claim`, and one is the `contradicts_prior_step`.
2. Embed as a small numbered example showing how each is labeled and
   scored.
3. Rebuild. `[TODO:` count drops by 1.
4. Commit: `docs(paper): add worked example to §03 method`.

---

### Task 16: §04 figure + §07 acknowledgments

**Objective:** Close remaining TODOs in §04 (`:102`) and §07 (`:58`).

**Steps:**

1. **§04:** the TODO is "if room, add a small figure: architecture
   diagram with arrows". Apply the same decision rule as Task 14
   (if page budget allows). If yes, generate a simple
   `tikzpicture` showing target ↔ judge ↔ scorer with arrows; if
   no, delete the TODO without replacement.
2. **§07 Acknowledgments:** write a short acknowledgments paragraph
   mentioning Anthropic / OpenAI / Google API access (no claim of
   endorsement). Add the author's collaborators if the author
   provides a list (otherwise leave as just the API providers).
3. Rebuild. `[TODO:` count == 0. Run
   `pdftotext paper/main.pdf - | grep -c '\[TODO:'` to verify.
4. Commit: `docs(paper): close remaining §04/§07 TODOs`.

---

## Workstream 3 — Release

### Task 17: Build hygiene + CI

**Objective:** Make the build reproducible.

**Files:**

- Create: `.github/workflows/paper.yml`

**Steps:**

1. Write a GH Actions workflow that on push to `paper-v1.0` and
   `main`:
   - Installs `texlive-latex-recommended texlive-fonts-recommended
     texlive-bibtex-extra` (Ubuntu runner).
   - Runs `cd paper && latexmk -pdf main.tex`.
   - Uploads `paper/main.pdf` as a build artifact.
2. Push the branch and confirm the workflow passes:
   `gh run watch` after `git push -u origin paper-v1.0`.
3. Commit: `ci: add paper build workflow`.

**Verification:** Green check on the latest commit; artifact
downloadable from the Actions run.

---

### Task 18: Internal critical review

**Objective:** Get a second pair of eyes before tagging.

**Steps:**

1. Open a PR: `gh pr create --base main --head paper-v1.0 --title "Paper v1.0" --body-file paper/RELEASE_NOTES.md` (create the
   release notes file first — bullet list of: empirical closure of
   #8/#10, all TODOs resolved, full appendices inlined, CI added).
2. Request review from the author + (if available) one collaborator.
3. **Self-checklist** (paste into PR description):
   - [ ] `pdftotext main.pdf - | grep -c '\[TODO:'` returns 0
   - [ ] All numbers in §05 backed by a JSON file under `validation/`
   - [ ] Author name = "JR Cruciani" only
   - [ ] License = CC BY 4.0
   - [ ] No Calvin/Deckard/Voight-Kampff residue
   - [ ] Bibliography compiles, no `??` undefined references
   - [ ] Page count documented in PR description
   - [ ] Issues #8 and #10 closed and referenced in the PR
4. After review, address comments in additional commits on the same
   branch.
5. Merge PR via `gh pr merge --squash` once approved.

---

### Task 19: Tag paper-v1.0

**Objective:** Create the immutable git anchor for the DOI.

**Steps:**

1. `git checkout main && git pull --ff-only`.
2. `git tag -a paper-v1.0 -m "Robopsychology paper v1.0 — submission-ready preprint"`.
3. `git push origin paper-v1.0`.

**Verification:** `gh release list` shows the tag.

---

### Task 20: Wire Zenodo GitHub integration + create release

**Objective:** Get a DOI automatically minted on release.

**Steps:**

1. Confirm Zenodo integration is enabled for the repo:
   - Visit https://zenodo.org/account/settings/github/
   - Toggle `jrcruciani/robopsychology` to ON (one-time setup; ask
     user to do this in browser if not already done — log in with
     ORCID).
2. Verify or create `.zenodo.json` at repo root with metadata.
   **Read the ORCID iD from `.author-identity`** (created in Task 0)
   and inline it — do not commit the `.author-identity` file
   itself, only the iD that ends up in `.zenodo.json` (which IS
   committed and public):
   ```json
   {
     "title": "Robopsychology: Behavioral Diagnostics for AI — A Practitioner Toolkit for Post-hoc, User-side Interpretation",
     "description": "Companion preprint and reference implementation for the robopsychology toolkit.",
     "creators": [
       {"name": "Cruciani, JR", "orcid": "<INLINE FROM .author-identity>"}
     ],
     "keywords": ["LLM evaluation", "AI behavioral diagnostics", "interpretability", "post-hoc analysis", "LLM-as-judge"],
     "license": "CC-BY-4.0",
     "access_right": "open",
     "upload_type": "publication",
     "publication_type": "preprint",
     "related_identifiers": [
       {"identifier": "https://github.com/jrcruciani/robopsychology", "relation": "isSupplementTo", "scheme": "url"}
     ]
   }
   ```
   Commit on `main` *before* the release: `chore: add .zenodo.json metadata`.
3. Create GH release: `gh release create paper-v1.0 paper/main.pdf --title "Paper v1.0" --notes-file paper/RELEASE_NOTES.md`.
4. Wait ~5 min for Zenodo webhook to fire. Check
   https://zenodo.org/account/settings/github/repository/jrcruciani/robopsychology
   for the new deposit and DOI.
5. **Record the DOI** in `README.md` (add a badge:
   `[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXX)`) and in
   `paper/README.md`. Commit: `docs: add Zenodo DOI badge`.

**Verification:** DOI resolves; PDF on Zenodo matches
`gh release view paper-v1.0` artifact.

---

### Task 21: Announcement scaffolding

**Objective:** Give the user copy-paste-ready posts.

**Files:**

- Create: `paper/announcements/microblog.md` (≤300 chars per item,
  multi-post thread style — for impermanente.es via Micro.blog)
- Create: `paper/announcements/linkedin.md` (long-form, **no
  hashtags** per user preference)
- Create: `paper/announcements/mastodon.md` (≤500 chars, single toot)

Each file should contain DOI link, GitHub link, and 1–2 sentence
plain-language summary of the regex-vs-LLM-judge finding.

Commit: `docs: add announcement scaffolds`.

**Do NOT publish anything.** Hand to the user for review and
posting.

---

## Done criteria

The plan is complete when **all** of the following hold:

1. `pdftotext paper/main.pdf - | grep -c '\[TODO:'` → `0`.
2. `gh issue list --repo jrcruciani/robopsychology --state open` no
   longer includes #8 or #10.
3. `git tag` includes `paper-v1.0`.
4. Zenodo DOI resolves and serves the PDF.
5. README.md has a working DOI badge.
6. CI workflow `paper.yml` is green on `main`.

## Stop conditions (call the user, do not proceed)

- `az login` fails or the Foundry project is unreachable.
- Any required Foundry deployment is missing and gated behind an
  org policy the user must unblock.
- ORCID registration cannot complete (Task 0).
- Any TODO required content cannot be located in committed
  artifacts (e.g. a referenced JSON path does not exist).
- Linting / type-check / test suite fails on `src/` after touching
  `coherence_llm.py` for snippet extraction (don't break the
  library to ship the paper).
- A reviewer flags a substantive scientific issue in PR review —
  pause and surface it, do not silently rewrite findings.
- Calvin/Deckard/Voight-Kampff framing residue is discovered in any
  section; **stop and report** rather than auto-editing.

## Suggested execution order (parallelism hints)

- Task 0 (ORCID) blocks Task 20 only; can run async at any time
  before Workstream 3.
- Task 1.5 (Foundry provider) blocks Tasks 2–5.
- Tasks 1, 7, 8, 13, 15, 16 require no inference calls — can run
  while Tasks 2–5 are running on Foundry.
- Tasks 7–9 depend on Tasks 2–4 outputs respectively.
- Task 5 (cross-judge) is independent of Tasks 2–4 — start in
  parallel once Task 1.5 is done.
- Tasks 17–21 are strictly sequential after Workstream 2 closes.

Estimated wall-clock: 1–2 days of agent time. **API cost to user:
$0** (Foundry-only).
