# Measurement Protocol

> An unmeasured claim is a hypothesis. A badly measured claim is worse, because it looks like evidence.

## 1. Before measuring

- Write the metric, the unit, and the aggregation (mean, p50, p99, max) **before** running anything.
- Freeze the workload: same input distribution, same concurrency, same data size, same warm/cold state.
- Record the environment: CPU model, core count, memory, OS version, runtime version, compiler flags,
  container limits, and whether the machine is shared.
- Decide the decision rule: "if p99 drops below X, adopt". Without it, you will rationalize whatever
  number appears.

## 2. Benchmark hygiene

| Requirement | Why |
| --- | --- |
| Warmup runs excluded from results | JIT, caches, connection pools, page faults |
| ≥ 5 repetitions, report spread | A single run cannot distinguish signal from noise |
| Report median and tail, not only mean | Means hide bimodal latency |
| Same machine for A and B | Cross-machine comparisons are not comparisons |
| Alternate A/B runs | Drift affects the last-run group most |
| Fixed CPU frequency / no thermal throttling | Mobile and laptop CPUs change clocks |
| Isolated from other workloads | Noisy neighbors dominate small differences |
| Workload validated against production | Synthetic workloads optimize for the synthetic case |

## 3. Variance and noise

- Estimate noise first: run the same configuration twice and measure the difference. Any effect smaller
  than this is not a finding.
- Report absolute and relative change together ("−1.8 ms, −12%").
- If the distribution is bimodal, investigate before averaging; the modes usually mean two different
  code paths or two different cache states.
- Use confidence intervals for repeated measurements, and state the method. Do not compute a p-value for
  a single run.

## 4. Tails

- p99 is where queueing and GC live. A change that improves the mean and worsens p99 is usually a
  regression in user experience.
- Compare tails only at the same load. Tail latency at 10% utilization says little about 80%.
- If the tail is dominated by a rare event (compaction, token refresh, DNS), name it; optimizing the
  common path will not move it.

## 5. Profiling

- Sampling profilers show statistical distribution; they miss short but frequent calls less than they
  miss rare expensive ones. Interpret accordingly.
- Distinguish **inclusive** (self + callees) from **exclusive** (self only) time before naming a
  bottleneck.
- A profile from a synthetic benchmark may not match production; say which one you used.
- Allocation profiles and CPU profiles answer different questions; do not substitute one for the other.

## 6. Comparative claims

For "A is faster than B":

1. Same work: identical input, identical output requirement, identical correctness constraints.
2. Same resources: cores, memory limit, network.
3. Same starting state: cold caches for cold-start claims, warm for steady-state claims.
4. Same measurement point: client-observed or server-observed, but stated.
5. Same version family, and the comparison dated.

If any of these cannot be equalized, report the difference as a confound rather than hiding it.

## 7. Reporting template

```text
Metric: p99 latency, ms, server-observed
Workload: 500 rps, 8 KiB payloads, 80/20 read/write, dataset 20 GB
Environment: 8 vCPU, 32 GB, kernel X, runtime Y, same host for A and B
Method: 60 s warmup, 5 × 120 s runs, alternating A/B
Result: A 41.2 ms (σ 1.8), B 36.4 ms (σ 1.1), delta −4.8 ms (−11.7%)
Noise floor: 0.9 ms from A-vs-A control
Caveat: dataset fits in page cache; cold-start behavior not measured
```
