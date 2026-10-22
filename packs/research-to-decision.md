# Research to Decision

**Pack id:** `research-to-decision` · **Skills:** 4 · **Typical effort:** one day to one week

## Purpose

Move from "we think X" to a decision with sources, alternatives, and a test that could prove it wrong.
Most technical research stops at a summary; this pack ends at a commitment.

## Audience

Engineers and technical leads choosing a technology, an algorithm, or an approach where being wrong is
expensive.

## Members and roles

| Order | Skill | Role in the pack | Produces |
| --- | --- | --- | --- |
| 1 | `technical-research` | Establish what is actually known, from primary sources | Source ledger + findings by question |
| 2 | `evidence-validation` | Check the claims that will carry the decision | Graded claim inventory |
| 3 | `technical-brainstorming` | Turn the evidence into genuinely distinct options | Options + conditional recommendation |
| 4 | `experiment-design-and-falsification` | Design the test that separates the leading options | Experiment plan |

## Recommended order and why

Research first: generating options before knowing the constraints of the field produces fantasy.
Validation second: the options inherit the credibility of the evidence, so fix the evidence first.
Brainstorming third: it consumes the evidence rather than re-searching. Experiment last: it needs a
specific pair of options to discriminate between.

## Cost and permissions

- Network access is needed for primary sources; the pack must work without paid databases.
- No API calls to paid services without explicit approval.
- Experiments run locally or in staging; production experiments require authorization.

## When a single skill is enough

- The answer already exists in a spec → `technical-research`.
- The options are obvious and only the test is missing →
  `experiment-design-and-falsification`.
- Someone handed you a report and asked if it is sound → `evidence-validation`.

## Limitations

- Paywalled literature is out of reach; state this rather than implying exhaustive coverage.
- Research quality is bounded by source availability, not by effort.
- The pack does not implement the chosen option.

## Validation

Structural checks only. The research quality gate is the source ledger; the decision gate is the
experiment's decision rule. Neither is automated in this release.
