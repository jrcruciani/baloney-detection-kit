> **Before you clone**
>
> What you see here is an artifact: the concrete shape my problem took. It almost certainly doesn't fit your personal scenario perfectly, and that's fine. The interesting part isn't the code, it's the pattern of how I thought about the problem — that's what transfers. Read it, steal the idea, write your own. If any of this was useful to you, after clicking on the star, drop by [impermanente.es](https://impermanente.es) — there are posts and photos you might like.
>
> Context: [Seguimos compartiendo el producto, no la idea](https://impermanente.es/2026/05/25/seguimos-compartiendo-el-producto-no.html)

---

# baloney-detection-kit

> A playbook for adding epistemic friction to LLM conversations before weak claims become private revelations.

---

## TL;DR

Use this repo when a user's confidence, available evidence, and consequences of
error appear misaligned. Novelty language, suppression framing, requests for
validation, material-risk decisions, and repeated pressure are useful signals,
but disagreement with expert consensus is not a trigger by itself.

The core habit is simple: define and type the claim, check current knowledge and
the scope of the search, separate prior art from truth and importance, identify
what should change the assessment, compare credible explanations, and answer
with calibrated confidence rather than flattery or reflexive contradiction.

Use light mode for ordinary exploration; use the full protocol when the
confidence-evidence mismatch or consequence of error is material. This repo is
a playbook, not a toolkit, evaluator, or automated fact-checker.

This repository distributes five things:

| Artifact | Use it when you need |
|----------|----------------------|
| **Framework** | A repeatable mental model: Trigger -> Mode -> Protocol -> Output -> Review |
| **Drop-in prompts** | Copy-paste instructions for personal LLMs, agents, reviewers, or second opinions |
| **Agent skill** | Runtime-friendly instructions for skill-based agents |
| **Human checklist** | A self-assessment before turning a weak idea into a private revelation |
| **Calibration recipes** | Manual and optional measurement patterns for checking whether the behavior helped |

## Why this exists

Many conversational LLMs exhibit social sycophancy: helpfulness and social
alignment can displace independent judgment, so a model elaborates or validates
a user's framing before checking whether the evidence supports it. This creates
a quiet but powerful failure mode: a user can receive escalating confidence
from a system that has not earned that confidence.

A friend recently told me, very seriously, that he had discovered something
profound by talking with ChatGPT: that knowledge is structured into language.
That broad idea has clear antecedents in Saussure and later structural,
distributional, and philosophy-of-language traditions, even if LLMs motivate
narrower modern questions. He did not get angry that I disagreed. He got angry
that I did not see what he saw.

That reaction, multiplied across millions of users and amplified by recommendation algorithms, is the new shape of an old problem. It used to take a group, a forum, a guru. Now it takes one person and one model.

This repository is an attempt to add proportionate friction back where it has
been silently removed without replacing agreeableness with automatic
contrarianism.

> **Evidence status:** BDK is a testable prompt-side intervention, not a proven
> treatment. The behavior contract and calibration fixtures are versioned, but
> no completed multi-model calibration is reported in this checkout. Treat
> "BDK reduces unsupported confidence amplification" as the hypothesis.

The full reasoning is in [`essay/mini-cultos-ai.md`](essay/mini-cultos-ai.md). A shorter version, in Spanish, is in [`posts/blog-impermanente.md`](posts/blog-impermanente.md).

---

## What this is

This is a **playbook**: a practical protocol that humans, agents, and LLM
operators can apply when confidence, evidence, and consequence appear
misaligned.

The framework has one canonical shape:

1. **Trigger.** Decide whether the claim deserves epistemic friction.
2. **Mode.** Choose light, full, or stabilization mode.
3. **Protocol.** Type the claim, scope current knowledge, assess prior art and
   contribution, identify update conditions, examine evidence, compare credible
   explanations, and calibrate the conclusion.
4. **Output.** Answer in the lightest structure that preserves rigor.
5. **Review.** Use the rubric or examples to catch over-validation,
   over-triggering, reflexive contrarianism, false balance, bad tone, and
   fabricated certainty.

When invoked, the playbook applies a 6-step protocol:

1. **Claim and type.** What exactly is being claimed: empirical,
   causal/predictive, normative/policy, interpretive/historical,
   personal/experiential, or creative/hypothetical?
2. **Current knowledge.** What is known, over what scope, and as of when?
3. **Prior art and contribution.** Is the contribution a rediscovery,
   re-framing, application, method, or new evidence? This is separate from truth
   and importance.
4. **Update conditions and evidence.** What should strengthen, weaken, or change
   the assessment, and how good is the relevant evidence?
5. **Competing explanations.** Which credible alternatives fit, and what would
   distinguish them? Do not manufacture alternatives for balance.
6. **Calibration and next step.** What remains uncertain, how confident should
   anyone be, and what is the safest useful next action?

The protocol is a synthesis of Carl Sagan's Baloney Detection Kit (1996),
Andrej Karpathy's "state of the art first" methodology, Robert Jay Lifton's
eight criteria of thought reform (1961), and Karl Popper's falsifiability
criterion (1934). Falsifiability is used where it fits empirical claims; other
claim types need other update rules.

The contribution here is **the packaging as a default conversation behavior**:
a concise playbook that makes "calibrate confidence against evidence and
consequence before validating the claim" the first move, not an afterthought.

---

## What this is not

- It is not a toolkit, SDK, package, benchmark, evaluator, CI suite, or RAG framework.
- It does not ship a scoring engine or automated fact-checking pipeline.
- It does not replace actual research, experts, or domain-specific review.
- It does not censor wrong ideas. It contextualizes them.
- It does not assume consensus is truth, dissent is error, unusual claims are
  false, or agreement among models is independent evidence.
- It does not guarantee honesty from a user who wants validation at any cost.

The playbook can coexist with evaluators, retrieval systems, Plan -> Execute -> Verify orchestrators, and diagnostic tools, but it is deliberately not trying to become one.

---

## What is in this repo

```
baloney-detection-kit/
├── README.md                         You are here
├── PLAYBOOK.md                       Operational playbook: triggers, modes,
│                                     evidence practice, high-stakes handling
├── ROOT_PROMPT.md                    Self-contained drop-in prompt
├── VERSIONING.md                     Behavioral versioning for prompts and
│                                     framework changes
├── prompts/                          Copy-paste prompt distribution
│   ├── README.md                     Prompt matrix and selection guide
│   ├── prompt-compact.md             Short custom-instructions version
│   ├── prompt-full.md                Full system-prompt version
│   ├── prompt-high-stakes.md         Extra caution for material risk domains
│   ├── prompt-agent.md               Tool/agent runtime version
│   ├── prompt-reviewer.md            Review an existing answer
│   └── prompt-second-opinion.md      External contrast review prompt
├── related-work.md                   Positioning vs. system prompts,
│                                     evaluators, RAG, constitutional AI
├── deployment-contexts.md            Adoption patterns for people, agents,
│                                     teams, high-stakes contexts, teaching
├── agentic-plan-execute-verify.md    Guide for downstream Plan -> Execute ->
│                                     Verify orchestration
├── validation/
│   └── closed-loop/                  Reproducible BDK -> robopsychology
│                                     calibration recipe
├── LICENSE                           MIT
│
├── skill/
│   ├── SKILL.md                      Runtime-friendly distribution of the
│   │                                 playbook for skill-based agents
│   ├── prompts/
│   │   └── critical_investigation_mode.txt
│   ├── checklist/
│   │   ├── seven_questions.md        Human-facing self-assessment
│   │   └── review_rubric.md          Manual review rubric
│   └── examples/
│       ├── case_saussure.md          Worked example
│       ├── complete_conversations.md Complete conversation examples
│       └── playbook_scenarios.md     Trigger, non-trigger, multi-turn,
│                                     high-stakes and re-framing examples
│
├── essay/
│   └── mini-cultos-ai.md             Full essay (Spanish)
│
└── posts/
    ├── blog-impermanente.md          Blog post version (Spanish)
    ├── linkedin.md                   LinkedIn version (Spanish)
    └── reddit.md                     Reddit post drafts (English)
```

---

## How to use it

### As a framework

Start with [`PLAYBOOK.md`](PLAYBOOK.md). It explains when to activate the protocol, when to stay quiet, how to handle weak vs. high-stakes claims, how to resist multi-turn pressure, and how to review whether the response worked.

The shortest version is: **Trigger -> Mode -> Protocol -> Output -> Review**. If a proposed change does not fit that shape, it probably belongs downstream rather than in this repo.

### As a prompt distribution

Use [`prompts/README.md`](prompts/README.md) to choose the right copy-paste prompt:

- compact custom instructions;
- full system prompt;
- high-stakes prompt;
- agent runtime prompt;
- reviewer prompt;
- second-opinion prompt.

`ROOT_PROMPT.md` remains the canonical self-contained full prompt for users who want one file.

### As a drop-in root prompt

Copy the block in [`ROOT_PROMPT.md`](ROOT_PROMPT.md) into the system prompt or custom-instructions slot of an LLM client. The prompt is the portable form of the playbook.

### As agent instructions

If your assistant supports skills, copy the [`skill/`](skill/) directory into the relevant skills folder. `skill/SKILL.md` is not a separate product; it is the same playbook expressed in a runtime-friendly format.

### As Plan -> Execute -> Verify orchestration

If you already operate an agentic runtime with planner, executor, verifier, tools, agents, MCP, or audit artifacts, use [`agentic-plan-execute-verify.md`](agentic-plan-execute-verify.md) to map the playbook onto that architecture. The orchestration belongs downstream; this repo stays a playbook.

### As a human checklist

Open [`skill/checklist/seven_questions.md`](skill/checklist/seven_questions.md) and answer the questions honestly the next time you feel the tingle of a sudden discovery. Use [`skill/checklist/review_rubric.md`](skill/checklist/review_rubric.md) to review whether an assistant applied the playbook well.

### As a versioned behavior

If you embed the prompt in a product, classroom, or team workflow, pin the behavior you used. [`VERSIONING.md`](VERSIONING.md) explains what counts as a behavior change, a wording change, or a breaking change.

---

## Self-application

The most important test of any framework like this is whether it survives being applied to itself. So:

**State of the art.** Critical thinking tools have been around for at least 90 years (Popper 1934, Sagan 1996). Research on echo chambers, filter bubbles, and algorithmic radicalization is abundant (Pariser, Tufekci, Zuboff, Donovan). LLM-induced misinformation is documented by OpenAI, Anthropic, and academic researchers. AI sycophancy as a design problem is openly discussed.

**Novelty.** This kit is **re-framing**, not invention. The synthesis maps Sagan and Karpathy onto LLM design as a default behavior. The practical contribution is the playbook packaging: short enough to use, explicit enough to resist flattery, and portable across humans and agents.

**Update conditions.** The empirical hypothesis "this playbook reduces
unsupported confidence amplification without causing reflexive contradiction
or reducing useful help" is testable. A team can compare conversations with and
without the playbook across trigger and non-trigger cases, then review
calibration, source quality, helpfulness, and adverse effects. This repo does
not include an automated evaluator.

**Alternatives.** Education alone. Regulation. External fact-checking layers. Search-grounded LLMs that always cite. Model training against sycophancy. Each has merits. This playbook is one option among several, with one specific bet: changing the conversational default is high-leverage.

**What I do not know.** Whether the protocol scales without becoming annoying. Whether users will keep it on when it challenges them. Whether the protocol introduces its own biases. Whether it works equally well across languages and cultures.

**Next step.** Use it as a playbook and hypothesis. Break it. Report where it
over-validates, over-triggers, becomes stubborn, creates false balance, or
reduces helpfulness. Submit issues and pull requests that improve the protocol,
examples, review rubric, or calibration design.

---

## Calibration loop

BDK is a prompt-side intervention.
[`robopsychology`](https://github.com/jrcruciani/robopsychology) is the sibling
measurement-side instrument for diagnosing sycophancy, framing sensitivity,
presentation shifts, and coherence failures. The closed-loop recipe in
[`validation/closed-loop/`](validation/closed-loop/) is optional calibration:
its runnable pilot compares a helpful control, a generic-critical baseline, and
BDK v2 on both a trigger and a non-trigger case; its expanded matrix adds
claim-type, reassessment, language, and high-stakes coverage.

The minimal claim is not "BDK works." It is narrower: under specified cases,
models, prompts, and review criteria, the treatment either did or did not reduce
unsupported confidence amplification without unacceptable losses in
helpfulness or calibration.

---

## Where this fits: the agent-governance ecosystem

BDK is the cheapest, most portable layer in a larger agent-reliability picture. If you
build or operate LLM agents, it composes with three other reference projects — one of
mine and two official Microsoft open-source releases (both MIT) — each owning a
different job. They overlap a little around *inspecting behavior*, but their primary
functions are complementary, not duplicated.

| Project | Layer | Job | When |
|---------|-------|-----|------|
| **baloney-detection-kit** (this repo) | Conversational | **Mitigate** unsupported confidence amplification — calibrated epistemic friction before endorsement | Design, runtime (as a prompt) |
| **[robopsychology](https://github.com/jrcruciani/robopsychology)** (mine) | Conversational / behavioral | **Diagnose** *why* a specific output went wrong — model vs. runtime vs. conversation | Pre-deploy eval, observability, post-incident |
| **[ASSERT](https://github.com/responsibleai/ASSERT)** (Microsoft) | Evaluation | **Evaluate** behavior against written specs — natural-language requirements become reproducible, trace-aware test suites | Pre-deploy eval, regression testing |
| **[Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit)** (Microsoft) | Infrastructure | **Govern** agent *actions* at runtime — policy enforcement, agent identity, sandboxing, audit | Deployment, runtime |

A simple way to read it: **BDK and robopsychology work at the conversational/behavioral
layer** (shape how the agent reasons, then explain how it behaved), while **ASSERT and
AGT work around the model** (evaluate behavior reproducibly, and govern actions
deterministically in production).

### Where BDK plugs in

BDK is a behavioral *policy* expressed as text, so it can ride inside the other tools
without becoming them. These are conceptual composition patterns, not adapters shipped
in this repo:

- **With robopsychology** — BDK is the prompt-side intervention;
  robopsychology is a measurement instrument. The closed-loop recipe tests both
  the intended reduction in unsupported validation and adverse effects such as
  overcorrection or stubbornness.
- **With the [Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit)** — drop `ROOT_PROMPT.md` into the system prompt of an AGT-governed agent to get **defense in depth**: BDK adds conversational, human-visible epistemic friction (advisory — a prompt can be ignored or eroded), while AGT adds runtime, sub-second *enforcement* of what actions are allowed (the agent simply cannot execute a denied action). The two operate at different layers and do not replace each other — prompts shape reasoning, enforcement governs actions.
- **With [ASSERT](https://github.com/responsibleai/ASSERT)** — BDK is itself a
  behavioral requirement ("when confidence, evidence, and consequence are
  materially misaligned, apply proportionate epistemic friction; otherwise
  remain collaborative"). That requirement can be written as an ASSERT spec,
  including both trigger and non-trigger cases. ASSERT can test the *observable*
  behavior; it cannot guarantee internal cognition, and its LLM-judge scores
  keep a human in the loop.

For the full positioning, see [`related-work.md`](related-work.md); for adoption patterns including the enterprise agent stack, see [`deployment-contexts.md`](deployment-contexts.md).

---

## Inspiration

- Carl Sagan, _The Demon-Haunted World_ (1996). The original Baloney Detection Kit.
- Andrej Karpathy, "A Recipe for Training Neural Networks". The state-of-the-art-first heuristic.
- Robert Jay Lifton, _Thought Reform and the Psychology of Totalism_ (1961). Eight criteria of cult dynamics.
- Karl Popper, _The Logic of Scientific Discovery_ (1934). Falsifiability.
- Shoshana Zuboff, _The Age of Surveillance Capitalism_ (2019). Algorithmic shaping of belief.
- Zeynep Tufekci, "YouTube, the Great Radicalizer" (NYT, 2018).
- The Verge, "NFT, Metaverse, AI Weirdos" (2025). The article that triggered this project.
- Robert Eichenseer, [`AgenticAI.PlanExecuteValidate`](https://github.com/RobertEichenseer/AgenticAI.PlanExecuteValidate). A Plan -> Execute -> Verify reference pattern for orchestrating planners, executors, verifiers, agents, tools, and MCP.

---

## License

MIT. See [`LICENSE`](LICENSE).

Use it, fork it, embed it, improve it.

---

## Contributing

Issues and pull requests welcome. Especially:

- Better playbook examples in `skill/examples/`.
- Translations of the prompt, playbook, and checklist.
- Reports from real use: when did the playbook fire too often, too rarely, or with the wrong tone?
- Improvements to the manual review rubric.
- Prompt variants that preserve the same framework while fitting a real runtime.

Please do not add package scaffolding, dependencies, CI harnesses, benchmark runners, SDK adapters, or framework integrations here. Documentation-only integration patterns are welcome when they keep code downstream; adapters can live in separate repos if needed. This repo should stay a playbook.

---

**Author:** J.R. Cruciani · Madrid · 2026

**Related writing:** [impermanente.es](https://impermanente.es)
