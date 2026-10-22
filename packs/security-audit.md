# Security Audit

**Pack id:** `security-audit` · **Skills:** 3 · **Typical effort:** one to four days

## Purpose

Find reachable weaknesses in a scope the user controls, then make the report survive scrutiny. The
security pass finds candidate paths, the code review establishes whether they are real in the
implementation, and the evidence pass checks that the report's claims match the evidence.

## Audience

Maintainers auditing their own project, security engineers doing an internal review, and teams
preparing for an external assessment.

## Members and roles

| Order | Skill | Role in the pack | Produces |
| --- | --- | --- | --- |
| 1 | `security-review` | Model assets, actors, boundaries; trace source to sink | Findings + control register |
| 2 | `universal-code-review` | Establish whether the surrounding logic is correct enough for the finding to hold | Correctness findings |
| 3 | `evidence-validation` | Audit the report's own claims before delivery | Graded claim inventory |

## Recommended order and why

Security first, because the threat model determines which code is even relevant. Correctness second,
because a finding built on a misread control flow is a false positive. Evidence validation last,
because it is the only step that sees the finished report and can catch overreach.

## Cost and permissions

- Written authorization is required for any activity beyond reading code the user already possesses.
- No scanning, fuzzing, or exploitation of third-party systems.
- Proofs of concept only if the target is owned by the user, the action is non-destructive, and
  reachability cannot be established statically.

## When a single skill is enough

- "Is this one endpoint safe?" → `security-review` with `QUICK` or `STANDARD` depth.
- "Did the fix actually close it?" → `universal-code-review` on the fix plus `security-review` on the
  path.
- "Is this report credible?" → `evidence-validation`.

## Limitations

- Coverage is bounded by the reviewed surface; the report must say so.
- Static analysis cannot confirm runtime configuration, deployed flags, or infrastructure IAM.
- Absence of findings is not evidence of absence of vulnerabilities.

## Validation

Structural validation only (members exist, document present, order consistent). Scenario-level
validation is manual and recorded in the release notes. Do not describe this pack as "certified".
