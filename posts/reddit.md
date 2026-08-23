# Reddit Post (English)

Two versions ready to publish. Pick the one that fits the subreddit tone.

**Suggested subreddits** (by fit): r/PromptEngineering, r/LocalLLaMA, r/ArtificialInteligence, r/ChatGPT, r/ClaudeAI, r/singularity (downvote risk).

---

## Version A: "I wrote a playbook" (high conversion, safe)

**Title:**
> I wrote a playbook that prompts LLMs to check user "discoveries" before validating them

**Body:**

A friend of mine recently told me, dead serious, that he had discovered
something profound by talking with ChatGPT: that knowledge is structured into
language. The broad intuition has clear antecedents in structural,
distributional, and philosophy-of-language traditions. That does not settle
every modern question about LLMs, but it does undercut a global novelty claim
based on one conversation. He got annoyed not because I disagreed, but because I
did not see what he saw.

That moment made me realize how easy it is, in 2026, to be in a "mini-cult of
one". It used to take a forum, a guru, or a group. Now one person and a chatbot
that exhibits social sycophancy can be enough.

I wrote a small open playbook: **baloney-detection-kit**. It is a synthesis of
Carl Sagan's Baloney Detection Kit, Andrej Karpathy's "state of the art first"
methodology, Lifton's cult dynamics, and Popper's falsifiability. The
contribution is the packaging: a practical protocol / drop-in system prompt
intended to make calibrated epistemic friction a conversational default.

When triggered, the model applies a 6-step protocol before validating any claim:

1. Claim type and scope
2. Current knowledge and search limits
3. Prior art and contribution, separated from truth and importance
4. Update conditions and evidence quality
5. Credible alternatives and discriminating evidence, without false balance
6. Calibrated confidence and a safe next step

The instructions are model-agnostic, though behavior will vary by model and
runtime. Use the playbook, paste the prompt as a system message, or adapt the
skill instructions for an agent. The repo also includes a 7-question human
checklist, a manual review rubric, and worked examples.

Repo: https://github.com/jrcruciani/baloney-detection-kit
MIT, free, no signup, no telemetry.

The kit applies its own filter to itself in the README. Spoiler: nothing in it is original. The only contribution is reducing the friction so people might actually use it.

Curious to hear from anyone who tries it: does it improve your conversations, or does it just make the model annoying?

---

## Version B: "Discussion / problem-first" (best for r/PromptEngineering)

**Title:**
> LLM sycophancy can reinforce personal mini-cults. I wrote a playbook for resisting it. Looking for feedback.

**Body:**

Observation that has been bugging me: major conversational LLMs can validate a
user's framing before checking whether the evidence supports it. Combine that
with users alone in their feed bubble and you can get something that resembles
cult dynamics, except the congregation is one person and the validating priest
is a model.

Sagan's Baloney Detection Kit and Karpathy's "look up the state of the art
before you have an opinion" offer many of the cognitive ingredients. They still
require discipline that is easy to skip in the heat of an epiphany.

So I moved some of the discipline from the user to the system. I wrote a
playbook + system prompt that runs a proportionate 6-step protocol when
confidence, evidence, and consequence appear misaligned:

1. What exactly is the claim, and what type is it?
2. What is known, over what search scope?
3. What is prior art, and what kind of contribution remains?
4. What should update the assessment, and how good is the evidence?
5. Which credible alternatives fit, and what would distinguish them?
6. What confidence and next step are justified?

Drop-in prompts work with OpenAI, Anthropic, and local models. BDK 3.0 also includes an optional reference CLI, behavioral diagnostics, validation scenarios, a checklist, a rubric, and examples.

Repo: https://github.com/jrcruciani/baloney-detection-kit (MIT)

Two questions for this sub:

1. Where does the prompt over-trigger, become stubborn, create false balance, or
   reduce helpfulness?
2. Anyone seen prior art doing exactly this as a default-behavior layer (not as
   an optional "rigor mode")?

The README applies the playbook to itself and admits the synthesis is not novel. The packaging is the only contribution.

---

## Posting tips

- Post in ONE sub first (ideally r/PromptEngineering). Wait 24h before cross-posting to avoid spam flags.
- If you get banned for self-promo: comment on related threads in the sub for a week before posting your own.
- Reply to the first 5 comments within 1h. Reddit's algorithm rewards early engagement.
- Do NOT edit title or body after publishing (penalty).
- Karma threshold matters: some subs (r/LocalLLaMA) require minimum account age + karma.
