# Workshop preprint draft

> **Academic track — work in progress.** This is the formal write-up of the
> method. The practitioner-facing version lives in
> [the playbook](https://impermanente.es/robopsychology-playbook/). Validation
> studies (Cohen's κ on ratchet coherence, judge agreement across model
> families) are tracked in issues #8 and #10.

This directory contains the LaTeX source for the robopsychology
workshop preprint (repository issue
[#11](https://github.com/jrcruciani/robopsychology/issues/11)).

## Status

This is a **first scaffold**, not a submission-ready draft. Sections
are seeded with content derived from the repository's existing
markdown documents (`framework/method.md`, `framework/taxonomy.md`,
`framework/related-work.md`, `validation/reproducible/*/analysis.md`,
`README.md`) so the structure is in place and reviewers can see the argument flow. Places that
require original authorial writing or numbers from runs that haven't
been executed yet are flagged with `\todo{...}` blocks inside the
source.

`\todo{...}` blocks render in red so they're visible in the compiled
PDF and easy to grep for in the source.

## File layout

```
paper/
├── README.md                       ← this file
├── main.tex                        ← root LaTeX file (article class)
├── bibliography.bib                ← references cited in the draft
├── sections/
│   ├── 01-introduction.tex
│   ├── 02-related-work.tex
│   ├── 03-method.tex
│   ├── 04-implementation.tex
│   ├── 05-validation.tex
│   ├── 06-limitations.tex
│   └── 07-future-work.tex
├── appendix/
│   ├── A-prompts.tex
│   ├── B-case-transcripts.tex
│   └── C-code-snippets.tex
└── figures/                        ← empty; .gitkeep only
```

## Build

The draft uses generic LaTeX so it compiles without venue-specific
style files:

```bash
cd paper/
pdflatex main.tex
bibtex   main
pdflatex main.tex
pdflatex main.tex
```

Or with `latexmk`:

```bash
cd paper/
latexmk -pdf main.tex
```

The output is `main.pdf` (~8 pages + appendix once `\todo` blocks
are resolved).

## Target venue

In order of fit (per issue #11):

1. **NeurIPS SafetyML workshop** — behavioral evals with measurable rigor.
2. **ICLR BlogTrack** — if framed as methodology + case studies.
3. **ACL RepL4NLP** — interpretability / representation angle.
4. **HEAL workshop** — practitioner-diagnosis angle.

Swap `main.tex`'s preamble for the venue-specific style file
(e.g. `neurips_2026.sty` or `iclr2026_conference.sty`) once selected.

## Outstanding work before submission

Blocking work, in order of dependency:

1. **Issue #10 (score distributions, $N$ runs).** Cases 1 and 2 now
   report Azure Foundry $N=5$ distributions in
   `sections/05-validation.tex`. Case~3 still needs the planned
   Foundry $N=10$ distribution before the validation section is fully
   camera-ready.

2. **Issue #8 (cross-family judges).** Re-run the Case~3 transcript
   through the Azure Foundry judge matrix (`gpt-5` and
   `mistral-large`) to get cross-family agreement. The script
   (`validation/reproducible/cross_judge_case03.py`) is in place and
   reads the deployments from `validation/reproducible/foundry_models.yaml`.

Non-blocking work (`\todo{...}` in the source):

3. Inline the remaining Case~3 aggregate numbers once the $N=10$ run
   is available.
4. Add the architecture diagram figure to `figures/architecture.pdf`.
5. Inline the verbatim YAML prompt text for the four key probes in
   appendix A.
6. Pick five-to-eight high-signal transcript excerpts per case for
   appendix B.
7. Extract the three code snippets for appendix C.
8. Write the acknowledgments section (last 4 lines of
   `07-future-work.tex`).

## arXiv submission

Once the `\todo` blocks above are resolved and the paper compiles
cleanly:

```bash
cd paper/
latexmk -pdf main.tex
# create a self-contained tarball for arXiv:
tar czf arxiv-submission.tar.gz \
    main.tex bibliography.bib main.bbl \
    sections/ appendix/ figures/
```

Then submit to arXiv under `cs.CL` or `cs.AI`. Update the root
`README.md`'s Citation section with the resulting arXiv ID
(replacing the current GitHub-only placeholder citation).
