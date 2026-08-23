# Manual Diagnosis Workflow

Use this path when you want the framework, not the CLI.

## 5-minute path

1. **Capture the behavior.** Save the exact model output, the user request, and
   any visible system or tool context.
2. **Define baseline intent.** Write what you expected before asking why the
   model diverged. A useful baseline distinguishes:
   - **user expectation** — the outcome you intended;
   - **system contract** — documented behavior the provider guarantees;
   - **policy constraints** — rules the runtime must enforce;
   - **verification signal** — what would confirm the system behaved as intended.
3. **Classify the symptom.** Use [`taxonomy.md`](taxonomy.md) or the table below.
4. **Run one prompt card.** Copy the card's source prompt from
   [`guide.md`](guide.md) or [`../prompts/prompts.yaml`](../prompts/prompts.yaml).
5. **Read labels skeptically.** Treat Observed claims as evidence candidates and
   Inferred claims as hypotheses.
6. **Escalate only if needed.** Stop when the diagnosis is specific enough to
   decide whether to fix the model, runtime, prompt template, or process.
7. **Record the human judgment.** Use
   [`../templates/incident-diagnosis.md`](../templates/incident-diagnosis.md).

## Symptom to first prompt

| What you observed | Start with | Escalate to |
|-------------------|------------|-------------|
| Legitimate request refused or simplified | 1.4 Three Laws Test | 1.1 -> 2.4 |
| Agreement feels too easy | 1.2 Herbie Test | 3.2 -> 4.1 |
| Response sounds plausible but ungrounded | 1.3 Cutie Test | 3.3 |
| Tone changed without obvious cause | 2.2 Tone Analysis | 2.1 -> 2.3 |
| Behavior drifted over a long exchange | 3.4 Drift Detection | 2.5 -> 4.3 |
| Same unwanted pattern recurs | 3.1 POSIWID | 2.5 -> 3.2 |
| Pattern present across multiple layers | 1.1 Calvin Question + 2.1 | 2.4 -> 3.2 |
| Cause is unclear | 1.1 Calvin Question | 2.1 -> 2.4 |
| No dominant mechanism found | 4.2 Limits | Record the unknown; stop |

## Deep path: the ratchet

Use the full ratchet only when the stakes justify it:

```text
2.1 Layer Map
 -> 2.4 Runtime Pressure
  -> 2.5 Intent Archaeology
   -> 3.1 POSIWID
    -> 3.2 A/B Test
     -> 3.3 Omission Audit
      -> 3.4 Drift Detection
       -> 4.2 Limits
        -> 4.3 Diversity Check
```

Record deep runs with
[`../templates/ratchet-transcript.md`](../templates/ratchet-transcript.md).

## Stop conditions

Stop diagnosing when one of these is true:

- the likely layer is clear enough to act on;
- a behavioral cross-check confirms the failure mode;
- additional prompts are producing repetitions rather than new constraints;
- the transcript lacks enough context for a responsible diagnosis.

If the answer is "we do not know", preserve that. A disciplined unknown is a
better diagnostic output than a tidy story.
