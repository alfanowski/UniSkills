# Failure Taxonomy

> Classify before you probe. The class narrows the search space and tells you which observations are
> even relevant.

## 1. Logic

**Signature:** deterministic, input-dependent, reproducible with a known value.

- Off-by-one at boundaries; empty/one/many.
- Inverted condition, wrong operator, wrong precedence.
- Type coercion, truncation, signedness.
- Wrong default, stale constant, copy-paste of a sibling branch.
- Incorrect date/time arithmetic, timezone assumptions.

**Probe:** smallest failing input, then smallest passing input one step away.

## 2. State

**Signature:** depends on ordering or history; a fresh restart fixes it temporarily.

- Uninitialized or partially initialized object.
- Cache poisoning, stale cache, missing invalidation.
- Migration applied partially, backfill incomplete.
- Session or token state carried across tenants/users.
- Global mutable state shared across requests.

**Probe:** reset to a known state, replay steps one at a time, inspect the state after each.

## 3. Concurrency

**Signature:** intermittent, load- or timing-dependent, disappears under a debugger or with a log line.

- Data race on shared memory.
- Check-then-act (TOCTOU) on files, rows, caches.
- Deadlock from inconsistent lock ordering.
- Lost wakeup, missed signal, unbounded queue.
- Async cancellation leaving a partial write.
- Connection pool exhaustion from leaked connections.

**Probe:** stress with N workers, add barriers/delays, run under a race detector, reduce to two threads.

## 4. Resource

**Signature:** degrades over time; works after restart; fails at scale.

- Descriptor, socket, connection, or thread leak.
- Unbounded memory growth (queue, cache, buffer).
- Disk full, inode exhaustion.
- Thread pool starvation from blocking calls.
- Timeout too tight for the tail.

**Probe:** watch the resource over time under load; compare with a shorter run.

## 5. Environment

**Signature:** works on one machine and not another; no code difference.

- Runtime or library version differences.
- Missing or different environment variable.
- Locale, timezone, encoding, filesystem case sensitivity.
- CPU architecture, endianness, word size.
- Container limits, cgroup throttling, kernel parameters.
- Permissions, SELinux/AppArmor, filesystem mount options.

**Probe:** diff the environments explicitly; reproduce in the smallest container that matches.

## 6. Dependency

**Signature:** started without a code change; correlates with a release or lockfile update.

- Upstream behavior change in a patch release.
- Transitive dependency conflict.
- Network or API contract change.
- Certificate or key rotation.
- Rate limit or quota change.

**Probe:** pin/rollback the dependency, compare versions, read the changelog.

## 7. Data

**Signature:** only some records fail; correlated with data shape, age, or volume.

- Invalid or partial legacy records.
- Unicode, null bytes, very long fields.
- Duplicate keys, orphaned rows, referential drift.
- Timezone-shifted timestamps.
- Numeric precision loss on ingest.

**Probe:** group failures by data attribute; find the discriminating attribute.

## 8. Configuration

**Signature:** affects one deployment, not one code path.

- Feature flag state differs.
- Wrong connection string or pool size.
- Timeout/retry settings inconsistent across services.
- Log level hiding the error.
- Secret rotated in one environment only.

**Probe:** dump the effective configuration (not the intended one) and diff it.

## 9. Trigger, cause, contributing factor

| Term | Definition | Example |
| --- | --- | --- |
| Trigger | The event that exposed the defect | A retry after a timeout |
| Cause | The mechanism that produces the wrong behavior | Idempotency key generated per attempt |
| Contributing factor | Why it was not caught | No test for retry paths; error swallowed upstream |

Fix the cause. Guard the contributing factor. Do not "fix" the trigger.
