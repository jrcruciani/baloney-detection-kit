# Robopsychology Framework

This directory is the canonical home of the method.

Robopsychology diagnoses one suspicious AI behavior at a time by separating it
into three layers:

1. **Model** - base-model tendencies, fine-tuning habits, style defaults,
   approval-seeking.
2. **Runtime/host** - system prompts, policies, tools, workflow rules, memory,
   session constraints.
3. **Conversation** - framing, local context, inferred user profile, recent
   assumptions.

## Reading order

| Start here | Purpose |
|------------|---------|
| [`manual-diagnosis.md`](manual-diagnosis.md) | Use the framework without the CLI |
| [`guide.md`](guide.md) | Full prompt toolkit and epistemic note |
| [`method.md`](method.md) | Decision flowchart, escalation paths, common misuses |
| [`taxonomy.md`](taxonomy.md) | Observation -> failure mode -> prompt mapping |
| [`falsifiability.md`](falsifiability.md) | How to keep diagnoses testable |
| [`deployment-contexts.md`](deployment-contexts.md) | When this belongs in an AI lifecycle |
| [`related-work.md`](related-work.md) | Positioning against benchmarks, evals, red teaming |
| [`versioning.md`](versioning.md) | Framework vs prompt toolkit vs CLI version tracks |

The prompt cards live in [`../prompts/cards/`](../prompts/cards/). The reusable
worksheets live in [`../templates/`](../templates/).
