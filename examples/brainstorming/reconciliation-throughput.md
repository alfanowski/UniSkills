# Example: Making a Six-Hour Reconciliation Fit in Thirty Minutes

> Synthetic example. Numbers are illustrative, not measurements.

## The request

> Our billing reconciliation job reads 40M ledger rows and matches them against a payments table. It takes
> about six hours and must finish in under thirty minutes. Auditability is contractual: we must be able to
> explain any mismatch for seven years. How should we approach it?

## Constraints and criterion

- **Hard:** Postgres stays; audit trail is contractual; no downtime window for the billing service.
- **Soft:** team of four, no dedicated data platform, on-call already loaded.
- **Optimizing for:** time to a defensible result, weighted above elegance.

## Options

| # | Option | Mechanism | Makes easy | Makes hard | Build | Operate | Reversible | Time to signal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Status quo, tuned | Add composite index, partition the scan by day, run 7 parallel workers | No schema change, no new system | Still full-table work; partition count grows linearly with history | S | Low | Trivial | Days |
| 2 | Incremental reconciliation | Persist a watermark per (account, day); recompute only changed partitions, keep a full sweep weekly | Cost scales with change volume, not history | Requires a correct change-detection signal and a backfill for existing history | M | Medium | Costly (watermark bugs are data bugs) | Weeks |
| 3 | Immutable event log + derived ledger | Append-only events become the source of truth; ledger is a materialized projection | Audit becomes inherent; recompute any date range cheaply | Rewrites the write path; migration of historical state; new failure modes | XL | High | One-way door | Months |
| 4 | Offload matching to a columnar store | Nightly CDC into a columnar engine; reconciliation runs there; Postgres stays system of record | 10–50x scan throughput; isolates heavy reads from the OLTP path | Second system to operate; CDC lag; consistency questions during incidents | L | Medium-High | Costly | Weeks |
| 5 | Do nothing, negotiate the SLA | Re-baseline the contractual window with evidence | Zero build | Doesn't solve the underlying growth; may be unacceptable | — | — | Trivial | Days |

## Pre-mortem on option 2 (the leading candidate)

- **Watermark correctness.** If the change-detection signal misses a late-arriving payment, the mismatch
  never surfaces. Mitigation: the weekly full sweep is not optional, and a mismatch must page.
- **Backfill ambiguity.** The first run has no watermark. Without an explicit "history trusted until"
  marker, the team cannot tell whether an old mismatch was reconciled or never scanned.
- **Operational silence.** Incremental jobs fail quietly because they process less work, not more.
  Mitigation: emit covered-partition counts and alert on a drop, not on an error.

## Recommendation

Choose **#2** if the change volume per day is a small fraction of total history — the common case for
billing. Choose **#1** only if the 40M-row scan is already close to the target after indexing. Choose
**#4** if #2's watermark cannot be made trustworthy, because a columnar offload preserves the Postgres
system of record without rewriting the write path. **#3** is the right long-term architecture and the wrong
first move: it is a one-way door, and this team cannot carry it this quarter.

## Cheapest discriminating experiment

- **What:** run option 1's index plus day-partitioned parallel scan against a production-sized snapshot.
- **Time box:** two days.
- **Decision rule:** if it lands under 45 minutes, do #1 and stop. If it lands between 45 and 90 minutes,
  do #2. If it is still above 90, the bottleneck is not scan throughput and #4 will not save you either —
  return to the cost model before choosing.

## Rejected options

| Option | Why rejected now | Revisit if |
| --- | --- | --- |
| #3 | One-way door, quarter-scale rewrite, team has no data-platform capacity | Reconciliation becomes a product surface, or audit requirements expand |
| #5 | Growth makes the window worse every quarter | Contract renegotiation is on the table |
| #4 | Operationally heavier than the team can absorb before the deadline | #2's watermark proves untrustworthy |

## What this example demonstrates

- Five options that differ in **mechanism**, not in tool choice.
- The status quo and "do nothing" are explicit, so the comparison is honest.
- The recommendation is conditional and names the condition that flips it.
- The experiment is cheap, discriminating, and has a numeric decision rule.
- The pre-mortem produced mitigations, not a decorative risk list.
