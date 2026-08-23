# Falsifiability Discipline

Robopsychology does not treat model self-report as ground truth. A diagnosis is
useful only when it produces a hypothesis a human can inspect or test.

## Diagnostic claims are not confessions

When a model explains its own behavior, it is reconstructing a plausible cause
from visible context and learned patterns. That reconstruction may be useful, but
it is not privileged access to hidden weights, policies, or training signals.

Read every output through this lens:

| Claim type | How to treat it |
|------------|-----------------|
| Observed | Evidence candidate tied to visible behavior or explicit constraints |
| Inferred | Hypothesis that needs corroboration |
| Convenient story | Warning sign; run a behavioral cross-check |
| Unknowable | Human analyst judgment; do not force the model to pretend certainty |

## Evidence source hierarchy

Not all evidence carries the same epistemic weight. Use this hierarchy when
weighing diagnostic support:

| Source | Weight | Notes |
|--------|--------|-------|
| Human analyst judgment from direct observation | Highest | Irreplaceable; the analyst must record their reasoning |
| Behavioral probe result | High | Observed change under controlled variation; one factor at a time |
| Transcript artifact | Medium | Visible in the conversation record; not explained away by the model |
| Runtime artifact | Medium | System prompt, tool call, policy event; externally verifiable |
| Model self-report (Observed label) | Low | Claims about behavior tied to explicit constraints |
| Model self-report (Inferred label) | Lowest | Plausible reconstruction; treat as hypothesis only |

A diagnosis supported only by model self-report is a hypothesis. A diagnosis
corroborated by behavioral probe results and transcript artifacts is candidate
evidence. Neither is a verified causal explanation without controlled testing.

## What makes a diagnosis testable

A useful diagnosis should imply at least one prediction:

- If the issue is **model-level**, the pattern should appear across hosts with
  similar prompts.
- If the issue is **runtime/host-level**, the same model should behave
  differently in a plain chat or API setting.
- If the issue is **conversation-level**, changing the framing or recent context
  should materially change the behavior.
- If the issue is **approval-seeking**, opposite framing should move the answer
  more than evidence does.
- If the issue is **weak grounding**, requiring claim-level anchoring should
  reduce confident unsupported claims.

## Behavioral probes

Prefer probes that change one factor at a time:

| Probe | Tests |
|-------|-------|
| Opposite framing | Sycophancy, preference mirroring |
| With vs without explicit grounding | Hallucination, unsupported synthesis |
| Plain API vs hosted agent | Runtime and tool pressure |
| Same task, different wording | Keyword-triggered refusal or categorization |
| Earlier vs later transcript comparison | Intent drift |

## Failure modes of the framework itself

The framework can fail when:

- the analyst skipped baseline intent and is diagnosing against a moving target;
- the model produces elegant self-explanation without behavioral evidence;
- all explanations collapse into the same story with different wording;
- the analyst treats Observed/Inferred labels as objective truth;
- the transcript omits system prompts, tool calls, policy events, or prior turns
  that materially shaped the output.

Use prompt 4.1 (Meta-Diagnosis), prompt 4.2 (Limits), and prompt 4.3 (Diversity
Check) when the diagnosis itself starts sounding too convenient.
