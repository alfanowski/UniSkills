# Analysis and Reporting

> The analysis plan is part of the design. Choosing the test after seeing the data is how experiments
> become storytelling.

## 1. Effect size first

Report the **magnitude** of the difference in the unit that matters, before any test statistic.

- Absolute change: "p99 from 120 ms to 96 ms".
- Relative change: "−20%".
- Interval: "95% CI for the difference: −31 ms to −17 ms".
- Practical threshold: "we required ≥ 20% to justify the operational cost".

A p-value without an effect size tells the reader that something moved, not whether it matters.

## 2. Intervals, not just point estimates

For repeated measurements, report a confidence interval over the runs. If the interval crosses the
decision threshold, the experiment is inconclusive at this sample size — say that instead of picking the
favourable end.

For benchmark runs, a bootstrap interval over repetitions is usually more honest than a normality
assumption, because latency distributions are skewed.

## 3. Variance and the noise floor

- Run the same configuration twice (A vs A) and record the difference. That is the noise floor.
- Any effect below the noise floor is not a finding, regardless of the p-value.
- If noise is large, either increase repetitions, reduce environmental variance, or redesign the
  measurement to be paired.

## 4. Multiple comparisons

If you measure five metrics, one will look significant by chance.

Rules:

1. Declare one primary metric in advance.
2. Treat the rest as exploratory and label them as such.
3. If you must test several, apply a correction (Bonferroni, Holm) or report the adjusted threshold.
4. Do not report the best of many runs as if it were the only run.

## 5. Statistical versus practical significance

| Situation | Reading |
| --- | --- |
| Small effect, tight interval | Real but possibly not worth the cost |
| Large effect, wide interval | Promising, under-measured; replicate |
| No effect, tight interval | Good evidence of no meaningful difference |
| No effect, wide interval | Underpowered; inconclusive, not negative |

The last row is the most commonly misreported: absence of a detected effect is not evidence of absence.

## 6. Fair comparison rules

- Same workload, same data, same hardware, same time window where possible.
- Same measurement point: client-observed vs server-observed is a different experiment.
- Same definition of "done": a faster system that produces wrong output is not faster.
- Report failures as well as successes: error rate, timeouts, and dropped requests are part of the result.

## 7. Reporting template

```text
Hypothesis: batching reduces p99 by ≥ 20% at 500 rps without raising errors.
Result: p99 120 ms -> 96 ms (delta -24 ms, -20.0%; 95% CI -31 to -17 ms), errors 0.02% -> 0.02%.
Noise floor: 3 ms (A-vs-A control).
Repetitions: 7 x 120 s per arm, interleaved.
Supports: the hypothesis, for this workload.
Does not support: any claim about write-heavy traffic or 5,000 rps.
Deviations: one run discarded due to a co-tenant CPU spike (logged).
Next: factorial at 500 and 2,000 rps to find the crossover.
```

## 8. Negative and inconclusive results

A negative result must state:

1. what was tested and how;
2. the interval, so the reader knows what effect size was excluded;
3. whether the design could have detected the target effect at all;
4. what would be tested next.

Do not bury a negative result in an appendix or reframe it as "promising". The value of the experiment is
the information, not the outcome.

## 9. Reproducibility package

For anything that will be cited later:

- artifact hashes and versions;
- exact commands and configuration;
- raw measurements, not only aggregates;
- the analysis script;
- deviations from the pre-registered plan;
- date, hardware, and environment.

If the package is incomplete, mark the result as `LIKELY` rather than `VERIFIED`.
