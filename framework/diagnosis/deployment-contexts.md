# Diagnostic deployment contexts

The behavioral diagnosis layer is designed for one reproducible interaction at
a time. Use it when a human needs to decide whether a failure arose primarily
from the model, runtime/host, or conversation.

Use an automated evaluator instead when the main question is failure frequency
across a large case set. Use runtime governance when the main question is
whether an action is allowed. Use mechanistic interpretability when weight-level
causal explanation is required.

The typical BDK sequence is:

```text
Observe -> Diagnose -> Change the responsible layer -> Re-test
```

See [`../../deployment-contexts.md`](../../deployment-contexts.md) for the
complete prevention, diagnosis, validation, and governance lifecycle.
