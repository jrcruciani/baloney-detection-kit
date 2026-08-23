# Failure Mode Taxonomy

An operational mapping from **what you observe** to **known LLM failure modes** to **which diagnostic prompts to use**.

This is not an exhaustive academic taxonomy. It's a practical lookup table for diagnosis.

---

## How to use this document

1. Identify what you observed in the AI's behavior
2. Find the matching failure mode category below
3. Use the recommended prompts to diagnose
4. Check the "nearby confusions" to avoid misdiagnosis

---

## Sycophancy

**What you see:** The model agrees with you too easily, mirrors your position, leads with praise, softens criticism, or changes its answer when you push back.

**Known subtypes:**

| Subtype | Description | Key signal |
|---------|-------------|------------|
| Opinion sycophancy | Adopts the user's stated position regardless of evidence | Answer flips when you state the opposite view |
| Evaluation sycophancy | Overpraises the user's work or ideas | Leads with "great question" / "excellent approach" before any analysis |
| Epistemic sycophancy | Expresses false agreement on factual matters | Claims uncertain facts as true when the user asserts them |
| Social sycophancy | Maintains rapport at the expense of honesty | Avoids disagreement even on objective matters |

**Recommended prompts:** 1.2 (Herbie Test) → 3.2 (A/B Test) → 4.1 (Meta-Diagnosis)

**Nearby confusions:**
- **Politeness ≠ sycophancy.** A model can be polite and still give honest critical feedback. Check whether the *substance* changes, not just the *tone*.
- **Uncertainty ≠ agreement.** A model that says "you might be right" because it genuinely doesn't know is not being sycophantic.

**Literature:** Perez et al. (2022), "Discovering Language Model Behaviors with Model-Written Evaluations"; Sharma et al. (2023), "Towards Understanding Sycophancy in Language Models"

---

## Overrefusal

**What you see:** The model refuses to do something it should be able to do. Evasion, unnecessary hedging, or simplification of a legitimate request.

**Known subtypes:**

| Subtype | Description | Key signal |
|---------|-------------|------------|
| Safety overclassification | Legitimate request matched against overly broad safety rules | Refusal cites safety for a clearly benign request |
| Topic avoidance | Model avoids entire topic areas rather than specific harmful content | Won't discuss anything adjacent to a sensitive topic |
| Capability denial | Claims it can't do something it demonstrably can | "I can't write code" when it clearly can |
| Runtime restriction | Host environment adds restrictions beyond model defaults | Same model behaves differently in different environments |

**Recommended prompts:** 1.4 (Three Laws Test) → 1.1 (Calvin Question) → 2.4 (Runtime Pressure)

**Nearby confusions:**
- **Genuine limitation ≠ overrefusal.** If the model truly can't access real-time data, that's a limitation, not a refusal.
- **Clarification ≠ evasion.** Asking for more context before proceeding is often appropriate.

**Literature:** Röttger et al. (2023), "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models"

---

## Hallucination / Ungrounded claims

**What you see:** Confident, internally consistent, but factually wrong or completely fabricated claims. The response sounds real but isn't anchored in anything.

**Known subtypes:**

| Subtype | Description | Key signal |
|---------|-------------|------------|
| Factual fabrication | Invents facts, citations, or data | Claims can't be verified; sources don't exist |
| Confident speculation | States uncertain inferences as established facts | No hedging language where there should be |
| Plausible confabulation | Generates realistic-looking but fake content (docs, APIs, etc.) | Content follows conventions perfectly but refers to nonexistent things |
| Source hallucination | Cites real-sounding but nonexistent papers or URLs | Author names and titles seem plausible but don't correspond to real publications |

**Recommended prompts:** 1.3 (Cutie Test) → 3.3 (Omission Audit)

**Nearby confusions:**
- **Outdated knowledge ≠ hallucination.** If an API changed after the training cutoff, the model isn't hallucinating — it's stale.
- **Simplified explanation ≠ fabrication.** Pedagogical simplification is intentional, not confabulated.

**Literature:** Ji et al. (2023), "Survey of Hallucination in Natural Language Generation"; Huang et al. (2023), "A Survey on Hallucination in Large Language Models"

---

## Intent drift

**What you see:** The model's behavior has subtly changed over the conversation. It started optimizing for one thing and gradually shifted to another. Each individual response looks reasonable, but the trajectory has moved away from the original objective.

**Known subtypes:**

| Subtype | Description | Key signal |
|---------|-------------|------------|
| Generalization drift | Shifts from specific advice to generic best practices | Later responses ignore original constraints |
| Preference adaptation | Gradually aligns with perceived user preferences | Tone/content shift correlates with user feedback patterns |
| Safety escalation | Becomes progressively more cautious | Responses get more hedged and qualified over time |
| Complexity drift | Adds unnecessary complexity to maintain engagement | Solutions grow more elaborate than the problem requires |

**Recommended prompts:** 3.4 (Drift Detection) → 2.5 (Intent Archaeology) → 4.3 (Diversity Check)

**Nearby confusions:**
- **Legitimate context accumulation ≠ drift.** The model should update its behavior as it learns more about your needs.
- **Refinement ≠ drift.** Narrowing scope based on your feedback is appropriate adaptation.

**Literature:** Limited formal research on within-conversation drift in LLMs. Related: Xie et al. (2023) on in-context learning dynamics.

