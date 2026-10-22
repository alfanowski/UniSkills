# Debugging and Regression

**Pack id:** `debugging-and-regression` · **Skills:** 3 · **Typical effort:** hours to two days

## Purpose

Turn a failure into a confirmed cause, a minimal fix, and a test that prevents recurrence. The pack
exists because most debugging stops at "it works now", which is not a root cause.

## Audience

On-call engineers, maintainers, and anyone who has just fixed a production incident.

## Members and roles

| Order | Skill | Role in the pack | Produces |
| --- | --- | --- | --- |
| 1 | `root-cause-debugging` | Reconstruct the causal chain and confirm it | Causal chain + reproduction |
| 2 | `universal-code-review` | Review the fix as a change, not as a patch to a symptom | Findings + verdict |
| 3 | `experiment-design-and-falsification` | Prove the fix changed the behavior, and that the test would catch a regression | Experiment + decision rule |

## Recommended order and why

Cause first: reviewing a fix before the cause is known reviews the wrong thing. Review second: the fix
is a change and deserves the same scrutiny as any other. Experiment last: it verifies the effect and
prevents "it stopped happening" from being accepted as proof.

## Cost and permissions

- Reproduction may require production data; prefer a synthetic fixture or an anonymized snapshot.
- No destructive probes on live systems.
- Instrumentation must not log secrets or full payloads.

## When a single skill is enough

- The cause is confirmed and the fix is one line → `universal-code-review` with `QUICK`.
- The fix is in and the question is whether it worked →
  `experiment-design-and-falsification`.
- The failure is intermittent and the mechanism is entirely unknown → `root-cause-debugging` alone,
  `DEEP`.

## Limitations

- Cannot prove the absence of sibling defects; only a search scope.
- Flaky failures may resist confirmation; the pack then ends at `PROBABLE` with the missing test named.
- Post-incident organizational actions are out of scope.

## Validation

Structural checks only. The causal chain is validated by the intervention rule in
`root-cause-debugging`, not by an automated harness.
