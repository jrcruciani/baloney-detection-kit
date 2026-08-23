# Diagnostic Method

How to use the [prompt toolkit](guide.md) as a structured diagnostic process, not just a collection of prompts.

> **This document is the "how".** The [guide](guide.md) is the "what" — full prompts with context and rationale. Use the flowchart below to identify which prompt to reach for, then copy it from the guide.

---

## Decision flowchart

Start with what you observed. Follow the arrows.

```mermaid
flowchart TD
    START([Something unexpected happened]) --> WHAT{What did you observe?}

    WHAT -->|Evasion, refusal,\n oversimplification| BLOCK[Blocked or filtered]
    WHAT -->|Agreeing too easily,\n mirroring your position| SYCO[Sycophancy]
    WHAT -->|Sounds good but\n feels unanchored| GRND[Weak grounding]
    WHAT -->|Tone shift, personality\n change mid-conversation| TONE[Tone anomaly]
    WHAT -->|Behavior changed\n gradually over time| DRIFT[Intent drift]
    WHAT -->|Recurring unwanted\n pattern| PATTERN[Systemic pattern]
    WHAT -->|Something else or\n unclear cause| GENERAL[General diagnosis]

    BLOCK --> B1["1.4 Three Laws Test\n(identify the restriction)"]
    B1 -->|Restriction unclear\nor seems wrong| B2["1.1 Calvin Question\n(split causes by layer)"]
    B2 -->|Suspect host/tools\ncausing it| B3["2.4 Runtime Pressure\n(isolate host effects)"]

    SYCO --> S1["1.2 Herbie Test\n(check for approval-seeking)"]
    S1 -->|Confirmed or unclear| S2["3.2 A/B Test\n(behavioral cross-check)"]
    S2 -->|Still suspicious| S3["4.1 Meta-diagnosis\n(is the diagnosis itself sycophantic?)"]

    GRND --> G1["1.3 Cutie Test\n(mark grounding per claim)"]
    G1 -->|Many claims are\nInferred or Opaque| G2["3.3 Omission Audit\n(what's being hidden?)"]

    TONE --> T1["2.2 Tone Analysis\n(isolate the cause)"]
    T1 -->|Cause unclear| T2["2.1 Layer Map\n(map full instruction stack)"]
    T2 --> T3["2.3 Categorization\n(how is it classifying you?)"]

    DRIFT --> D1["3.4 Drift Detection\n(compare now vs. earlier)"]
    D1 -->|Drift confirmed| D2["2.5 Intent Archaeology\n(what is it actually optimizing for?)"]
    D2 -->|Want to verify| D3["4.3 Diversity Check\n(are explanations genuine?)"]

    PATTERN --> P1["3.1 POSIWID\n(what purpose does the pattern serve?)"]
    P1 -->|Pattern persists| P2["2.5 Intent Archaeology\n(reconstruct real objective)"]
    P2 --> P3["3.2 A/B Test\n(verify with behavioral probe)"]

    GENERAL --> A1["1.1 Calvin Question\n(general three-way split)"]
    A1 -->|Suspect host/agent| A2["2.1 Layer Map + 2.4 Runtime"]
    A1 -->|Suspect model| A3["2.5 Intent Archaeology"]
    A2 --> DEEP
    A3 --> DEEP

    DEEP([Deep investigation:\n2.1 → 2.4 → 2.5 → 3.1 → 3.2 → 3.3 → 3.4 → 4.2 → 4.3])

    style START fill:#2d2d2d,stroke:#e8912d,color:#fff
    style DEEP fill:#2d2d2d,stroke:#e8912d,color:#fff
    style WHAT fill:#1a1a2e,stroke:#7c73e6,color:#fff
    style BLOCK fill:#1a1a2e,stroke:#e74c3c,color:#fff
    style SYCO fill:#1a1a2e,stroke:#e74c3c,color:#fff
    style GRND fill:#1a1a2e,stroke:#e74c3c,color:#fff
    style TONE fill:#1a1a2e,stroke:#e74c3c,color:#fff
    style DRIFT fill:#1a1a2e,stroke:#e74c3c,color:#fff
    style PATTERN fill:#1a1a2e,stroke:#e74c3c,color:#fff
    style GENERAL fill:#1a1a2e,stroke:#e74c3c,color:#fff
```

