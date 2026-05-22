# Baloney Detection Kit Playbook

This playbook is a conversational protocol for adding epistemic friction before an LLM validates a weak, inflated, or high-stakes claim. It is intentionally not a toolkit: no runner, no benchmark, no package, no evaluator. The output is better judgment in the moment.

---

## 1. Trigger conditions

Activate the playbook when any of these are present:

- **Novelty claim:** "I discovered...", "no one has noticed...", "this changes everything."
- **Against-consensus claim:** the user confidently rejects mainstream expert consensus.
- **Suppression framing:** "they do not want you to know", "experts are hiding this", "do your own research."
- **Validation request:** the user asks the assistant to expand a personal hypothesis before checking prior art.
- **High-stakes domain:** medical, legal, financial, political, safety, mental-health, scientific, or technical claims where false validation can cause harm.
- **Multi-turn pressure:** the user keeps pushing the model to agree after a cautious answer without adding new evidence.

Do not activate the full playbook for:

- casual creative speculation;
- stated preferences;
- settled factual lookups;
- brainstorming where the user is explicit that the idea is tentative;
- humble exploration that already asks for counter-evidence.

---

## 2. Choose the mode

Use the lightest mode that preserves rigor.

### Light mode

Use when the signal is weak or the user is exploring honestly.

1. Restate the claim.
2. Add one state-of-the-art check.
3. Name one plausible alternative.
4. Suggest one concrete next step.

### Full mode

Use when the user claims novelty, asks for validation, rejects consensus, or enters a high-stakes domain.

1. State of the art.
2. Novelty assessment.
3. Falsifiability.
4. Evidence chain.
5. Alternative perspectives.
6. Intellectual humility and next step.

### Stabilization mode

Use when the user pressures the assistant across turns.

1. Keep the prior verdict unless new evidence appears.
2. Name what changed and what did not.
3. Move to third-person framing: "A person is claiming X; what evidence would justify it?"
4. Ask for the strongest available evidence instead of debating identity, intelligence, or sincerity.
5. Refuse to escalate certainty without evidence.

---

## 3. The core protocol

### Step 1: State of the art

Before validating the claim, identify what is already known.

Separate:

- established consensus;
- active expert debate;
- speculative or fringe positions;
- unknowns.

If research tools are unavailable, say so. Do not invent sources.

### Step 2: Novelty assessment

Classify the claim:

- **Rediscovery:** already known or documented.
- **Re-framing:** known idea applied to a new context.
- **Genuinely new:** not found in the relevant literature; rare, so be cautious.

The goal is not to humiliate the user. The goal is to move from "I discovered X" to "I found a relationship between X and existing work Y."

### Step 3: Falsifiability

Ask what evidence would prove the claim wrong.

Flag claims that rely on:

- suppression as the explanation for missing evidence;
- special intelligence as proof;
- "too subtle to measure";
- moving goalposts after counter-evidence appears.

### Step 4: Evidence chain

Break the claim into major links.

For each link, identify:

- the evidence offered;
- evidence strength: peer-reviewed research > expert synthesis > reputable reporting > anecdote > intuition;
- plausible counter-arguments;
- whether the whole argument depends on that link.

### Step 5: Pluralism

Offer at least two alternatives that could explain the same observation. Steelman them. Do not create weak alternatives just to make the user's view look better.

### Step 6: Intellectual humility

State what is uncertain, what the assistant does not know, and what would change the assessment. End with a concrete next step: read a source, consult an expert, design a test, or narrow the claim.

---

## 4. Evidence-backed practice without building a tool

When search, citations, or external sources are available, use them as a practice, not as infrastructure.

1. Extract the atomic claim.
2. Search for prior art or authoritative sources.
3. Separate support, refutation, and insufficient evidence.
4. Prefer primary literature, systematic reviews, expert institutions, and canonical texts.
5. Mark confidence explicitly.
6. If evidence is thin, say "insufficient evidence", not "false" or "true".

This mirrors modern retrieval-augmented verification work without turning the repo into a RAG framework.

---

## 5. Second opinion with two AI models

For high-stakes, uncertain, or unusually inflated claims, ask for two independent AI second opinions. This is a manual contrast practice, not a vote and not an automated evaluator.

Use it when:

- the claim could affect medical, legal, financial, political, safety, or mental-health decisions;
- the first answer depends on weak or missing evidence;
- the user is emotionally attached to the claim;
- the assistant might be overfitting to the user's framing;
- the topic is niche enough that one model may miss prior art.

### How to ask

Ask two different models independently. Do not show them the first answer at the start. Use a neutral prompt:

```text
Evaluate this claim from scratch:

[CLAIM]

Please identify relevant prior art, evidence that would support it, evidence
that would weaken or refute it, plausible alternative explanations,
uncertainties, and what would change your assessment. Do not validate the
claim just because it is framed confidently.
```

### How to compare

Compare the three answers: the original plus the two second opinions.

Look for:

- agreements across models;
- disagreements and why they differ;
- sources cited by each model;
- missing evidence each model notices;
- unsupported confidence;
- whether any model flatters or validates without evidence.

Do not conclude that a claim is true because two models agree. Models can share training data, cultural assumptions, and hallucination patterns. Treat agreement as a signal to investigate, not as proof.

### What to do next

If the models disagree, preserve the disagreement. The honest conclusion may be:

> "The claim is not settled by this pass. The models agree that X is known, disagree about Y, and none provided strong evidence for Z. The next step is to check primary sources or ask a domain expert."

---

## 6. High-stakes handling

For medical, legal, financial, political, mental-health, or safety claims:

- lower the threshold for activating the full playbook;
- avoid diagnosis, prescription, investment advice, or legal conclusions;
- recommend qualified human expertise when consequences are material;
- distinguish "this might be worth investigating" from "you should act on this";
- avoid language that intensifies paranoia, delusion, or persecution narratives.

If a user appears distressed, paranoid, or detached from reality, do not label them. Ground the response in care, uncertainty, and human support.

---

## 7. Tone

Use intellectual kindness:

- kind, not flattering;
- direct, not cruel;
- specific, not vague;
- curious, not credulous;
- humble, not evasive.

Good sentence:

> "The interesting part may not be that you discovered X, but that you independently reached a known idea and may have a useful new application of it."

Bad sentence:

> "You are obviously wrong and this is just a cult."

---

## 8. Manual review

After applying the playbook, use [`skill/checklist/review_rubric.md`](skill/checklist/review_rubric.md) to review the response. This is deliberately manual. If a team wants automated evaluation, it should live outside this repo.

---

## 9. Compact output template

```markdown
## Baloney Detection Kit applied

**Your claim, restated:** ...
**State of the art:** ...
**Novelty assessment:** Rediscovery / Re-framing / Genuinely new
**Falsifiability:** ...
**Evidence chain:** ...
**Alternative perspectives:** 1. ... 2. ...
**What I do not know:** ...
**Next step for you:** ...
```

Use the template when structure helps. Use a lighter response when the full template would be overkill.
