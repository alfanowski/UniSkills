# Worked Examples

Four end-to-end outputs, each showing the **shape** a skill produces rather than a lucky answer. All
artifacts, repositories, identifiers, and numbers are synthetic.

| Example | Skill demonstrated | What to look for |
| --- | --- | --- |
| [Pagination cursor review](code-review/pagination-cursor.md) | `universal-code-review` | A finding with trigger, mechanism, impact, and an acceptance test — plus a rejected false positive |
| [Cross-tenant export](security-review/tenant-scope.md) | `security-review` | A source-to-sink chain with actor, precondition, control register, and residual risk |
| [Reconciliation throughput](brainstorming/reconciliation-throughput.md) | `technical-brainstorming` | Mechanism-distinct options, pre-mortem, conditional recommendation, discriminating experiment |
| [A "10x faster" benchmark](research/benchmark-claim.md) | `technical-research` + `evidence-validation` | Claim labels, benchmark comparability, source ledger, and an explicit refusal to overclaim |

## How to read them

Each example is structured like the real report:

1. the situation (what the user asked);
2. the output the skill would produce;
3. a short note on why that shape matters.

They are not transcripts, and they are not evaluation results. A transcript of a real run would include
tool calls, dead ends, and the model's actual wording; these files isolate the deliverable.

## Using them

- As a reference for what "good" looks like before you write a new skill.
- As a prompt fixture: paste the situation and compare the shape of the answer.
- As a source of test ideas: every example contains at least one behavior worth turning into an eval case.

## What they are not

- Evidence that the skill works. That requires a recorded run against a model, per
  [`../docs/evaluation-methodology.md`](../docs/evaluation-methodology.md).
- Real findings. Nothing here describes a real system.
