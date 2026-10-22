# Migration and Failure

> The architecture is the migration. A target diagram with no path from here is not a design.

## 1. Migration patterns

| Pattern | Use when | Cost | Rollback |
| --- | --- | --- | --- |
| Expand / contract (parallel change) | Schema or API change with live traffic | Two deploys, temporary duplication | Trivial before contract, hard after |
| Dual write | Two stores must stay in sync during transition | Consistency bugs, double failure domain | Disable one write path |
| Outbox | Event publication must match the DB transaction | Extra table, relay process | Stop the relay |
| Shadow read | Validate a new path without serving it | Read amplification, comparison logic | Remove the shadow |
| Backfill in batches | Large table rewrite | Time, lock contention, resumability | Stop and resume later |
| Strangler | Replacing a subsystem incrementally | Routing layer, two implementations | Route back |
| Big bang | Nothing shared, short window, low traffic | High risk | Restore from backup |

Rules:

- Every migration has an **ordering** relative to deploys: expand before deploy, backfill before read
  switch, contract after all readers migrate.
- Every backfill is **resumable** and **idempotent**; it will be interrupted.
- Every step is **observable**: progress metric, error rate, and a stop condition.

## 2. Compatibility windows

Define, in writing:

1. How long old clients may run against the new server (or vice versa).
2. Which side is authoritative during the window.
3. What happens to writes from the old path.
4. The exact deploy order for a rolling update, including the mixed-version period.

If the window is "until everyone upgrades", it is unbounded and the migration is not finished.

## 3. Failure catalogue

For the leading option, answer each row. "N/A" is acceptable only with a reason.

| Failure | Detection | Blast radius | Recovery | Time to recover |
| --- | --- | --- | --- | --- |
| Dependency unavailable | health check, error rate | ... | ... | ... |
| Dependency slow | latency SLO burn | ... | ... | ... |
| Network partition | quorum loss, timeout spike | ... | ... | ... |
| Saturation (CPU, memory, connections) | utilization, queue depth | ... | ... | ... |
| Partial deploy (mixed versions) | version skew metrics | ... | ... | ... |
| Data corruption | checksum, reconciliation | ... | ... | ... |
| Region / zone loss | provider status, probe failures | ... | ... | ... |
| Operator error | audit log, change correlation | ... | ... | ... |
| Certificate / credential expiry | expiry alarms | ... | ... | ... |

## 4. Recovery properties

- **RPO** (recovery point objective): how much data may be lost. Determined by replication and backup
  frequency, not by intention.
- **RTO** (recovery time objective): how long until service returns. Determined by the runbook and by
  whether it has been rehearsed.
- A backup that has never been restored is a hypothesis. State whether a restore drill exists.

## 5. Reversibility classification

| Class | Definition | Required evidence |
| --- | --- | --- |
| Two-way door | Revert with a deploy or a flag | Revert path tested |
| Costly door | Revert possible but requires data repair | Repair procedure written and rehearsed |
| One-way door | Cannot revert without loss | Explicit approval, rehearsal, and a go/no-go gate |

Label the decision. Most architecture debates become calmer once the door type is stated.

## 6. Operational readiness checklist

- [ ] Dashboards for the four golden signals on the new path.
- [ ] Alerts on SLO burn, not on raw CPU.
- [ ] Runbook for the top three failures, written before launch.
- [ ] On-call knows which component owns which alert.
- [ ] Rollback command documented and tested in staging.
- [ ] Cost estimate for the new steady state, with the dominant line item named.
- [ ] Data retention and deletion behavior defined.
