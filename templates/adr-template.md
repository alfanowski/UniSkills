# Architecture Decision Record

> Use for `architecture-design-review`. One file per decision, numbered, never deleted — superseded
> decisions are marked, not removed.

```markdown
# ADR-<NNN>: <decision in imperative form>

**Status:** PROPOSED | ACCEPTED | REJECTED | SUPERSEDED by ADR-<NNN>
**Date:** YYYY-MM-DD
**Deciders:** <roles, not names if the record is public>

## Context

<The forces at play: functional requirement, hard constraints, and what happens if nothing is decided.>

## Quality-attribute scenarios

| # | Stimulus | Response | Measure | Priority |
| --- | --- | --- | --- | --- |

## Options considered

| # | Structure | Where state lives | Satisfies | Build cost | Operate cost | Reversibility |
| --- | --- | --- | --- | --- | --- | --- |

## Decision

<One paragraph. Mechanism, not product names. State what is being optimized and what is being traded.>

## Consequences

- **Positive:** ...
- **Negative / accepted trade-offs:** ...
- **New failure modes:** ...
- **Migration:** expand/contract steps, compatibility window, rollback trigger
- **One-way door:** yes | no — if yes, the approval and rehearsal required

## Rejected alternatives

| Option | Why rejected | Revisit if |
| --- | --- | --- |

## Assumptions that would invalidate this

- <assumption> — check by <date or metric>

## Acceptance criteria

- [ ] <observable check: chaos test, latency budget, restore drill, cost ceiling>
```

## Notes

- An ADR without rejected alternatives is a press release.
- An ADR without a review date becomes folklore.
- If two ADRs conflict, the newer one wins only if it says it supersedes the older one.
