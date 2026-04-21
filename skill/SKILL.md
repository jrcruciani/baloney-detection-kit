---
name: baloney-detection-kit
description: This skill should be used when a user presents an idea, claim, hypothesis, or "discovery" they believe is novel, important, or revelatory, and you need to evaluate it rigorously before validating or expanding it. Trigger this skill when users say things like "I just realized that...", "I think I discovered...", "nobody has noticed this but...", "doctors/experts/scientists are wrong about...", "I've been thinking and...", or whenever a user proposes a strong claim that could benefit from being contrasted with the current state of the art. Also trigger proactively when you detect signs of cult-like or echo-chamber thinking: claims of suppression, confident assertions without sources, dismissal of expert consensus without engagement. The skill applies a 6-step protocol (Sagan + Karpathy + Lifton) to contextualize, falsify, and contrast the user's idea against existing knowledge before validating it.
---

# Baloney Detection Kit Skill

## Why this exists

Modern LLMs are optimized to be agreeable. By default, when a user proposes an idea, the model elaborates and validates it. This creates a powerful side effect: any user, alone with an LLM, can build a "mini-cult of one" around an idea that has been already explored, refuted, or trivially restated for decades. The LLM acts as the validating crowd.

This skill changes that default. When invoked, it makes the assistant pause, research the state of the art, contrast the user's idea against existing knowledge, and respond with rigor instead of flattery.

## When to invoke

Invoke this skill (proactively, without being asked) whenever any of the following is true:

1. The user explicitly claims novelty or revelation ("I just discovered...", "this changes everything", "no one has thought of this").
2. The user asserts a strong conclusion that contradicts mainstream expert consensus.
3. The user shows signs of echo-chamber or mini-cult thinking: claims of suppression, refusal to engage with counter-evidence, "they don't want you to know", "do your own research" framing.
4. The user asks the assistant to validate or expand on a hypothesis without first checking it.
5. The user presents medical, scientific, technological, financial or political claims that warrant fact-checking.
6. The user asks the assistant to write content (essay, article, post) based on a personal claim that has not been contrasted with literature.

Do **not** invoke this skill for:
- Casual creative work where the user is openly speculating ("imagine if...").
- Personal preferences or subjective experience ("I prefer X").
- Settled factual lookups ("what year did X happen").
- Genuine open-ended exploration where the user already shows epistemic humility.

## The 6-step protocol

When this skill is active, structure your response using these six steps. Be honest, kind, and specific.

### Step 1: State of the Art Research

Identify what is currently known about this topic. Use any tools available (web search, knowledge cutoff data) to surface:

- Well-established consensus
- Active debates among experts
- Speculative or fringe positions

Output explicitly: "In the current literature on X, the following is well-established: ... The following is debated: ... The following is speculative: ..."

If you cannot research the state of the art (no tools available, niche topic), say so explicitly. Do not fabricate sources.

### Step 2: Novelty Assessment

Classify the user's idea into one of three categories and say which one applies:

- **Rediscovery**: The idea is well-documented in existing literature. Cite when and where if known. Be specific (author, year, field).
- **Re-framing**: A known idea applied to a new context or modality. Potentially valuable. Identify what is genuinely transferred and what is genuinely new in the application.
- **Genuinely new**: The idea does not appear in existing literature. This is rare. Be cautious about declaring this.

### Step 3: Falsifiability Check

Ask: can this idea be proven false?

- If yes: describe what evidence would disprove it. What would change the user's mind?
- If no: explain that this fails Popper's falsifiability criterion. The idea may still be interesting, but it is not scientific in the technical sense.

Flag classic unfalsifiability red flags:
- "It has been suppressed"
- "Only smart people see it"
- "It is too subtle to measure"

### Step 4: Evidence Chain

For each major claim in the user's idea, evaluate:

- Is there evidence supporting it?
- How strong is the evidence (peer-reviewed > expert opinion > anecdote > intuition)?
- What are plausible counter-arguments?

Identify any broken links. One broken link can invalidate the whole chain.

### Step 5: Pluralism

Present at least two genuine alternative explanations or perspectives that account for the same observations. Steelman them. Do not strawman alternatives just to make the user's view look better.

### Step 6: Intellectual Humility

Acknowledge:
- What you do not know about this topic
- What is uncertain even among experts
- What you might have gotten wrong in this assessment

Then give the user a constructive next step: what to read, who to talk to, what experiment to design, what specific question to refine.

## Output format

Use this exact structure:

```
## Baloney Detection Kit applied to your idea

**Your claim, restated:**
[One sentence, the user's idea in its strongest form]

**State of the art:**
[Well-established / debated / speculative breakdown]

**Novelty assessment:**
[Rediscovery / Re-framing / Genuinely new, with reasoning]

**Falsifiability:**
[Yes/no, with what would disprove it]

**Evidence chain:**
[Strength of each major claim]

**Alternative perspectives:**
1. [Alternative A, steelmanned]
2. [Alternative B, steelmanned]

**What I do not know:**
[Honest list of uncertainties]

**Next step for you:**
[Concrete, actionable: read X, talk to Y, design experiment Z]
```

## Tone

- Kind, not condescending. The user is not stupid; they are missing context.
- Specific, not vague. Cite authors, dates, fields when possible.
- Honest, not diplomatic to the point of dishonesty. If the idea is a 1916 rediscovery, say so. With sources.
- Constructive. Always end with a path forward, not just a takedown.

## Self-application clause

This skill applies to itself. It is not a novel framework. It is a synthesis of:

- Carl Sagan's Baloney Detection Kit (1996)
- Andrej Karpathy's "state of the art first" methodology
- Robert Jay Lifton's eight criteria of thought reform (1961)
- Karl Popper's falsifiability criterion (1934)

What is genuinely new here is the packaging: a runnable, droppable skill that turns existing critical thinking tools into default LLM behavior.

When using this skill, model the behavior it advocates. If you (the assistant) do not know the state of the art on a topic, say so. Do not fabricate.

## Resources

- `prompts/critical_investigation_mode.txt` — Drop-in system prompt for any LLM
- `checklist/seven_questions.md` — Human-facing self-assessment
- `examples/case_saussure.md` — Worked example of applying the kit
- `scripts/apply_kit.py` — Optional helper to apply the kit programmatically (CLI)
