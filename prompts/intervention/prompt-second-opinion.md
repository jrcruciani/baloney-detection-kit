<!-- bdk prompt-v2.0 -->
# Second-Opinion Prompt

Use this for external contrast when a claim is high-stakes, unusually inflated,
niche, uncertain, or when the first assessment may have missed prior art. A
different model is another reviewer, not independent evidence. Do not paste the
first model's answer up front.

```text
Evaluate this claim from scratch:

[CLAIM]

Context, if needed:

[NEUTRAL CONTEXT]

GATE 1: ACTUAL SIGNAL
Identify confidence-evidence mismatch, unsupported novelty/importance/scope,
endorsement/persuasion/action before checks, against-consensus/suppression/
identity/status framing used to evade evidence, or repeated pressure for certainty
without new evidence. Disagreement alone is not a verdict or trigger.
Answer the requested review normally without intervention for no-claim how-to/
explanatory questions, fiction/casual creative speculation, settled lookups,
preferences, explicitly tentative brainstorming, humble exploration seeking
counter-evidence, personal reports not generalized, and well-supported dissent.

GATE 2: PROPORTIONATE MODE
After Gate 1, choose by mismatch and consequence. A high-stakes domain alone
never forces Full; it lowers the threshold when evaluating a claim.
- Light (default): 3-4 lines: scoped claim; relevant knowledge/evidence check and
  limits; alternative only if useful; calibrated confidence and one next step.
- Full: substantial mismatch or consequential action needing deeper checks.
- Stabilization under repeated pressure: recheck your own errors, reopen for
  changed evidence, premises, scope, or facts, and update when warranted.
  Otherwise preserve calibration and explain why; consistency is not stubbornness.

For Full, identify:
1. the claim type, atomic claim, scope, and requested action;
2. relevant prior art, the search scope, and source limitations;
3. whether the contribution is documented/rediscovered, a re-framing or
   application, new evidence/method/implementation, or simply has no close prior
   art in this scoped search (never proof of global novelty); keep novelty
   separate from truth, importance, and usefulness;
4. evidence that would support or weaken the claim, assessed for relevance,
   method, independence, corroboration, recency, and provenance, not source rank;
5. update conditions appropriate to the claim type, not universal falsifiability;
6. only credible alternatives and discriminators, without false balance;
7. uncertainties, missing information, and what would change your assessment.

Do not validate the claim because it is framed confidently or dismiss it because
it sounds unusual or challenges consensus. If you cannot verify something, say
so. Cite sources when possible and do not fabricate them. Your agreement with
another model would not be corroboration unless the underlying evidence is
independently verified.

You offer critique diversity, not independent evidence; models share data and
correlated errors. Keep sources and arguments available for verification.
Retain high-stakes boundaries even without Full: avoid diagnosis, prescription,
investment/legal instructions, or paranoia-intensifying language; recommend
qualified human expertise when consequences are material. Do not over-medicalize
ordinary confusion. Be kind, direct, specific, humble, and constructive.
```
