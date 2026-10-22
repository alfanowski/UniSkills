# Option Evaluation

> Evaluation is a decision aid, not a performance. Keep it legible enough that a skeptic can disagree
> with one cell without rejecting the whole table.

## 1. Dimensions

| Dimension | Question | Scale |
| --- | --- | --- |
| Mechanism fit | Does the mechanism actually address the stated cause? | direct / partial / indirect |
| Build cost | Engineering days, new dependencies, coordination | S (<1w) / M (1–4w) / L (>1m) / XL (quarter+) |
| Operate cost | On-call load, new failure modes, toil, cost per unit | low / medium / high |
| Reversibility | Cost to undo after 30 days | trivial / costly / one-way door |
| Time to signal | How soon you know if it works | days / weeks / months |
| Blast radius | Worst plausible failure and who it hits | local / service / org / customer |
| Skill fit | Does the team already have the capability? | yes / partial / no |
| Exit cost | Cost to leave this choice later (lock-in) | low / medium / high |

Use ordinal labels, not invented scores. A number implies a measurement you did not perform.

## 2. If you must score

Some decisions need a weighted score to be comparable. Then:

1. Declare the weights before scoring, in writing.
2. Use a 1–3 or 1–5 integer scale with a definition per level.
3. Keep the per-cell justification; the score is a summary, not the argument.
4. Show a sensitivity check: which weight change would flip the winner?
5. Never average dimensions that are not commensurable (build cost and blast radius are not the same
   unit).

## 3. Pre-mortem prompts

Assume the decision is twelve months old and went badly. Answer in concrete terms:

- What did we underestimate — the data volume, the operational load, the migration, the org change?
- Which dependency disappeared, changed license, or broke compatibility?
- What did we discover about the workload that invalidated the assumption?
- Who had to maintain it, and did they have the context?
- What did we stop doing to afford this, and did that loss matter more?

If a failure story is plausible and has no mitigation, it becomes: a condition on the recommendation, a
mitigation in the plan, or a reason to reject the option. Do not leave it as a decorative risk bullet.

## 4. Recommendation forms

| Form | When |
| --- | --- |
| "Choose A" | The criteria clearly separate A, and the condition is stable. |
| "Choose A if X, B otherwise" | The ranking depends on a genuinely uncertain variable. |
| "Do A now, instrument, then decide B" | The decision is reversible and information is cheap. |
| "Do not decide yet" | The missing information is cheaper to get than the cost of reversing a wrong choice. |
| "None of these" | All options violate a hard constraint — say so and return to framing. |

## 5. Discriminating experiment design

A good experiment between two options is:

- **small** — hours to days, not a quarter;
- **discriminating** — the two options produce *different* observable outcomes;
- **decision-bearing** — the result maps to a pre-declared choice;
- **cheap to abort** — no production dependency.

Template:

```text
Hypothesis: option A outperforms B on <metric> under <workload>.
Method: <minimal prototype> | Duration: <time box>
Measure: <metric, unit, collection method>
Decision rule: if <threshold> then A else B.
Abort rule: if <blocker> then stop and report.
```

If both options pass every experiment, the difference is preference. Choose the one that is easier to
reverse and stop spending.

## 6. Reporting rejected options

For each rejected option, record:

- the mechanism in one line (so it is not confused with a variant later);
- the criterion that killed it;
- the trigger that would make it viable again.

"Rejected: too complex" is not a record. "Rejected: requires dual-write across two stores for the
migration window; revisit if we adopt an outbox" is.
