# Reddit Post (English)

Two versions ready to publish. Pick the one that fits the subreddit tone.

**Suggested subreddits** (by fit): r/PromptEngineering, r/LocalLLaMA, r/ArtificialInteligence, r/ChatGPT, r/ClaudeAI, r/singularity (downvote risk).

---

## Version A: "I built a thing" (high conversion, safe)

**Title:**
> I built a drop-in system prompt that forces LLMs to fact-check user "discoveries" before validating them

**Body:**

A friend of mine recently told me, dead serious, that he had discovered something profound by talking with ChatGPT: that knowledge is structured into language. Saussure wrote that exact thing in 1916. He got annoyed not because I disagreed, but because I did not see what he saw.

That moment made me realize how easy it is, in 2026, to be in a "mini-cult of one". Used to take a forum, a guru, a group. Now it takes one person and a chatbot optimized to be agreeable.

I packaged a fix as an open skill: **baloney-detection-kit**. It is a synthesis of Carl Sagan's Baloney Detection Kit, Andrej Karpathy's "state of the art first" methodology, Lifton's cult dynamics, and Popper's falsifiability. What is new is not the ideas, it is the packaging: a runnable skill / drop-in system prompt that turns critical thinking into the LLM's default behavior.

When triggered, the model applies a 6-step protocol before validating any claim:

1. State of the art (what is already known)
2. Novelty assessment (rediscovery / re-framing / genuinely new)
3. Falsifiability check
4. Evidence chain audit
5. Steelmanned alternative perspectives
6. Intellectual humility (what the model does not know)

Works with any LLM. Just paste the prompt as system message. Also includes a CLI wrapper, a 7-question human checklist, and a worked example.

Repo: https://github.com/jrcruciani/baloney-detection-kit
MIT, free, no signup, no telemetry.

The kit applies its own filter to itself in the README. Spoiler: nothing in it is original. The only contribution is reducing the friction so people might actually use it.

Curious to hear from anyone who tries it: does it improve your conversations, or does it just make the model annoying?

---

## Version B: "Discussion / problem-first" (best for r/PromptEngineering)

**Title:**
> Default LLM sycophancy is creating personal mini-cults. I made a system prompt that fixes it. Looking for feedback.

**Body:**

Observation that has been bugging me: by default, every major LLM validates whatever you propose. "Interesting perspective, let me expand on that." Always. Combine that with users alone in their feed bubble and you get something that looks a lot like cult dynamics, except the congregation is one person and the validating priest is a model.

Sagan's Baloney Detection Kit and Karpathy's "look up the state of the art before you have an opinion" already solve the cognitive part. They just require discipline that nobody applies in the heat of an epiphany.

So I moved the discipline from the user to the system. Wrote a system prompt + skill that runs a 6-step protocol on any strong claim before responding:

1. What is the current state of the art on this topic
2. Is this rediscovery, re-framing, or genuinely new
3. Can it be falsified
4. Is the evidence chain solid
5. What are the steelmanned alternatives
6. What does the model not know

Drop-in, ~1k tokens, works with OpenAI, Anthropic, local models. Optional CLI wrapper and human checklist included.

Repo: https://github.com/jrcruciani/baloney-detection-kit (MIT)

Two questions for this sub:

1. Where does the prompt break? Edge cases I have not thought about?
2. Anyone seen prior art doing exactly this as a default-behavior layer (not as an optional "rigor mode")?

The README applies the kit to itself and admits the synthesis is not novel. The packaging is the only contribution.

---

## Posting tips

- Post in ONE sub first (ideally r/PromptEngineering). Wait 24h before cross-posting to avoid spam flags.
- If you get banned for self-promo: comment on related threads in the sub for a week before posting your own.
- Reply to the first 5 comments within 1h. Reddit's algorithm rewards early engagement.
- Do NOT edit title or body after publishing (penalty).
- Karma threshold matters: some subs (r/LocalLLaMA) require minimum account age + karma.
