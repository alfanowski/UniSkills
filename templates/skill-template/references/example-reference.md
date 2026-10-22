# Example Reference

> This file demonstrates the expected shape of a reference document. Delete it when you copy the
> template. Keep references focused: one topic, loadable on its own, linked from `SKILL.md`.

## Contents

- Purpose and when to load
- The substantive material (tables, checklists, decision rules)
- Failure modes specific to this topic

## When to load

State the exact workflow step and the condition. "Read at step 4 when the artifact crosses a service
boundary." A reference with no loading condition is dead weight.

## Substantive material

Prefer tables and decision rules over prose. A reference should change what the agent does, not just
inform it.

| Condition | Action | Why |
| --- | --- | --- |
| ... | ... | ... |

## Failure modes

- **Too long.** If this file passes ~150 lines, split it by decision, not by heading.
- **Too abstract.** If every sentence would be true for any project, it belongs in `docs/`, not here.
- **Nested.** Do not link to another reference from here; link from `SKILL.md` so the load path stays one
  level deep.
