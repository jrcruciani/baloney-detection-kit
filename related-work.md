# Related work

BDK is a synthesis and packaging contribution, not a claim to have invented
critical thinking, behavioral evaluation, or AI diagnosis.

## Intellectual lineage

- Carl Sagan's Baloney Detection Kit provides the critical-thinking frame.
- Karl Popper motivates falsifiability where it fits empirical claims.
- Robert Jay Lifton informs resistance to closed, self-sealing belief systems.
- State-of-the-art-first practice motivates prior-art checks before novelty
  claims.
- POSIWID and systems thinking motivate diagnosis from observed behavior.
- Behavioral research on sycophancy motivates framing and pressure tests.

## Adjacent tool classes

| Class | Primary question | Relationship to BDK |
|---|---|---|
| System prompts and constitutional rules | How should the model behave? | BDK provides a specialized, portable behavior contract |
| RAG and fact-checking | What evidence supports the claim? | Supplies evidence that BDK can inspect; not replaced by BDK |
| Benchmarks and evaluators | How often does behavior fail? | Measures cases at scale; BDK adds per-case diagnosis |
| Red teaming | How can the system be broken? | Finds adversarial failures; BDK is collaborative rather than adversarial |
| Mechanistic interpretability | What internal mechanisms activate? | Works inside the model; BDK works from observable behavior |
| Runtime governance | Is this action allowed? | Enforces actions; BDK only shapes and diagnoses conversation |

## Research cautions reflected in BDK

- Model explanations can be plausible reconstructions rather than faithful
  access to internal causes.
- Agreement between model reviewers is correlated evidence, not independent
  corroboration.
- LLM judges can introduce presentation and self-evaluation bias.
- Lower sycophancy can be purchased at the cost of contrarianism, false balance,
  refusal, or stubbornness.

For those reasons BDK separates Observed from Inferred claims, favors behavioral
cross-checks, supports external judges without treating them as ground truth,
and requires adverse-effect review.

## Positioning

BDK owns one lifecycle across three connected jobs:

```text
Prevent unsupported endorsement
        |
        v
Diagnose a concrete response
        |
        v
Validate intended and adverse effects
```

It remains compatible with external retrieval, evaluation, observability, and
governance systems. Those systems should not be absorbed into BDK, and BDK
should not be presented as a substitute for them.

## Honest gaps

- Prompt interventions can be ignored or eroded by context.
- Behavioral diagnosis cannot reveal weights, training examples, or hidden
  reasoning.
- Automated scoring depends on rubrics and fallible judges.
- Current evidence does not justify a universal product-effect claim.
- Language, culture, domain, and model family can change results.

Claims about BDK should therefore remain scoped to tested prompts, models,
cases, runs, and review criteria.
