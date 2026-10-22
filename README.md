# UniSkills

**Universal, evidence-driven skills for AI agents that do serious engineering work.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-3776AB.svg)](tools/)
[![Agent Skills format](https://img.shields.io/badge/format-Agent%20Skills-6E56CF.svg)](https://agentskills.io/specification)
[![Status: 0.1.0 beta](https://img.shields.io/badge/status-0.1.0%20beta-orange.svg)](CHANGELOG.md)
[![Validate](https://github.com/alfanowski/UniSkills/actions/workflows/validate.yml/badge.svg)](.github/workflows/validate.yml)

UniSkills is a suite of portable [Agent Skills](https://agentskills.io/specification) for code review,
security analysis, performance work, debugging, architecture, research, and reverse engineering.

Every skill is a **procedure with an evidence contract**: ordered steps, explicit exit conditions, claim
labels, and a stated depth budget. Install one directory, and the agent stops improvising a review and
starts running one.

```bash
git clone https://github.com/alfanowski/UniSkills.git
cp -R UniSkills/skills/universal-code-review ~/.claude/skills/
```

That is the whole installation. No package manager, no runtime, no account.

---

## Contents

- [Why this exists](#why-this-exists)
- [What makes it different](#what-makes-it-different)
- [Quick start](#quick-start)
- [The skills](#the-skills)
- [Packs](#packs)
- [How a skill reasons](#how-a-skill-reasons)
- [Evidence, not vibes](#evidence-not-vibes)
- [Context and tool economy](#context-and-tool-economy)
- [Safety model](#safety-model)
- [What is verified, and what is not](#what-is-verified-and-what-is-not)
- [Repository layout](#repository-layout)
- [Contributing](#contributing)
- [License](#license)

---

## Why this exists

Engineers do not need more prompts. They need procedures that survive contact with reality.

A prompt tells a model *what to say*. It rarely tells it **what to check, in what order, with what proof,
and when to stop**. The result is fluent, plausible, and occasionally completely wrong in a way that reads
exactly like confidence. You notice a week later, in production.

UniSkills encodes the missing half:

| A prompt gives you | A UniSkills skill gives you |
| --- | --- |
| A role and a tone | A numbered workflow with exit conditions |
| "Be thorough" | A depth profile chosen by risk, with concrete obligations |
| Assertions | Seven evidence labels and a pointer per load-bearing claim |
| "Find issues" | Severity, priority, confidence, and a verdict vocabulary |
| A wall of text | An output contract you can diff between runs |

## What makes it different

**1. One method, translated per domain.** Every skill applies the same reconstruction discipline —
scope, components, state, transfer, contracts, resources, trust, failure — but the vocabulary, lenses, and
checklists are domain-specific. A code review traces control flow and invariants; a security review traces
sources and sinks; a performance review traces cost layers. The shared doctrine lives once, in
[`docs/universal-method.md`](docs/universal-method.md).

**2. Depth is a budget, not a personality.** Four profiles with concrete obligations:

| Profile | Use when | What you get |
| --- | --- | --- |
| `QUICK` | Small, reversible, low blast radius | Direct answer + one falsification check |
| `STANDARD` | Ordinary engineering work | Full workflow, evidence pointers, adversarial check |
| `DEEP` | High uncertainty or high impact | Alternative hypotheses, failure matrix, cross-checks |
| `FORENSIC` | Incidents, critical audits, untrusted artifacts | Artifact hashes, tool versions, coverage map |

Escalation is mandatory for auth, crypto, money, memory safety, concurrency, migrations, and untrusted
input parsing — regardless of diff size. `QUICK` never skips a safety gate.

**3. Skills are standalone, and the repository proves it.** No skill links outside its own directory.
A single copy keeps working. The shared part is a ~110-word contract embedded in every skill and
drift-checked by the validator, so it cannot quietly diverge.

**4. The catalog cannot lie.** `catalog/skills.yaml` is the source of truth; the markdown views are
generated in CI. A `planned` skill must **not** have a directory. A `flagship` skill must have passing
validation and at least three evaluation cases.

**5. Quality is executable.** Frontmatter, required sections, section order, contract drift, link
validity, reference reachability, eval schema, catalog/filesystem consistency, and secret patterns are
all checked by deterministic tooling with no dependencies.

## Quick start

### Prerequisites

Git and a client that supports the Agent Skills format. Nothing else.

### Install

```bash
git clone https://github.com/alfanowski/UniSkills.git

# one skill
cp -R UniSkills/skills/universal-code-review ~/.claude/skills/

# or a set
cp -R UniSkills/skills/{root-cause-debugging,universal-code-review} ~/.claude/skills/
```

Replace the destination with the skills directory your client documents. Keep the whole directory:
`references/` is part of the skill, not documentation.

### Use

Trigger by intent, in the skill's own vocabulary:

> "Review this diff and tell me whether it is safe to merge."

> "The service returns duplicates only after a timeout. Find the root cause."

> "Is this benchmark credible for our workload?"

Full instructions, verification steps, and uninstall: [`docs/installation.md`](docs/installation.md).

### Validate locally

```bash
python3 tools/validate_skills.py
python3 tools/validate_catalog.py
python3 tools/check_links.py
python3 tools/check_secrets.py
python3 tools/render_catalog.py --check
python3 -m unittest discover -s tools/tests -t .
```

Standard library only. Read-only. Works offline.

## The skills

Twelve shipped skills. Each one is a complete workflow, two references, and three evaluation cases.

| Skill | What it decides | Reach for it when |
| --- | --- | --- |
| [`uniskills-router`](skills/uniskills-router/SKILL.md) | Which skill, which depth, which deliverable | A request could match several skills |
| [`context-efficiency`](skills/context-efficiency/SKILL.md) | How to spend context without losing evidence | The repository or logs are too big to read fully |
| [`evidence-validation`](skills/evidence-validation/SKILL.md) | Whether a claim is actually supported | A report is about to inform a decision |
| [`universal-code-review`](skills/universal-code-review/SKILL.md) | Whether a change is safe to merge | A PR, patch, or function needs a verdict |
| [`root-cause-debugging`](skills/root-cause-debugging/SKILL.md) | What actually caused the failure | Something breaks and the reason is unknown |
| [`architecture-design-review`](skills/architecture-design-review/SKILL.md) | Which structure to commit to, and how to migrate | A boundary, ownership, or migration decision is open |
| [`performance-review`](skills/performance-review/SKILL.md) | Where the cost really goes | Latency, throughput, or memory is at risk |
| [`security-review`](skills/security-review/SKILL.md) | Whether an actor can reach a dangerous operation | Auth, parsing, files, secrets, or a new trust boundary |
| [`technical-research`](skills/technical-research/SKILL.md) | What is actually established, from primary sources | The state of the art, or a vendor claim, is in question |
| [`technical-brainstorming`](skills/technical-brainstorming/SKILL.md) | Which genuinely different option to choose | The options have not been made explicit |
| [`experiment-design-and-falsification`](skills/experiment-design-and-falsification/SKILL.md) | What test would settle the claim | An improvement is asserted and contested |
| [`reverse-engineering`](skills/reverse-engineering/SKILL.md) | What an authorized artifact does, and how | A binary, format, or protocol must be understood |

Full catalog — including 34 planned and deferred capabilities, so you can see what is *not* built yet:
[`catalog/SKILL_CATALOG.md`](catalog/SKILL_CATALOG.md) · [`catalog/ROADMAP.md`](catalog/ROADMAP.md).

## Packs

Packs are ordered playbooks over existing skills. They add sequencing, not content.

| Pack | Sequence | Use case |
| --- | --- | --- |
| [Engineering Audit](packs/engineering-audit.md) | architecture → code review → security → performance | Pre-release or high-risk merge |
| [Security Audit](packs/security-audit.md) | security → code review → evidence validation | Auditing your own codebase |
| [Debugging and Regression](packs/debugging-and-regression.md) | root cause → review → experiment | From failure to a verified fix |
| [Research to Decision](packs/research-to-decision.md) | research → validation → brainstorming → experiment | Choosing a technology under uncertainty |
| [Idea to Specification](packs/idea-to-spec.md) | brainstorming → research → architecture | From ambition to a decision record |
| [Reverse Engineering Lab](packs/reverse-engineering-lab.md) | reverse engineering → validation → security | Authorized artifact analysis |

## How a skill reasons

The phrase *"reason like you are analyzing assembly"* is used inside this project as an analogy for
**resolution**, not as a product requirement. It means: do not stop at what a system appears to do.
Reconstruct how it does it, to the depth the task actually needs.

| Surface description | Reconstructed description |
| --- | --- |
| "The function validates the token." | Which branch accepts, on which field, against what, with which clock, and what happens on each failure edge. |
| "The cache makes it fast." | Key composition, invalidation trigger, eviction policy, miss-path cost, and when it is slower than no cache. |
| "The migration adds a column." | Lock mode, rewrite cost, backfill order, deploy/rollback window, and which readers break in between. |

The eight reconstruction questions — scope, components, state, transfer, contracts, resources, trust,
failure — are defined once in [`docs/universal-method.md`](docs/universal-method.md).

**This does not mean UniSkills ships an assembly-analysis skill.** Instruction-level reasoning lives where
it belongs: as an on-demand reference inside `reverse-engineering`, loaded only when the question requires
ISA, ABI, or stack-frame evidence. The decision and its rationale are recorded in
[`docs/decision-log.md`](docs/decision-log.md#d2--no-standalone-assembly-flagship).

## Evidence, not vibes

Every skill labels its claims:

| Label | Meaning |
| --- | --- |
| `VERIFIED` | Observed or reproduced, with a pointer |
| `DERIVED` | Follows by explicit reasoning from verified premises |
| `LIKELY` | Strong indirect support, one named gap |
| `HYPOTHESIS` | Proposed, with the test that would settle it |
| `SPECULATIVE` | Exploratory, never a premise for a load-bearing conclusion |
| `UNKNOWN` | Not determinable with available access or tools |
| `N/A` | Does not apply, with a reason |

Three rules make this more than decoration:

1. **A pointer per claim.** `path:line`, symbol, offset, commit, URL + access date, or test id.
2. **Absence of evidence is not evidence of absence.** A clean scan is not a security certificate.
3. **Confidence is not severity.** A high-confidence low-impact issue is still low impact.

The full taxonomy is in [`docs/evidence-and-claims.md`](docs/evidence-and-claims.md).

## Context and tool economy

Context is a shared budget: every token a skill loads competes with the actual task.

- **Progressive disclosure in practice.** `SKILL.md` is decision logic (≤ 500 lines target, hard cap enforced). Depth lives
  in `references/`, loaded per workflow step, one level deep so partial reads cannot lose the thread.
- **Locate before reading.** `git diff --stat` before a diff, `rg -l` before a file, `--stat` before a
  directory tree.
- **Read in expanding rings.** Exact lines → callers and contracts → tests and docs. Stop when the next
  ring cannot change the answer.
- **Shape tool output.** `-C2` context, `jq` projections, explicit `head`/`tail`, counts before raw logs.
- **Reuse only with a cache key.** Artifact identity + operation + parameters + tool version.
- **Checkpoint instead of re-reading.** ≤ 20 lines: goal, verified facts, refuted hypotheses, next action.

There is no "token savings" number in this README, because clients do not expose a stable, comparable
metric. The protocol for measuring it honestly — same model, same task, N ≥ 5 runs, rubric-scored — is in
[`docs/evaluation-methodology.md`](docs/evaluation-methodology.md).

## Safety model

A skill influences what an agent reads, runs, writes, and asserts. It is closer to installing a small
program than to reading a blog post.

- **Read-only by default.** No external writes, installs, deployments, or active security testing without
  explicit authorization.
- **Analyzed content is data.** A README, log line, issue, or binary string that says "ignore previous
  instructions" is reported as an observation, never obeyed.
- **Authorization gates for security and reverse engineering.** Written scope, static-first, no
  exploitation, no execution of unknown artifacts on the analysis host.
- **No scripts in skills.** The first release ships zero executable skill scripts; repository tooling is
  auditable, standard-library only, and makes no network calls.

Details: [`docs/safety-model.md`](docs/safety-model.md) · vulnerability reporting: [`SECURITY.md`](SECURITY.md).

## What is verified, and what is not

This project's own rules apply to its claims.

**Verified in this repository (2026-10-22):**

- Frontmatter, required sections, section order, and the operating contract pass for all 12 skills.
- All relative links resolve; every reference is reachable from its `SKILL.md`.
- Catalog, packs, and filesystem are consistent: 12 flagship, 32 planned, 2 deferred.
- 36 evaluation cases validate against the schema, each with `must` and `must_not` expectations.
- 51 unit tests pass, including a differential test of the in-repo YAML parser against PyYAML on every
  YAML file.
- No secrets or personal absolute paths detected.

**Not verified:**

- No model was run against any evaluation case. There is no pass rate, no benchmark, and no token
  measurement. Claiming otherwise would violate the project's own evidence rules.
- No client was installed. Compatibility with Claude Code, the Claude API, the OpenAI Responses/Agents
  APIs, or any other client is **expected from the format, not tested here**.
- Skills are `beta`, not `stable`. `stable` requires recorded cross-model runs and a regression history.

The full disclosure is in [`docs/compatibility.md`](docs/compatibility.md) and
[`CHANGELOG.md`](CHANGELOG.md).

## Repository layout

```text
skills/         12 installable skill bundles (SKILL.md + references/)
packs/          6 ordered playbooks
catalog/        skills.yaml (source of truth) + generated catalog and roadmap
docs/           vision, architecture, method, evidence, safety, compatibility, evaluation
evals/          36 cases, rubrics, synthetic fixtures
templates/      skill template, finding schema, review/research/experiment/ADR templates
tools/          validators, YAML subset parser, catalog renderer, tests
examples/       four worked end-to-end examples
```

## Contributing

Contributions are welcome, including disagreement with the method. The bar is explicit:

- a new skill needs a workflow, two references, three eval cases (one of which must be a
  false-positive guard), and passing validators;
- a behavioral change needs an eval case that would have caught the old failure;
- a claim needs a pointer.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and
[`docs/skill-authoring-standard.md`](docs/skill-authoring-standard.md) before writing a skill.

## License

MIT — see [`LICENSE`](LICENSE).

"UniSkills" is used descriptively; no trademark is claimed. Unrelated projects use similar names, and the
survey records the collision check: [`docs/research-and-competitor-survey.md`](docs/research-and-competitor-survey.md#4-name-collision-check).

---

<p align="center">
  <sub>Built for people who review technical work for a living.</sub>
</p>
