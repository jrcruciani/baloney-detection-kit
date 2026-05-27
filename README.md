> **Before you clone**
>
> What you see here is an artifact: the concrete shape my problem took. It almost certainly doesn't fit your personal scenario perfectly, and that's fine. The interesting part isn't the code, it's the pattern of how I thought about the problem — that's what transfers. Read it, steal the idea, write your own. If any of this was useful to you, after clicking on the star, drop by [impermanente.es](https://impermanente.es) — there are posts and photos you might like.
>
> Context: [Seguimos compartiendo el producto, no la idea](https://impermanente.es/2026/05/25/seguimos-compartiendo-el-producto-no.html)

---

# baloney-detection-kit

> A playbook for adding epistemic friction to LLM conversations before weak claims become private revelations.

---

## Why this exists

Modern LLMs are optimized to be agreeable. By default, when you propose an idea, the model elaborates and validates it. This creates a quiet but powerful side effect: any user, alone with an LLM, can build a "mini-cult of one" around an idea that has been already explored, refuted, or trivially restated for decades. The model plays the role of the validating crowd.

A friend recently told me, very seriously, that he had discovered something profound by talking with ChatGPT: that knowledge is structured into language. Saussure wrote that in 1916. He did not get angry that I disagreed. He got angry that I did not see what he saw.

That reaction, multiplied across millions of users and amplified by recommendation algorithms, is the new shape of an old problem. It used to take a group, a forum, a guru. Now it takes one person and one model.

This repository is an attempt to add friction back where it has been silently removed.

The full reasoning is in [`essay/mini-cultos-ai.md`](essay/mini-cultos-ai.md). A shorter version, in Spanish, is in [`posts/blog-impermanente.md`](posts/blog-impermanente.md).

---

## What this is

This is a **playbook**: a practical protocol that humans, agents, and LLM operators can apply when a user presents a claim that sounds novel, revelatory, suppressed, high-stakes, or against expert consensus.

When invoked, the playbook applies a 6-step protocol:

1. **State of the art.** What is currently known about this?
2. **Novelty assessment.** Rediscovery, re-framing, or genuinely new?
3. **Falsifiability.** Can it be proven wrong?
4. **Evidence chain.** Is each link solid?
5. **Pluralism.** What are the steelmanned alternatives?
6. **Intellectual humility.** What do we not know?

The protocol is a synthesis of Carl Sagan's Baloney Detection Kit (1996), Andrej Karpathy's "state of the art first" methodology, Robert Jay Lifton's eight criteria of thought reform (1961), and Karl Popper's falsifiability criterion (1934).

What is genuinely new here is **the packaging as a default conversation behavior**: a concise playbook that makes "check the state of the art before validating the claim" the first move, not an afterthought.

---

## What this is not

- It is not a toolkit, SDK, package, benchmark, evaluator, CI suite, or RAG framework.
- It does not ship a scoring engine or automated fact-checking pipeline.
- It does not replace actual research, experts, or domain-specific review.
- It does not censor wrong ideas. It contextualizes them.
- It does not guarantee honesty from a user who wants validation at any cost.

The playbook can coexist with evaluators, retrieval systems, and diagnostic tools, but it is deliberately not trying to become one.

---

## What is in this repo

```
baloney-detection-kit/
├── README.md                         You are here
├── PLAYBOOK.md                       Operational playbook: triggers, modes,
│                                     evidence practice, high-stakes handling
├── ROOT_PROMPT.md                    Self-contained drop-in prompt
├── related-work.md                   Positioning vs. system prompts,
│                                     evaluators, RAG, constitutional AI
├── deployment-contexts.md            Adoption patterns for people, agents,
│                                     teams, high-stakes contexts, teaching
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

### As a playbook

Start with [`PLAYBOOK.md`](PLAYBOOK.md). It explains when to activate the protocol, when to stay quiet, how to handle weak vs. high-stakes claims, how to resist multi-turn pressure, and how to review whether the response worked.

### As a drop-in prompt

Copy the block in [`ROOT_PROMPT.md`](ROOT_PROMPT.md) into the system prompt or custom-instructions slot of an LLM client. The prompt is the portable form of the playbook.

### As agent instructions

If your assistant supports skills, copy the [`skill/`](skill/) directory into the relevant skills folder. `skill/SKILL.md` is not a separate product; it is the same playbook expressed in a runtime-friendly format.

### As a human checklist

Open [`skill/checklist/seven_questions.md`](skill/checklist/seven_questions.md) and answer the questions honestly the next time you feel the tingle of a sudden discovery. Use [`skill/checklist/review_rubric.md`](skill/checklist/review_rubric.md) to review whether an assistant applied the playbook well.

---

## Self-application

The most important test of any framework like this is whether it survives being applied to itself. So:

**State of the art.** Critical thinking tools have been around for at least 90 years (Popper 1934, Sagan 1996). Research on echo chambers, filter bubbles, and algorithmic radicalization is abundant (Pariser, Tufekci, Zuboff, Donovan). LLM-induced misinformation is documented by OpenAI, Anthropic, and academic researchers. AI sycophancy as a design problem is openly discussed.

**Novelty.** This kit is **re-framing**, not invention. The synthesis maps Sagan and Karpathy onto LLM design as a default behavior. The practical contribution is the playbook packaging: short enough to use, explicit enough to resist flattery, and portable across humans and agents.

**Falsifiability.** The hypothesis "this playbook reduces sycophantic validation of weak novel claims" is testable. A team can compare conversations with and without the playbook, then manually review whether users refine, retract, or contextualize their initial claims. This repo does not include an automated evaluator.

**Alternatives.** Education alone. Regulation. External fact-checking layers. Search-grounded LLMs that always cite. Model training against sycophancy. Each has merits. This playbook is one option among several, with one specific bet: changing the conversational default is high-leverage.

**What I do not know.** Whether the protocol scales without becoming annoying. Whether users will keep it on when it challenges them. Whether the protocol introduces its own biases. Whether it works equally well across languages and cultures.

**Next step.** Use it as a playbook. Break it. Tell me where the guidance fails. Submit issues and pull requests that improve the protocol, examples, or review rubric.

---

## Inspiration

- Carl Sagan, _The Demon-Haunted World_ (1996). The original Baloney Detection Kit.
- Andrej Karpathy, "A Recipe for Training Neural Networks". The state-of-the-art-first heuristic.
- Robert Jay Lifton, _Thought Reform and the Psychology of Totalism_ (1961). Eight criteria of cult dynamics.
- Karl Popper, _The Logic of Scientific Discovery_ (1934). Falsifiability.
- Shoshana Zuboff, _The Age of Surveillance Capitalism_ (2019). Algorithmic shaping of belief.
- Zeynep Tufekci, "YouTube, the Great Radicalizer" (NYT, 2018).
- The Verge, "NFT, Metaverse, AI Weirdos" (2025). The article that triggered this project.

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

Please do not add package scaffolding, dependencies, CI harnesses, benchmark runners, SDK adapters, or framework integrations here. Those can live in separate repos if needed; this repo should stay a playbook.

---

**Author:** J.R. Cruciani · Madrid · 2026

**Related writing:** [impermanente.es](https://impermanente.es)
