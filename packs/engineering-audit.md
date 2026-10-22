# Engineering Audit

**Pack id:** `engineering-audit` · **Skills:** 4 · **Typical effort:** half a day to two days

## Purpose

Decide whether a change or a system is safe to commit to. The pack moves from structure to
correctness to adversarial exposure to cost, because each step narrows what the next one must examine.

## Audience

Tech leads and senior engineers preparing a high-risk merge, a pre-release review, or a design
sign-off.

## Members and roles

| Order | Skill | Role in the pack | Produces |
| --- | --- | --- | --- |
| 1 | `architecture-design-review` | Establish whether the structure can satisfy the quality attributes at all | Decision record + scenarios |
| 2 | `universal-code-review` | Judge the actual change against contracts and failure paths | Findings + verdict |
| 3 | `security-review` | Re-examine the same change through trust boundaries and reachable sinks | Security findings + control register |
| 4 | `performance-review` | Test the cost claims and locate the dominant layer | Cost model + ranked bottlenecks |

## Recommended order and why

Structure first: there is no point reviewing the correctness of a change whose decomposition cannot
work. Correctness next: a security review of code that is functionally broken wastes effort on paths
that will change. Security third: it depends on the finalized control flow. Performance last: it needs
the stable shape of the code to attribute cost.

## Cost and permissions

- Read-only by default. Running tests or profilers is optional and must be authorized.
- The security step must stay within static analysis unless the user owns the target and permits active
  testing.
- Expect a large context footprint; use `context-efficiency` to keep the reading plan bounded.

## When a single skill is enough

- Only one file changed and it is a pure refactor: `universal-code-review`.
- The question is "will this handle the load": `performance-review`.
- The question is "is this reachable by an attacker": `security-review`.
- No code exists yet: `architecture-design-review` alone.

## Limitations

- Not a penetration test, not a compliance attestation.
- Static review cannot prove the absence of vulnerabilities.
- Performance conclusions are weak without a representative workload.

## Validation

Each member skill ships its own eval cases. Pack-level validation is limited to structural checks
(members exist, order is a permutation, document present) plus manual dry runs recorded in
`docs/release-process.md`. No automated end-to-end pack evaluation is claimed.
