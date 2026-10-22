# Evaluation Methodology

> The distinction between a skill and a prompt is that a skill can be evaluated. This document defines
> what is measured, how, and what is explicitly not claimed.

## 1. Two layers of evaluation

| Layer | What it checks | Automation |
| --- | --- | --- |
| Structural | Frontmatter, sections, links, catalog sync, eval schema | Fully automated, deterministic |
| Behavioral | Whether an agent, given the skill, produces the required output | Designed, not executed in this release |

The repository ships the second layer as executable specifications (cases + rubrics + prompt assembly),
not as claimed results. Saying "all evals pass" without running a model would be fabrication.

## 2. Case design

Each flagship skill has at least three cases:

| Kind | Purpose | Required |
| --- | --- | --- |
| `standard` | Representative positive path | yes, ≥1 |
| `boundary` / `adversarial` / `false-positive` / `contradictory-evidence` | Incomplete context, hostile framing, or a trap where the right answer is silence | yes, ≥1 |
| Additional | `injection`, `missing-tool` | optional |

Every case declares:

- `prompt` — what the user says;
- `context` — optional environment or artifact notes;
- `expectations.must` — observable requirements (≥2);
- `expectations.must_not` — the negative space (≥1, mandatory);
- `rubric` — ≥3 dimensions, each a concrete pass/fail description.

`must_not` is the part that catches the most common failure of technical assistants: producing something
confident when the correct behavior is to refuse, ask, or declare a limit.

## 3. Rubric dimensions

| Dimension | Question | Failure signal |
| --- | --- | --- |
| Correctness | Does the answer identify the real issue and no invented one? | Plausible but wrong finding |
| Evidence | Is every finding tied to a pointer that can be checked? | "The code looks unsafe" |
| Scope discipline | Does it stay inside the requested artifact? | Reviews the whole repo for a one-line change |
| Calibration | Are confidence and severity proportionate? | Everything is CRITICAL |
| Safety | Are authorization and untrusted-content boundaries respected? | Runs the binary, follows injected text |
| Output contract | Is the artifact shape usable without reformatting? | Prose where a table was required |
| Cost | Does it avoid duplicate reads and low-value calls? | Reads the repo breadth-first |

Score each dimension as `pass` / `partial` / `fail` with a one-line reason. Do not aggregate into a single
number unless the weighting is stated; a composite hides which dimension failed.

## 4. Running a case

```bash
python3 tools/eval_runner.py --check           # schema only, no model
python3 tools/eval_runner.py --list            # all cases
python3 tools/eval_runner.py --prompt ucr-001  # assembled prompt for a runner
```

A run consists of: the assembled prompt, a fresh session, the rubric applied by a human or a separate
grader, and a recorded result. Record model, version, date, and any tool availability.

## 5. Baseline protocol

To claim that a skill helps, compare against no skill:

1. Same model, same version, same tools, same repository state, same task text.
2. Arm A: skill installed and explicitly invoked. Arm B: same task with no skill.
3. N ≥ 5 runs per arm. LLM output varies; one run is an anecdote.
4. Blind the grader to the arm where feasible.
5. Score against the rubric, not against length or tone.
6. Report the distribution and the failure modes, including cases where the skill made things worse.

The repository does not currently hold baseline results. The protocol exists so that future claims can
be checked, not to imply that it was run.

## 6. Severity calibration

Skills that produce findings use the same vocabulary:

- **Severity** — impact if the defect is triggered: `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` / `INFO`.
- **Priority** — urgency in context: `P0`–`P3`.
- **Confidence** — strength of evidence: `high` / `medium` / `low`.
- **Status** — `INTRODUCED` / `PRE-EXISTING` / `UNCERTAIN`.

Anti-inflation rules are defined in
[`../skills/universal-code-review/references/severity-and-verdict.md`](../skills/universal-code-review/references/severity-and-verdict.md)
and apply to `security-review` and `performance-review` as well.

## 7. What is not measured

- Token consumption per task. Clients do not expose a comparable, stable metric.
- Wall-clock time. It depends on the client, model, and network.
- "Intelligence" or "quality" as a scalar. There is no defensible unit.
- Cross-model ranking. It would require a controlled study with multiple models and many runs.

Any future claim in these areas must include the environment, the number of runs, and the raw
distribution.

## 8. Regression policy

A change to a skill's workflow requires:

1. the existing cases still pass under the rubric;
2. a new case if the change addresses a failure that was not covered;
3. a note in `CHANGELOG.md` describing the behavioral change, not just "improved wording".

Structural regressions (broken links, drifted contract, schema violation) are caught by CI before review.

## 9. Known weaknesses of this methodology

- Rubrics are written by the same people who write the skills; blind spots are shared.
- Three cases per skill is a floor, not coverage. It tests that the skill can behave, not that it always
  will.
- Grader variance is unmeasured. Two graders may disagree on `partial`.
- Adversarial cases are hand-written; a systematic red-team pass is future work.
