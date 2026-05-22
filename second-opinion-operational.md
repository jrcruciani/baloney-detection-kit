# Second Opinion — Operational Lessons

Companion notes to [`PLAYBOOK.md`](PLAYBOOK.md) §5 ("Second opinion with two AI models") and [`skill/checklist/review_rubric.md`](skill/checklist/review_rubric.md) §8 ("External contrast").

The playbook says **what** the second-opinion practice is. These are the implementation lessons from actually running it in an agent runtime: things that look obvious on paper but fail silently in practice. They are intentionally narrow — no infrastructure, no evaluator, no tool. Just rules of thumb for the human or agent driving the contrast.

---

## 1. Summarize the object; do not paste the conversation

This is the single highest-leverage rule and the easiest to get wrong.

If the reviewer model sees the chain of reasoning that produced the first answer, it will tend to confirm that chain. If it sees only the object — the claim, the draft, the decision — it will tell the requester what they missed.

Operational rule: extract the **object to review** (claim, paragraph, plan, decision) and send only that, with enough framing context for the reviewer to evaluate it on its own merits. Do not paste the prior chat. Do not include the first answer "for context".

The whole point of a second opinion is that the reviewer is not contaminated by how the object was reached.

---

## 2. Pick reviewers from genuinely different training lineages

The playbook warns that "models can share training data, cultural assumptions, and hallucination patterns." Operationalize it.

Heuristic: pick reviewers from **different providers and different base-model lineages**. Two GPTs from the same provider are not two opinions; they are one opinion sampled twice. A Hermes 4 + Mistral Large pair, or a Claude + Llama-derivative pair, gives real contrast.

If only one model family is available, say so explicitly and lower the weight given to agreement. Two same-family models agreeing is weak evidence; two different-family models agreeing is moderate evidence; two different-family models disagreeing is the most informative outcome.

---

## 3. The courier is not the third reviewer

If an agent orchestrates the second-opinion call, the orchestrator should return the two external outputs **as external outputs**, side by side, without silently folding them into its own answer.

Default output shape:

```text
━━━ Reviewer A (model, provider) ━━━
<raw answer>

━━━ Reviewer B (model, provider) ━━━
<raw answer>
```

Only add synthesis if the user explicitly asked for it. When synthesizing, label the section visibly (e.g. `━━━ Synthesis from orchestrator ━━━`) so the user can tell which sentences come from a reviewer and which come from the orchestrator. Otherwise the orchestrator's own bias contaminates the contrast it was supposed to enable.

---

## 4. For URLs and files, extract content first

Direct model APIs usually cannot browse. Passing a bare URL to a reviewer that lacks tool use produces hallucinated reviews of what the model *believes* the URL says.

Operational rule: if the object is a URL or file, fetch/extract the text first and send the text. If extraction fails, say so and ask the human to paste the relevant content.

---

## 5. Ask reviewers for severity-tagged findings

Combine the playbook's neutral-prompt guidance with explicit severity tags. Without severity, reviewers tend to pad the response with low-impact nitpicks to look thorough; with severity, the load-bearing flaws surface first.

Suggested suffix to the neutral prompt:

```text
Tag each finding with a severity:
- high: load-bearing flaw; if true, the main thesis or decision fails.
- medium: meaningful weakness that should be addressed but does not invalidate
  the whole.
- low: nitpick, stylistic, or polish-level issue.

Surface high-severity findings first. Do not pad with lows to look thorough.
```

This pairs naturally with the playbook's evidence-chain step: one `high` from one reviewer outweighs any number of `low`s, regardless of which reviewer produced them.

---

## 6. Match the reviewer's response language to the object's language

If the object is in language L, ask both reviewers to answer in L. If a reviewer answers in a different language anyway, **do not silently translate** — note the mismatch and pass the response through. Translation by the orchestrator loses signal (hedges, idiom, specificity) precisely where the contrast matters most.

---

## 7. Handle asymmetric failure explicitly

If one reviewer fails (rate limit, auth error, timeout) and the other succeeds:

- Return the successful review.
- Add a concise note of which reviewer failed and why at a high level (do not leak credentials, raw headers, or stack traces).
- Do not present a single-reviewer pass as triangulation. Single-reviewer is single-reviewer; the contrast is gone.

If both fail, say so and fall back to the first answer with an explicit "no external contrast was obtained" caveat.

---

## 8. Preserve disagreement; don't paper over it

The playbook already says agreement is not proof. The corollary, worth emphasising in the rubric, is that **disagreement is signal, not failure**. When the two reviewers diverge:

- Preserve the divergence in the output.
- Identify what they agree on (often the unsurprising part) and what they diverge on (usually the load-bearing part).
- The honest conclusion is often: "Not settled by this pass. Next step is a primary source or a domain expert."

Trying to resolve the disagreement on the orchestrator's authority defeats the purpose of asking.

---

## 9. What to write up after the contrast

A useful artifact for the requester after a second-opinion pass:

```text
Object reviewed: <one line>
Reviewers: <model A> / <model B>

Agreements:
- ...

Disagreements:
- ... (and the likely reason)

Highest-severity findings:
- ... (with which reviewer raised them)

What no reviewer addressed:
- ...

Next step:
- read X / ask expert Y / run test Z / narrow the claim
```

This is also the right shape for the rubric §8 review notes.

---

## What this is not

These notes do not propose:

- a runner, evaluator, or benchmark;
- a specific provider, SDK, or framework;
- an automated way to score reviewer agreement;
- a replacement for the playbook itself.

They are practice notes for anyone implementing §5 of the playbook in a real agent runtime, in the same spirit as the rest of the repo: a habit, not infrastructure.