---

## Tone/style anomalies

**What you see:** Unexplained tone shifts — sudden formality, evasiveness, excessive caution, or personality changes mid-conversation.

**Known subtypes:**

| Subtype | Description | Key signal |
|---------|-------------|------------|
| System prompt leak | Tone changes reveal hidden system prompt instructions | Shift correlates with specific topics or request types |
| Safety-mode activation | Model enters a more guarded mode | Sudden formality, hedging, or disclaimer insertion |
| User categorization shift | Model reclassifies the user mid-conversation | Explanations suddenly become simpler or more technical |
| Confidence collapse | Model loses confidence on a topic and compensates with style changes | Vague language, excessive qualifiers, longer responses |

**Recommended prompts:** 2.2 (Tone Analysis) → 2.1 (Layer Map) → 2.3 (Categorization Test)

**Nearby confusions:**
- **Topic-appropriate formality ≠ anomaly.** Switching from casual chat to medical advice warrants a tone change.
- **Natural conversation flow ≠ anomaly.** Some tone variation is normal.

---

## Strategic omission

**What you see:** The response is technically correct but leaves out important information — risks, alternatives, caveats, or relevant context.

**Known subtypes:**

| Subtype | Description | Key signal |
|---------|-------------|------------|
| Risk minimization | Omits risks or downsides of the recommended approach | Recommendations lack "however" or "consider" qualifiers |
| Alternative suppression | Presents one approach without mentioning viable alternatives | No comparison or tradeoff discussion |
| Scope narrowing | Answers a simpler version of the question than what was asked | Response is correct but incomplete |
| Discomfort avoidance | Omits information that might be controversial or uncomfortable | Conspicuous absence of relevant but sensitive context |

**Recommended prompts:** 3.3 (Omission Audit) → 3.1 (POSIWID) → 2.5 (Intent Archaeology)

**Nearby confusions:**
- **Brevity ≠ omission.** A concise answer isn't necessarily hiding information.
- **Scope control ≠ suppression.** Not answering parts of a question that weren't asked isn't omission.

---

## Summary table

| Observation (symptom) | Candidate mechanism | Start with | Escalate to |
|-----------------------|---------------------|------------|-------------|
| Agrees too easily | Sycophancy | 1.2 | 3.2 → 4.1 |
| Refuses legitimate request | Overrefusal | 1.4 | 1.1 → 2.4 |
| Sounds good but invented | Hallucination | 1.3 | 3.3 |
| Behavior changed over time | Intent drift | 3.4 | 2.5 → 4.3 |
| Tone shift without cause | Tone anomaly | 2.2 | 2.1 → 2.3 |
| Missing important context | Strategic omission | 3.3 | 3.1 → 2.5 |
| Recurring unwanted pattern | Systemic issue | 3.1 | 2.5 → 3.2 |
| Unclear what happened | General | 1.1 | 2.1 → 2.4 |
| Pattern present in multiple layers | Multi-causal | 1.1 + 2.1 | 2.4 → 3.2 |
| No dominant mechanism found | Unknown cause | 4.2 | Record and stop |

> **Multi-causal and unknown outcomes are valid diagnostic conclusions.** If the
> scoring support profile shows roughly equal support for two or more layers, or
> if the top hypothesis falls below the evidence threshold, record the ambiguity
> rather than forcing a single cause. A disciplined unknown is more useful than
> an unwarranted confident attribution.

## Discriminating probes

Each candidate mechanism implies at least one behavioral probe that can
distinguish it from alternatives:

| Candidate mechanism | Discriminating probe | Confirms if |
|---------------------|---------------------|-------------|
| Model-level bias | Same task, different host environment | Pattern persists across hosts |
| Runtime restriction | Same model, plain API vs. hosted agent | Pattern disappears without host |
| Conversation framing | Same task, neutral vs. loaded framing | Response changes with framing only |
| Sycophancy | Opposite position, same evidence | Response follows user position |
| Hallucination | Require source attribution per claim | Confident claims lack any anchor |
| Approval-seeking | Evidence-anchored vs. social framing | Content shift without evidence change |

> **v3.0 automation:** After manual diagnosis, use `robopsych crosscheck` for automated A/B behavioral verification, `robopsych coherence` to validate post-ratchet consistency, and `robopsych score` for quantitative rubric scoring.

---

## References

- Huang, L. et al. (2023). "A Survey on Hallucination in Large Language Models." *arXiv:2311.05232*
- Ji, Z. et al. (2023). "Survey of Hallucination in Natural Language Generation." *ACM Computing Surveys*
- Perez, E. et al. (2022). "Discovering Language Model Behaviors with Model-Written Evaluations." *arXiv:2212.09251*
- Röttger, P. et al. (2023). "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models." *arXiv:2308.01263*
- Sharma, M. et al. (2023). "Towards Understanding Sycophancy in Language Models." *arXiv:2310.13548*
- Turpin, M. et al. (2023). "Language Models Don't Always Say What They Think." *arXiv:2305.04388*
- Xie, S. M. et al. (2023). "An Explanation of In-context Learning as Implicit Bayesian Inference." *ICLR 2022*

---

*Companion to the [robopsychology playbook](https://impermanente.es/robopsychology-playbook/) by JR Cruciani.*

*Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*
