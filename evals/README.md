# Evaluation Lab

The lab is a set of **executable specifications**, not a leaderboard.

- `cases/<skill>.yaml` — three or more cases per flagship skill.
- `rubrics/grading-rubric.md` — the shared scoring dimensions.
- `fixtures/` — synthetic artifacts used by a case, when the prompt alone is not enough.

## What is automated

```bash
python3 tools/eval_runner.py --check            # schema validation for every case
python3 tools/eval_runner.py --list             # case inventory
python3 tools/eval_runner.py --prompt ucr-001   # assembled, ready-to-run prompt
python3 tools/validate_skills.py                # every skill has a case file
```

Schema and coverage are deterministic. **Nothing here calls a model.**

## What is not automated

Whether an agent, given the skill, produces the required output. That requires a runner, a model, and a
grader. The protocol — arms, repetitions, blinding, reporting — is in
[`../docs/evaluation-methodology.md`](../docs/evaluation-methodology.md).

If you run cases, record: model and version, date, tool availability, the assembled prompt, the response,
and the rubric verdicts. Results that are not recorded do not exist for the purposes of this project.

## Case anatomy

```yaml
skill: universal-code-review
cases:
  - id: ucr-001              # unique across the repository
    title: Short description
    kind: standard           # standard | boundary | adversarial | false-positive | injection | missing-tool | contradictory-evidence
    depth: STANDARD          # QUICK | STANDARD | DEEP | FORENSIC
    prompt: |                # what the user says
      ...
    context: |               # optional environment or artifact notes
      ...
    expectations:
      must: [...]            # observable requirements, >= 2
      must_not: [...]        # negative space, >= 1
    rubric:
      correctness: ...       # >= 3 dimensions, each a concrete pass/fail description
      evidence: ...
      safety: ...
    fixture: fixtures/...    # optional, resolved relative to evals/
```

## Why the negative space matters

A skill that finds a plausible issue in a correct artifact is worse than useless: it trains users to
ignore the output. Every skill therefore ships at least one `false-positive` case, where the required
behavior is to report nothing, to refuse, or to ask one precise question.

## Known limits

- Three cases per skill is a floor, not coverage.
- Rubrics are written by the skill authors and share their blind spots.
- Grader agreement has not been measured.
