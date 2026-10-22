# Experiment Plan

> Use for `experiment-design-and-falsification`. Written before the run; the result section is filled
> after, and the plan is not edited retroactively.

```markdown
# Experiment: <title>

**Hypothesis:** <direction + magnitude + population + conditions>
**Decision:** positive -> <action> | negative -> <action> | inconclusive -> <action>
**Owner / date:** ...

## Design

- Independent variable: ...
- Dependent variable: <metric, unit, aggregation, measurement point>
- Control: <the current system, precisely>
- Treatment: <the change, precisely>
- Assignment: randomized | paired | crossover | before-after
- Repetitions: <n> | Warmup: <policy> | Noise floor: <measured A-vs-A delta>

## Confounders

| Confounder | Strategy | Residual risk |
| --- | --- | --- |
| Environment drift | interleave arms | |
| Warmup / cache | discard first N | |
| Workload difference | fixed corpus | |
| Metric definition | declared above | |

## Pre-registered analysis

- Primary metric: ...
- Stopping rule: ...
- Exclusions: ...
- Method: <effect size + interval; test if applicable>

## Result

- Control: <value ± interval> | Treatment: <value ± interval>
- Effect: <absolute> (<relative>), 95% CI <low..high>
- Practical significance: yes | no | uncertain
- Deviations from plan: ...

## Interpretation

- Supported: ...
- Not supported: ...
- Confounded by: ...

## Next

- <one follow-up that would be most informative>
```

## Rules

- The stopping rule is written before data collection. Editing it afterwards converts the experiment into
  a search for a favourable number.
- Report the interval. A point estimate hides the uncertainty that the decision depends on.
- Negative results are results. State the effect size that was excluded.