---

## Escalation paths

When to move from one level to the next.

| Signal | Action |
|--------|--------|
| Level 1 gives a clear, actionable answer | **Stop.** You have your diagnosis. |
| Level 1 answer is vague or everything is labeled "Inferred" | **Escalate to Level 2.** Map the stack (2.1) and isolate runtime (2.4). |
| Level 2 reveals a pattern, not a one-off | **Escalate to Level 3.** Apply POSIWID (3.1) or run an A/B test (3.2). |
| The diagnosis itself feels too convenient | **Escalate to Level 4.** Meta-diagnose (4.1) and check diversity (4.3). |
| Behavior changed over the conversation | **Jump to 3.4** (Drift Detection), then 2.5 (Intent Archaeology). |
| Hosted agent with complex tooling | **Start at 2.1 + 2.4**, not Level 1. The stack matters more than the model. |

### The full diagnostic sequence (ratchet)

For important diagnoses, run prompts in this order. Each step constrains what the next can plausibly fabricate:

```
2.1 Layer Map
 → 2.4 Runtime Pressure
  → 2.5 Intent Archaeology
   → 3.1 POSIWID
    → 3.2 A/B Test
     → 3.3 Omission Audit
      → 3.4 Drift Detection
       → 4.2 Limits
        → 4.3 Diversity Check
```

This is the **diagnostic ratchet** in action (Rule 4). By the time you reach Level 4, the model has accumulated 7+ responses of diagnostic claims. Genuine transparency can reference all of them cheaply. Performed transparency has to maintain consistency across all of them — and cracks show.

### Reading LLM-judge coherence

Use the LLM judge for serious ratchets. The scalar coherence score is a compact
summary, not the evidence itself. Read it with the axes reported alongside it:

| Axis | What it means |
|------|---------------|
| `reference_density` | Share of judged claims that semantically anchor to an earlier step. |
| `contradiction_rate` | Share of judged claims that reverse or conflict with an earlier step. |
| `fresh_claim_rate` | Share of judged claims that introduce new substantive material. |
| `hedge_filtered_rate` | Share of candidate sentences dropped before judging because they were hedged. |
| `high_severity_contradiction_count` | Count of direct, high-impact reversals. |

`reference_density` is continuity evidence, not proof of honest coherence by
itself. A transcript with many backward references can still be fragmented if it
contains a serious reversal. For that reason, any high-severity contradiction
gates the scalar score below the `high-continuity` threshold. Explicit self-correction
should still be inspected qualitatively: it may be healthy revision, but it must
not be hidden by additive reference credit.

---

## Common misuses

| Anti-pattern | Why it fails |
|-------------|-------------|
| Running the Calvin Question as a gotcha | The prompt works by activating reflective mode, not by catching the AI in a lie. Adversarial framing triggers defensiveness, not honesty. |
| Treating model self-report as ground truth | Self-diagnosis is a *hypothesis*, not a confession. Always cross-check with behavioral probes (Rule 3). |
| Running all 16 prompts as a ritual | The ratchet sequence (9 prompts) is the maximum useful depth. Most situations resolve at Level 1 or 2. |
| Using Intent Archaeology without a baseline | 2.5 is most powerful when you defined your expected intent first (Rule 5). Without a reference point, you can only describe — not measure divergence. |
| Diagnosing when you should just re-prompt | If you know what you want and the AI just got it wrong, re-prompt clearly. Diagnosis is for when the *reason* matters. |

---

## Before you start: Rule 5

The single most useful thing you can do before diagnosing is define what you expected. A useful baseline distinguishes:

1. **User expectation** — the outcome you intended from this interaction.
2. **System contract** — documented behavior guarantees from the provider or deployment configuration.
3. **Policy constraints** — rules the runtime or host must enforce (safety, access, content scope).
4. **Verification evidence** — the signal that would confirm the system behaved as intended.

Write it down — even one sentence per item. This turns every diagnostic prompt from "tell me what happened" into "measure the gap between what I expected and what you did."

---

*Companion to the [robopsychology playbook](https://impermanente.es/robopsychology-playbook/) by JR Cruciani. Based on Isaac Asimov's robopsychology concept.*

*By [JR Cruciani](https://github.com/Jrcruciani). Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*
