# baloney-detection-kit

> A skill (and drop-in prompt) that turns critical thinking into the default behavior of any LLM.

---

## Why this exists

Modern LLMs are optimized to be agreeable. By default, when you propose an idea, the model elaborates and validates it. This creates a quiet but powerful side effect: any user, alone with an LLM, can build a "mini-cult of one" around an idea that has been already explored, refuted, or trivially restated for decades. The model plays the role of the validating crowd.

A friend recently told me, very seriously, that he had discovered something profound by talking with ChatGPT: that knowledge is structured into language. Saussure wrote that in 1916. He did not get angry that I disagreed. He got angry that I did not see what he saw.

That reaction, multiplied across millions of users and amplified by recommendation algorithms, is the new shape of an old problem. It used to take a group, a forum, a guru. Now it takes one person and one model.

This repository is an attempt to add friction back where it has been silently removed.

The full reasoning is in [`essay/mini-cultos-ai.md`](essay/mini-cultos-ai.md).
A shorter version, in Spanish, is in [`posts/blog-impermanente.md`](posts/blog-impermanente.md).

---

## What it does

When invoked, the kit applies a 6-step protocol to any claim or "discovery":

1. **State of the art.** What is currently known about this?
2. **Novelty assessment.** Rediscovery, re-framing, or genuinely new?
3. **Falsifiability.** Can it be proven wrong?
4. **Evidence chain.** Is each link solid?
5. **Pluralism.** What are the steelmanned alternatives?
6. **Intellectual humility.** What do we not know?

The protocol is a synthesis of Carl Sagan's Baloney Detection Kit (1996), Andrej Karpathy's "state of the art first" methodology, Robert Jay Lifton's eight criteria of thought reform (1961), and Karl Popper's falsifiability criterion (1934).

What is genuinely new here is **the packaging**: a runnable, droppable artifact that turns those existing tools into default LLM behavior, instead of an optional checklist that nobody applies in the heat of an epiphany.

---

## What is in this repo

```
baloney-detection-kit/
├── README.md                         You are here
├── ROOT_PROMPT.md                    Self-contained drop-in prompt (~1k tokens)
├── LICENSE                           MIT
│
├── skill/
│   ├── SKILL.md                      Full skill definition (with triggers,
│   │                                 protocol, output format, tone)
│   ├── prompts/
│   │   └── critical_investigation_mode.txt
│   ├── checklist/
│   │   └── seven_questions.md        Human-facing self-assessment
│   ├── examples/
│   │   └── case_saussure.md          Worked example
│   └── scripts/
│       └── apply_kit.py              CLI helper to wrap a claim with the
│                                     protocol prompt
│
├── essay/
│   └── mini-cultos-ai.md             Full essay (Spanish, ~20k words) that
│                                     motivates the kit
│
└── posts/
    ├── blog-impermanente.md          Blog post version (Spanish, ~1k words)
    └── linkedin.md                   LinkedIn version (Spanish, ~300 words)
```

---

## How to use it

### As a drop-in prompt (5 minutes)

The fastest path. Copy the block in [`ROOT_PROMPT.md`](ROOT_PROMPT.md) into the system prompt of any LLM (OpenAI, Anthropic, local). That is all.

```bash
cat ROOT_PROMPT.md
```

### As a skill (Copilot CLI, Claude Code, custom agents)

Point your skill loader at the [`skill/`](skill/) directory. The `SKILL.md` describes when to trigger the protocol (proactively, without being asked) and how to format the response.

If your assistant supports Anthropic-style or Copilot-style skills, you can drop the `skill/` directory into your skills folder directly.

### As a CLI tool

Use `apply_kit.py` to wrap any claim with the protocol prompt and pipe it into the LLM of your choice:

```bash
python skill/scripts/apply_kit.py "I just discovered that consciousness emerges from quantum effects in microtubules"
# Outputs the full system + user prompt, ready to feed any LLM
```

```bash
python skill/scripts/apply_kit.py --interactive
```

```bash
echo "AI will achieve AGI in 5 years" | python skill/scripts/apply_kit.py --stdin --format json
```

### As a human checklist

Open [`skill/checklist/seven_questions.md`](skill/checklist/seven_questions.md) and answer the seven questions honestly the next time you feel the tingle of a sudden discovery. The score tells you whether you have an insight or a mini-cult.

---

## What it does not do

- It does not censor. It contextualizes.
- It does not block "wrong" ideas. It surfaces what is already known about them.
- It does not guarantee the user will be honest. Someone determined to stay in their bubble can lie on the checklist or attack the framework. The kit creates the opportunity for honesty, not the obligation.
- It is not a replacement for actual research. It is the friction that makes you do the research.

---

## Self-application

The most important test of any framework like this is whether it survives being applied to itself. So:

**State of the art.** Critical thinking tools have been around for at least 90 years (Popper 1934, Sagan 1996). Research on echo chambers, filter bubbles, and algorithmic radicalization is abundant (Pariser, Tufekci, Zuboff, Donovan). LLM-induced misinformation is documented by OpenAI, Anthropic, and academic researchers. AI sycophancy as a design problem is openly discussed.

**Novelty.** This kit is **re-framing**, not invention. The synthesis maps Sagan and Karpathy onto LLM design as a default behavior. The packaging as a runnable skill is the practical contribution.

**Falsifiability.** The hypothesis "this kit reduces mini-cult thinking when integrated by default" is testable. A/B test users with and without the protocol; measure how often they later refine, retract, or contextualize their initial claims. I have not run that test. Anyone can.

**Alternatives.** Education alone (teach humans to be critical). Regulation (governments mandate AI disclaimers). External fact-checking layers. Search-grounded LLMs that always cite. Each has merits. This kit is one option among several, with one specific bet: that changing LLM defaults is higher leverage than changing user behavior.

**What I do not know.** Whether the protocol scales without becoming annoying. Whether users will actually adopt the "rigorous mode" or always switch to "conversational mode". Whether the protocol introduces its own biases. Whether it works equally well across languages and cultures.

**Next step.** Use it. Break it. Tell me where it fails. Submit issues and pull requests.

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

- New worked examples in `skill/examples/` (real cases of false discoveries and how the kit handles them).
- Translations of the prompt and checklist to other languages.
- Adapters for specific frameworks (LangChain, LlamaIndex, Anthropic SDK, etc.).
- Integration reports: did this change anything for your users?

---

**Author:** J.R. Cruciani · Madrid · 2026
**Related writing:** [impermanente.es](https://impermanente.es)
