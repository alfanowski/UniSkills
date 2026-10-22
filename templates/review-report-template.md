# Review Report

> Fill for code, security, and performance reviews. Delete sections that do not apply; do not delete the
> limits section.

```markdown
# Review: <title> (<base>..<head>)

**Verdict:** BLOCK | APPROVE_WITH_NITS | APPROVE | INCOMPLETE
**Intent:** <one sentence, reconstructed from description, commits, and tests>
**Scope:** <files, modules, boundaries reviewed>
**Not reviewed:** <areas, with reason>
**Tests run:** <commands + result, or "none — reason">

## Summary

<2–3 sentences: what this change does, what the risk is, what must happen before merge.>

## Findings

### F1 — <title>  [SEVERITY] · [PRIORITY] · confidence: high|medium|low
- **Location:** `path:line` (+ call sites)
- **Trigger:** <precondition + input/state>
- **Mechanism:** <control/data flow>
- **Impact:** <what breaks, bounded>
- **Evidence:** <pointer + what was read/executed>
- **Status:** INTRODUCED | PRE-EXISTING | UNCERTAIN
- **Fix:** <smallest correct change>
- **Acceptance:** <test that fails now and passes after>

### F2 — ...

## Test gaps

| Behavior | Covered? | Missing case |
| --- | --- | --- |

## Residual risk

- <unreviewed area / unexecuted check / assumption the verdict depends on>
```

## Notes for the author

- Order findings by severity, then by decision impact. Never by file order.
- Merge duplicates by root cause; five occurrences of one bug is one finding with five locations.
- If the verdict is `APPROVE` and the limits section is empty, the verdict is wrong.
