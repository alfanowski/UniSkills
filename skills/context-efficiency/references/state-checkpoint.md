# State Checkpoint

> A checkpoint is what lets a long task survive a context boundary without re-reading the world.
> Keep it short, factual, and pointer-based.

## 1. When to write one

- After reconnaissance, before deep analysis.
- After each major phase (evidence gathering, hypothesis testing, remediation design).
- Before delegating to a subagent, so the subagent gets state instead of a re-exploration mandate.
- Before any long-running command or interruption risk.

## 2. Template

````markdown
## Checkpoint <n> — <phase>
- Goal: <the decision this phase serves>
- Scope: <in / out>
- Verified: <fact> [path:line | commit | cmd]
- Reused: <fact> (from checkpoint <m>, artifact unchanged)
- Hypotheses: <hypothesis> — status (open / refuted / confirmed by <evidence>)
- Decisions: <decision> — reason
- Open questions: <question> — cost to resolve
- Next action: <one concrete step>
````

Rules:

- Maximum 20 lines. If it does not fit, the phase was too large — split it.
- Every `Verified` line carries a pointer. A checkpoint without pointers is a summary, and summaries
  decay into guesses.
- Never delete a refuted hypothesis; mark it refuted and keep the reason. It prevents re-litigating
  the same dead end.

## 3. Evidence ledger

For `DEEP` and `FORENSIC` work, keep a table alongside the checkpoints:

| # | Claim | Label | Evidence | Pointer | Cache key |
| --- | --- | --- | --- | --- | --- |
| 1 | ... | VERIFIED | ... | `src/a.c:88` | `sha:4f2a..` + `rg 1.2` |

The **cache key** is what makes reuse safe: artifact identity + operation + parameters + tool version.
If any component differs, the row is stale and must be re-derived.

## 4. Handoff to a subagent

A delegation prompt must contain:

1. the question and the decision it serves;
2. the scope, including what **not** to read;
3. the starting evidence (checkpoint + ledger rows), so the subagent does not repeat the search;
4. the required output shape and the stop condition;
5. the rule that returning "unknown" is acceptable and preferred to invention.

## 5. Recovery after a gap

When resuming:

1. Read the last checkpoint only — do not re-read the repository.
2. Verify that the artifacts it cites are unchanged (commit id, file mtime, hash).
3. If unchanged, continue from `Next action`.
4. If changed, invalidate the affected rows and re-derive only those.

This is the entire point: cost of resumption should scale with what changed, not with the size of the
project.
