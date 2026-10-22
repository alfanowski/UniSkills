# Idea to Specification

**Pack id:** `idea-to-spec` · **Skills:** 3 · **Typical effort:** two days to two weeks

## Purpose

Take a vague ambition and end with a decision record that an implementation team can act on. The pack
deliberately separates "what are the options" from "what does the field already know" from "which one
do we commit to".

## Audience

Founders, product-minded engineers, and architects at the start of a project or a major pivot.

## Members and roles

| Order | Skill | Role in the pack | Produces |
| --- | --- | --- | --- |
| 1 | `technical-brainstorming` | Generate mechanism-distinct options from the actual constraints | Options + criteria |
| 2 | `technical-research` | Check prior art, known failure modes, and vendor claims | Source ledger |
| 3 | `architecture-design-review` | Commit to one structure with failure analysis and a migration path | Decision record |

## Recommended order and why

Brainstorm first so the research has a target; researching before framing produces a literature tour
with no decision. Research second so the options are evaluated against reality rather than intuition.
Architecture last because commitment requires scenarios and a rollback, which only exist once the
options are narrowed.

## Cost and permissions

- Mostly read-only and local.
- Research requires network access; no paid sources assumed.
- The output is a decision record, not code and not a deployment.

## When a single skill is enough

- You only need alternatives → `technical-brainstorming`.
- You only need prior art → `technical-research`.
- The option is already chosen and needs a design review → `architecture-design-review`.

## Limitations

- `specification-writing` (planned) is not part of this pack yet; the decision record stops short of
  task-level acceptance criteria.
- The pack does not estimate delivery dates.
- It cannot resolve disagreements about priorities; it can only make the trade-off explicit.

## Validation

Structural checks only in this release. The quality bar for the pack is that each step's artifact is
consumed by the next; a chain that produces an unused artifact is a failed pack run.
