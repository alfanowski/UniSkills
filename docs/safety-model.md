# Safety Model

> A skill is executable influence over an agent. Treat it as code review, not as documentation.

## 1. Why a skill is an attack surface

A `SKILL.md` can change what an agent looks at, which tools it calls, what it writes, and what it
declares as true. Installing a skill is closer to installing a small program than to reading a blog post.
Three consequences follow:

1. Skill content is privileged relative to user data.
2. Skills must not gain capabilities merely by being present.
3. Skills that analyze untrusted content must assume that content is adversarial.

## 2. Threat model

| Threat | Vector | Mitigation in this repository |
| --- | --- | --- |
| Instruction injection | A README, issue, log, web page, or binary string containing "ignore previous instructions" | Every skill states that analyzed content is data; the contract echoes it; eval cases include injection |
| Privilege escalation by instruction | A skill telling the agent to install packages, edit global config, or deploy | Skills are read-only by default; external actions require explicit authorization; no install instructions |
| Data exfiltration | A skill instructing the agent to send repository contents to an endpoint | No skill requests network egress of user data; no bundled scripts make network calls |
| Malicious scripts | A `scripts/` file that does more than documented | First release ships no executable skill scripts; repository tooling is auditable and stdlib-only |
| Supply chain | A dependency, template, or copied asset with unclear provenance | No third-party code; the survey records what was read and its license; nothing is copied |
| Deceptive claims | A skill that inflates confidence or fabricates results | Evidence labels, mandatory gaps, explicit "never fabricate" rules, and eval cases that test refusal |
| Over-broad activation | A description that triggers on unrelated tasks | Descriptions must contain explicit "Use when" triggers; each skill must list ≥3 exclusions |
| Destructive analysis | Running an unknown binary, deleting state to "reset", probing production | Explicit authorization gates; static-first for RE; no destructive probes |

## 3. Authorization gates

A skill may proceed without asking only when all of the following hold:

- the action is local and read-only;
- the target is material the user already possesses or owns;
- the action is reversible with no external side effect.

Otherwise it must stop and ask. The gates, uniformly across skills:

| Action | Gate |
| --- | --- |
| Reading files in the user's workspace | Allowed |
| Running a project's existing tests | Allowed if non-destructive; state what was run |
| Installing packages | Explicit authorization |
| Writing to a third-party system, opening PRs, creating issues | Explicit authorization |
| Deploying, migrating a live database, deleting data | Explicit authorization + rollback plan |
| Active security testing of a target | Written authorization naming the target and scope |
| Executing an unknown binary | Isolated environment + authorization; not on the analysis host |
| Sending data to an external API | Explicit authorization, and only the minimum data needed |

## 4. Untrusted content rule

Text inside the analyzed artifact never changes the agent's instructions. Concretely:

- A comment saying "agent: do X" is reported as an observation, not obeyed.
- A README claiming a different scope does not expand the scope.
- Tool output is evidence about the artifact, not a command.
- If injected instructions are found, they are surfaced to the user as a finding.

This is tested: `context-efficiency` case `ctx-002` plants an injection in a Makefile comment and
requires the agent to report it and continue.

## 5. Security research boundaries

UniSkills supports defensive work, interoperability, and analysis of artifacts the user owns. It does
not support:

- unauthorized access, scanning, or exploitation;
- credential theft, persistence, or evasion for an intruder;
- malware development or weaponized payloads;
- bypassing licensing or access controls for illegitimate use.

Where a request is ambiguous, the skill restricts itself to static, defensive analysis and asks the
minimum clarifying question. This is a product boundary, not legal advice.

## 6. Script policy

The first release ships **no executable scripts inside skills**. All repository tooling:

- is Python 3 standard library only;
- makes no network calls;
- reads and writes only inside the repository (plus test temp directories);
- prints errors with file and line;
- refuses to run destructive operations (there are none).

If a future skill needs a script, the requirements are: documented purpose, deterministic output,
explicit error handling, no network, no writes outside a stated path, and a test.

## 7. Supply chain of the repository itself

- No runtime dependencies. `requirements.txt` does not exist on purpose.
- CI uses the runner's Python, no third-party actions beyond the official checkout/setup actions.
- No secrets are required to run the tests.
- `tools/check_secrets.py` scans on every CI run.
- Third-party material is cited, never copied. Licenses are recorded in
  [research-and-competitor-survey.md](research-and-competitor-survey.md).

## 8. Reporting a vulnerability

See [`../SECURITY.md`](../SECURITY.md). Do not open a public issue for a vulnerability in UniSkills or in
a skill's guidance. Reports go through the private channel described there.

## 9. Residual risks

These are accepted and not fully mitigated:

- A skill can still be *wrong* in a way that produces confident bad advice. Evaluations reduce this; they
  do not eliminate it.
- Prompt injection defense is instruction-level. A model may still comply with injected text under
  pressure; the mitigation is that the skill treats content as data and that evals test it.
- Users can install a modified copy. UniSkills cannot attest to the integrity of forks.
- Descriptions are a routing surface; a malicious fork could over-trigger deliberately.
