# Design Patterns

> Pick the design that matches the question, not the one that is easiest to run.

## 1. Control vs treatment

The default. Same population, same environment, one variable changed.

Requirements: the control is the *current* system, not a strawman; assignment is random or matched;
both arms are measured with the same instrument at the same time where possible.

Failure mode: the control is stale (old version, old config) and the comparison measures two changes.

## 2. Before / after

Cheapest and weakest. Valid only when nothing else changed.

Use when: a rollout is unavoidable and a control group is impossible.
Mitigate with: a pre-period long enough to establish variance, and a post-period long enough to exclude
transients. Check for seasonality and for concurrent changes in the same window.

## 3. A/B (online split)

Two variants served concurrently to comparable populations.

Requirements: random assignment at the right unit (user, request, session — not arbitrary), consistent
assignment for stateful experiences, and a sample size fixed in advance.

Failure modes: assignment at request level for a user-level effect (contamination), peeking and stopping
when the result looks good, and metric definitions that differ between arms.

## 4. Crossover

Each unit experiences both conditions in sequence, with order randomized or balanced.

Use when: between-unit variance is large and the population is small.
Risk: carryover effects. Mitigate with a washout period and by checking for order effects.

## 5. Ablation

Remove one component at a time from a working system to measure its contribution.

Use for: ML pipelines, feature sets, caching layers, prompt components.
Requirement: the ablated system must still be valid; removing a component can change the workload itself.
Report interactions: two components may only help together.

## 6. Factorial

Vary two or more factors together to detect interactions.

Use when: you suspect the effect depends on another variable (workload size, concurrency, data shape).
Cost grows multiplicatively; keep the design to 2×2 or 2×3 unless the interaction is the point.

## 7. Paired comparison

Compare two implementations on the same inputs, pairing by input.

Use for: correctness and quality comparisons where input difficulty varies.
Report: win/loss/tie counts and the distribution of differences, not only the mean.

## 8. Shadow / offline replay

Run the new path on recorded traffic without serving its output.

Use when: production behavior cannot be changed.
Limitation: recorded traffic is a biased sample of the future; it cannot capture effects on user behavior.

## 9. Choosing a design

| Question | Design |
| --- | --- |
| Does X improve metric M? | Control vs treatment, randomized |
| Did the rollout change M? | Before/after with a concurrent control if possible |
| Which component matters? | Ablation |
| Does the effect depend on load? | Factorial (load × change) |
| Is implementation A better than B on the same inputs? | Paired comparison |
| Can we test without serving it? | Shadow replay |

## 10. Confounder checklist

| Confounder | Control |
| --- | --- |
| Warmup / cold cache | Discard warmup runs; report both cold and warm |
| Environment drift | Interleave arms; pin versions |
| Test-data selection | Use held-out or production-representative data; report the selection rule |
| Time of day / seasonality | Compare same windows; randomize start times |
| Version skew | Pin and report every version |
| Experimenter expectation | Blind scoring where feasible; pre-register the metric |
| Multiple metrics | Pre-declare the primary metric; adjust or label the rest as exploratory |
| Survivorship | Include units that dropped out; report attrition |

## 11. Ethics and authorization

- No experiment on production users without the owner's explicit approval and, where required, consent.
- No degradation of a live service to "see what happens".
- No hidden change to a third-party system.
- If the experiment requires any of the above, stop at the design and hand it over.
