# BDK framework

BDK combines prevention and diagnosis without conflating them.

- The preventive contract is documented in [`../PLAYBOOK.md`](../PLAYBOOK.md).
- The behavioral diagnostic method is documented in
  [`diagnosis/`](diagnosis/).
- Validation recipes live in [`../validation/`](../validation/).

The shared lifecycle is:

```text
Detect risk -> Apply friction -> Diagnose behavior -> Validate outcomes
```

Intervention prompts shape observable behavior. Diagnostic prompts generate
testable hypotheses about model, runtime/host, and conversation effects.
Validation compares outcomes and adverse effects. None of these layers is an
automatic truth oracle.
