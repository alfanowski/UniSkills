# Example: Checking a "10x Faster" Benchmark Claim

> Synthetic example. The vendor, product, and numbers are invented; the reasoning is the point.

## The claim

> "Our vector index is 10x faster than pgvector at 1M vectors, with 99% recall."

Context: the decision is whether to adopt it for a 50M-vector corpus with a strict recall floor and a
latency SLO of 80 ms p99.

## Answer

**Reported, not established.** The 10x figure is a vendor measurement on a dataset 50x smaller than the
target, and the claim does not state the recall at which the comparison was run. The figure cannot be
carried into the 50M-vector decision. What can be carried: the vendor's own numbers suggest a real
throughput advantage at 1M vectors, which justifies a paid experiment, not an adoption.

**Confidence:** medium for "the index is faster at small scale"; `UNKNOWN` for the 50M case.

## Findings

### Q1 — Is the benchmark comparable to our workload?

- **Reported:** 10x QPS at 1M vectors, 99% recall, single node.
- **Not stated:** hardware, dimensionality, index build parameters, query distribution, whether the
  baseline used the same recall target, and whether the measurement is client- or server-side.
- **Why it matters:** ANN benchmarks are extremely sensitive to `ef_search`/`nprobe`. A system tuned to
  99% recall compared against one tuned to 95% will look faster for reasons unrelated to the index.
- **Verdict:** `LIKELY` that the comparison is favorable to the vendor; not usable as-is.

### Q2 — Does the advantage survive at 50M vectors?

- **Unknown.** Index behavior at 50M is dominated by memory layout and disk access patterns. A structure
  that fits in RAM at 1M may spill at 50M, changing the curve entirely.
- **What would resolve it:** a run at 50M on hardware matching the production class, with recall measured
  at the same target and p99 reported.

### Q3 — Is the recall floor compatible with the latency target?

- **Derived:** at a strict recall floor, ANN parameters must be raised, which increases per-query work.
  The 10x figure at an unstated recall setting says nothing about the latency at *our* recall setting.
- This is the most likely place for the claim to fail, and the cheapest to test.

## Contradicting evidence

| Source | Claims | Conflicts with | Relevance |
| --- | --- | --- | --- |
| Independent benchmark blog (synthetic) | 2–3x at 10M, not 10x | Vendor headline | Different scale and recall target; directionally consistent with "advantage shrinks with scale" |
| Issue tracker (synthetic) | Memory growth above 20M requires sharding | Single-node 50M assumption | Changes the deployment shape, not just the speed |

## Source ledger

| # | Source | Version/date | Accessed | Tier | What it says |
| --- | --- | --- | --- | --- | --- |
| 1 | Vendor announcement | 2026-09 | 2026-10-22 | 3 (interested) | "10x at 1M, 99% recall" — no method section |
| 2 | Vendor docs, tuning guide | v2.1 | 2026-10-22 | 3 | recall/latency trade-off controlled by a single parameter |
| 3 | Independent benchmark post | 2026-08 | 2026-10-22 | 5 | 2–3x at 10M, methodology described |
| 4 | Project issue tracker | open issues | 2026-10-22 | 4 | memory pressure above ~20M vectors |

## Limits

- No access to the vendor's benchmark harness; the method cannot be reproduced from the announcement.
- The independent benchmark used a different dataset and dimensionality.
- No production hardware was available, so no measurement of our own was possible.

## What would change this answer

- A 50M-vector run at our recall target showing p99 under 80 ms would move the conclusion to `LIKELY`
  adopt, pending operational review.
- Evidence that the 10x was measured at the same recall target and on comparable hardware would raise
  Q1 from `LIKELY` to `VERIFIED`, but still would not settle Q2.

## Recommended next step

Run a two-day bake-off on a 10M-vector subset first — it is cheap, and if the advantage has already
collapsed by 10M, the 50M question is moot.
