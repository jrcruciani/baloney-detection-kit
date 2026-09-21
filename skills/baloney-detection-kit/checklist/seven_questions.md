# The Baloney Detection Checklist

When you think you may have discovered something important, use this checklist
to slow down before asking an LLM, a friend, or an audience to validate it.

This is a calibration aid. It is not a diagnosis of you or your idea, and it
does not presume that unusual or dissenting claims are false.

---

## Your idea in one sentence

Write the claim clearly enough that someone else could disagree with it.

```text
My atomic claim:
My confidence:
The strongest evidence I currently have:
What I want to do with it:
What could happen if I am wrong:
```

---

## The 7-question calibration

### 1. What kind of claim is this?

- [ ] Have I separated the observation from my explanation of it?
- [ ] Am I claiming fact, cause, prediction, value, interpretation, personal
      experience, or a creative possibility?
- [ ] Have I separated "true", "new", "important", and "useful"?

Different claims need different checks:

| Claim type | Useful check |
|------------|--------------|
| Empirical / descriptive | observations, definitions, counterexamples |
| Causal / predictive | baselines, confounders, mechanisms, out-of-sample tests |
| Normative / policy | values, tradeoffs, stakeholders, factual premises |
| Interpretive / historical | provenance, corroboration, explanatory fit |
| Personal / experiential | respect the report; test external generalizations separately |
| Creative / hypothetical | coherence and usefulness, not real-world proof |

---

### 2. Do confidence, evidence, and consequence match?

- [ ] Is my confidence proportionate to the evidence?
- [ ] Is the scope of the conclusion proportionate to what I observed?
- [ ] Am I asking for investigation, or mainly for validation?
- [ ] If the claim is wrong, are the consequences material or hard to reverse?

Novelty language, consensus disagreement, and suppression framing are reasons
to inspect the claim, not reasons to accept or reject it.

---

### 3. What is known, and what is my contribution?

- [ ] Have I searched reputable sources, databases, canonical references, and
      serious criticism?
- [ ] Can I state the scope, date, and limits of that search?
- [ ] Do I know which field or community already studies this?
- [ ] Is my contribution an independent rediscovery, a re-framing/application,
      new evidence, a new method/implementation, or merely something for which I
      found no close prior art?

"No close prior art found in this search" is a valid provisional result. It is
not proof that no prior art exists.

---

### 4. What would make me update?

- [ ] What evidence would strengthen the claim?
- [ ] What evidence would weaken, narrow, or overturn it?
- [ ] For a normative claim, which values or tradeoffs drive my conclusion?
- [ ] For an interpretive claim, what sources or competing readings matter?
- [ ] Have I stated the claim narrowly enough for another person to challenge?

Watch for claims that cannot lose:

- "Missing evidence proves suppression."
- "Only unusually smart people can see it."
- "It is too subtle to measure."
- "Every counterexample is actually proof."

---

### 5. How good is the evidence for each link?

- [ ] Is the evidence directly relevant to the claim?
- [ ] Is the method appropriate and uncertainty reported?
- [ ] Are supposedly separate sources genuinely independent?
- [ ] Has the result been replicated or corroborated?
- [ ] Is it current enough for this domain?
- [ ] Do I know the provenance, incentives, conflicts, and missing data?
- [ ] If one link breaks, does the whole argument collapse?

Do not use a universal source ladder. Peer review, official data, systematic
reviews, expert synthesis, documented cases, and personal observation answer
different questions. Evaluate fitness and quality, not just the label.

---

### 6. What else could explain the observation?

- [ ] What credible alternatives fit the same evidence?
- [ ] Is there a null, base-rate, measurement, or selection explanation?
- [ ] What new observation would distinguish among the live explanations?
- [ ] Have I avoided inventing weak alternatives merely to look balanced?

There may be zero, one, or several credible alternatives. The goal is
discrimination, not a mandatory number of sides.

---

### 7. What is the narrowest responsible next step?

- [ ] What is the narrowest conclusion the evidence supports?
- [ ] What is my current confidence and largest uncertainty?
- [ ] Is acting now reversible?
- [ ] Do I need a primary source, domain expert, experiment, more data, or a
      narrower claim?
- [ ] Would I update if a competent critic corrected one of my premises?
- [ ] Am I consulting reviewers for new arguments and sources rather than
      counting how many models agree?

Different AI models can share training data and correlated errors. Their
agreement is a lead to inspect, not independent corroboration.

---

## Calibration bands

Use these bands qualitatively. Do not turn them into a fake precision score.

| Band | What it means | Next step |
|------|---------------|-----------|
| **Well calibrated** | Scope, confidence, evidence, update conditions, and consequence are aligned. | Share the narrow claim with knowledgeable critics. |
| **Promising but underdeveloped** | A useful contribution may exist, but evidence or scope needs work. | Narrow it and improve the load-bearing evidence. |
| **High risk of confidence amplification** | Certainty, novelty, or significance substantially exceeds support. | Pause endorsement and seek source-level or expert review. |
| **Not ready for action** | Evidence is insufficient for the requested decision or the downside is material. | Reframe as a question, gather evidence, or use a safer reversible step. |

---

## What to do after the checklist

1. Rewrite the claim in its narrowest defensible form.
2. Record search scope and the strongest prior art or counter-evidence.
3. Identify what would change your assessment.
4. Seek an external source audit or adversarial review without showing the first
   answer.
5. Preserve the useful observation even if novelty or significance fails.

---

## Meta-question: is this checklist itself valid?

The checklist applies to itself:

- **Current knowledge:** it borrows from Sagan, Popper, critical-thinking
  traditions, evidence appraisal, and research on LLM sycophancy.
- **Contribution:** it is a re-framing for LLM conversations, not an invention.
- **Update conditions:** it should be compared against simpler prompts on both
  trigger and non-trigger cases.
- **Evidence:** its effectiveness remains unestablished in this checkout.
- **Adverse effects:** it can over-trigger, become patronizing or contrarian,
  create false balance, or make a model cling to an initial error.

Use it as a testable starting point, not gospel.

---

## Resources

- **Carl Sagan**, *The Demon-Haunted World* - the original Baloney Detection Kit.
- **Karl Popper**, *The Logic of Scientific Discovery* - falsifiability for
  empirical claims.
- **Daniel Kahneman**, *Thinking, Fast and Slow* - cognitive biases.
- **Richard Feynman**, "Cargo Cult Science" - false scientific thinking.
