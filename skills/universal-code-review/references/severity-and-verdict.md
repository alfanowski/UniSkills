# Severity and Verdict

> Severity describes impact. Priority describes urgency. Confidence describes evidence. They are three
> different axes and collapsing them produces bad reviews.

## 1. Severity

| Level | Definition | Typical examples |
| --- | --- | --- |
| `CRITICAL` | Data loss, corruption, security breach, or total unavailability in a realistic scenario | Unbounded write to a production table; auth bypass; silent truncation of stored records |
| `HIGH` | A core path is wrong for a plausible input, or an invariant is broken with wide blast radius | Off-by-one on a pagination boundary; retry that duplicates a charge; missing null check on a required field from a trusted-but-fallible source |
| `MEDIUM` | Wrong behavior in a narrower case, or a hazard that requires an unusual condition | Timezone bug affecting one region; leak bounded by request rate; error swallowed so a failure looks like success |
| `LOW` | Correctness or maintainability issue with limited impact | Misleading name causing misuse; missing validation whose failure is caught downstream |
| `INFO` | Observation, no defect | "This duplicates existing helper X"; "Consider extracting this" |

Calibration rules:

- Severity is about the **effect**, not the elegance of the code or the reviewer's surprise.
- A defect in dead code is `INFO` unless the code is about to be enabled.
- A defect behind an unreachable guard is `INFO`, with the reachability analysis stated.
- A theoretical issue with no reachable trigger is a `HYPOTHESIS`, not a finding. Either find the
  trigger or drop it.

## 2. Priority

| Level | Meaning |
| --- | --- |
| `P0` | Stop the line; fix before any further merge or deploy |
| `P1` | Fix in this change or before the next release |
| `P2` | Schedule; fix in the next planned iteration |
| `P3` | Backlog; fix when touching the area |

Priority is context-dependent: the same `HIGH` severity is `P0` on a payment path and `P2` in an
internal admin tool with two users. State the context that drove the priority.

## 3. Confidence

- `high` — the path was traced end to end and a triggering input is constructible.
- `medium` — the path is traced but one condition is unverified (config, caller, data shape).
- `low` — the defect is inferred from a pattern; the trigger is not established.

Never present a `low` confidence finding as a blocker. Instead, state the check that would raise it.

## 4. Verdict rules

| Verdict | Condition |
| --- | --- |
| `BLOCK` | At least one `CRITICAL` or `HIGH` finding with `INTRODUCED` status and no mitigation in the change |
| `APPROVE_WITH_NITS` | Only `LOW`/`INFO`/`NIT` findings, and no unresolved `UNCERTAIN` finding above `MINOR` |
| `APPROVE` | No findings above `INFO`, tests cover the behavior change, and residual risk is written down |
| `INCOMPLETE` | Required evidence is missing: intent unclear, diff truncated, tests unavailable, or a finding cannot be confirmed or refuted |

`INCOMPLETE` is not a failure of the reviewer. It is the honest verdict when approval would be a guess.

## 5. Anti-inflation rules

Do not:

- raise severity because the author ignored a previous review;
- raise severity because the code is ugly;
- add "security" to a finding without a trust boundary and a sink;
- use `CRITICAL` for anything that requires an attacker with existing admin access;
- report the same root cause five times with different line numbers.

Do:

- merge duplicates under one root cause with multiple locations;
- separate `PRE-EXISTING` from `INTRODUCED`, and block only on what this change makes worse;
- state the smallest fix and the test that proves it;
- downgrade when the trigger requires an unrealistic precondition, and say why.

## 6. Writing the finding

Order inside a finding: what is wrong → when it happens → what breaks → how you know → how to fix. That
order lets a reader decide whether to care before reading the mechanism.

Bad: "This looks unsafe, the lock might not be held."

Good: "The read at `cache.go:88` runs outside the mutex taken at `:74`. Two concurrent misses both
write a fresh entry, so a stale value written first can overwrite a fresh one. Trigger: two requests for
the same key after expiry. Fix: hold the lock across the check-and-set, or use `singleflight`. Test:
two goroutines, expired key, assert exactly one loader call."
