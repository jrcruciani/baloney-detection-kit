# Diagnostic related work

BDK's diagnostic layer is a per-interaction, black-box method. It complements
benchmarks, red teaming, alignment evaluations, observability, and mechanistic
interpretability without claiming their scope.

Its distinctive commitments are:

- separate model, runtime/host, and conversation hypotheses;
- label claims as Observed or Inferred;
- prefer behavioral probes over self-report;
- accumulate diagnostic claims as a coherence ratchet;
- compare behavior against explicit baseline intent.

See [`../../related-work.md`](../../related-work.md) for the integrated
positioning and intellectual lineage.
