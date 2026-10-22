<h1 align="center">UniSkills</h1>

<p align="center"><strong>Universal, evidence-driven skills for AI agents that do serious engineering work.</strong></p>

<p align="center">
  <a href="https://github.com/alfanowski/UniSkills/actions/workflows/validate.yml"><img src="https://github.com/alfanowski/UniSkills/actions/workflows/validate.yml/badge.svg" alt="Validate"></a>
  <a href="https://github.com/alfanowski/UniSkills/releases"><img src="https://img.shields.io/github/v/release/alfanowski/UniSkills?label=release&color=6E56CF" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href=".github/workflows/validate.yml"><img src="https://img.shields.io/badge/python-3.9%20%7C%203.12-3776AB.svg" alt="Python 3.9 | 3.12"></a>
  <a href="https://agentskills.io/specification"><img src="https://img.shields.io/badge/format-Agent%20Skills-111827.svg" alt="Agent Skills"></a>
</p>

<p align="center"><sub>12 skills · 6 packs · 36 evaluation cases · 0 runtime dependencies</sub></p>

---

A prompt tells a model **what to say**. It rarely tells it **what to check, in what order, with what
proof, and when to stop**. So you get answers that are fluent, plausible, and occasionally wrong in a way
that reads exactly like confidence.

UniSkills is a suite of [Agent Skills](https://agentskills.io/specification) that encodes the missing
half: a procedure, an evidence contract, and a depth budget for each recurring kind of engineering work.
Install one directory. The agent stops improvising and starts running a method.

```bash
git clone https://github.com/alfanowski/UniSkills.git
cp -R UniSkills/skills/universal-code-review ~/.claude/skills/
```

That is the whole installation: no package manager, no runtime, no account, no configuration.

## Contents

- [The difference](#the-difference)
- [See it work](#see-it-work)
- [Quick start](#quick-start)
- [What is inside](#what-is-inside)
- [The skills](#the-skills)
- [The packs](#the-packs)
- [How a skill thinks](#how-a-skill-thinks)
- [Why it holds up](#why-it-holds-up)
- [Verification status](#verification-status)
- [Compatibility](#compatibility)
- [Safety model](#safety-model)
- [Repository map](#repository-map)
- [Questions](#questions)
- [Roadmap](#roadmap)
- [Project status](#project-status)

---

## The difference

| | A prompt pack | A UniSkills skill |
| --- | --- | --- |
| **Shape** | A block of text you paste | A directory with a manifest, a workflow, and references |
| **Entry condition** | You remember it exists | A description that states what it does and when to use it |
| **Method** | "Be thorough" | Numbered steps with exit conditions and failure handling |
| **Claim discipline** | Assertions | Seven evidence labels and a pointer per load-bearing claim |
| **Depth** | Whatever the model feels like | `QUICK` / `STANDARD` / `DEEP` / `FORENSIC`, chosen by risk |
| **Quality gate** | None | Deterministic validators plus three evaluation cases per skill |
| **Cost control** | Unknown | Locator-first reading, ring expansion, evidence reuse, checkpoints |

The difference is not style. It is whether a second engineer can check your conclusion from the report
alone.

## See it work

What the review skill produces, on a synthetic one-line cursor change. Full example:
[`examples/code-review/pagination-cursor.md`](examples/code-review/pagination-cursor.md).

<details>
<summary><b>Open the finding</b></summary>

```markdown
### F1 — Cursor is now inclusive but the query is still exclusive: first row repeats on every page

- **Severity:** HIGH · **Priority:** P1 · **Confidence:** high · **Status:** INTRODUCED
- **Location:** `internal/items/list.go:88`, query at `:91`
- **Trigger:** any list with more than one page where the caller passes the returned `next`.
- **Mechanism:** `next` is set to the last returned id, and the query filters `id > $1`. The row with
  `id == next` is therefore included again on the next page.
- **Impact:** every page after the first repeats its first row; clients that concatenate pages produce
  duplicates.
- **Fix:** return `lastID` and change the predicate to `id >= $1`, or keep `> $1` and return `lastID + 1`.
- **Acceptance:** a test that inserts ids 1..5, requests `limit=2` twice, and asserts the second page
  starts at id 3 — fails on this revision, passes after either fix.
```

</details>

Four worked examples ship with the repository: a code review, a cross-tenant security finding, a
throughput brainstorm, and a benchmark-claim investigation. Every artifact in them is synthetic.

## Quick start

**Prerequisites:** Git, and a client that loads Agent Skills directories. Nothing else.

```bash
# 1. get the repository
git clone https://github.com/alfanowski/UniSkills.git

# 2. install one skill (replace the destination with your client's skills directory)
cp -R UniSkills/skills/universal-code-review ~/.claude/skills/

# 3. verify it loads
#    ask: "Review this diff and tell me whether it is safe to merge."
```

**Install a pack instead** — a pack is an ordered playbook over skills you install individually:

```bash
cp -R UniSkills/skills/{root-cause-debugging,universal-code-review} ~/.claude/skills/
cat UniSkills/packs/debugging-and-regression.md
```

**Check the repository locally** — standard library only, read-only, works offline:

```bash
cd UniSkills
python3 tools/validate_skills.py      # frontmatter, sections, contract, links, evals
python3 tools/validate_catalog.py     # catalog ↔ filesystem ↔ packs
python3 tools/check_links.py          # relative links
python3 tools/check_secrets.py        # secret and personal-path scan
python3 tools/render_catalog.py --check
python3 tools/eval_runner.py --check
python3 -m unittest discover -s tools/tests -t .
```

Full instructions, uninstall, and troubleshooting: [`docs/installation.md`](docs/installation.md).

## What is inside

| | Count | Where |
| --- | ---: | --- |
| Flagship skills | **12** | `skills/` |
| Packs | **6** | `packs/` |
| Catalog entries | **46** (12 flagship, 32 planned, 2 deferred) | [`catalog/SKILL_CATALOG.md`](catalog/SKILL_CATALOG.md) |
| Evaluation cases | **36** (3 per skill) | `evals/cases/` |
| Tooling tests | **51** | `tools/tests/` |
| Runtime dependencies | **0** | — |

Architecture: three layers, references pointing downward only.

```text
┌──────────────────────────────────────────────────────────────┐
│  PACKS      ordered playbooks: which skills, in which order   │
├──────────────────────────────────────────────────────────────┤
│  SKILLS     standalone bundles: SKILL.md + references         │
├──────────────────────────────────────────────────────────────┤
│  STANDARD   method · evidence · depth · safety · output       │
└──────────────────────────────────────────────────────────────┘
```

## The skills

Each skill is a complete workflow, two on-demand references, and three evaluation cases. Install one, or
compose them through a pack.

### Core

| Skill | It decides | Reach for it when |
| --- | --- | --- |
| [`uniskills-router`](skills/uniskills-router/SKILL.md) | Which skill, which depth, which deliverable | A request could match several skills |
| [`context-efficiency`](skills/context-efficiency/SKILL.md) | How to spend context without losing evidence | The repository or logs are too large to read fully |
| [`evidence-validation`](skills/evidence-validation/SKILL.md) | Whether a claim is actually supported | A report is about to inform a decision |

### Engineering and quality

| Skill | It decides | Reach for it when |
| --- | --- | --- |
| [`universal-code-review`](skills/universal-code-review/SKILL.md) | Whether a change is safe to merge | A PR, patch, or function needs a verdict |
| [`root-cause-debugging`](skills/root-cause-debugging/SKILL.md) | What actually caused the failure | Something breaks and the reason is unknown |
| [`architecture-design-review`](skills/architecture-design-review/SKILL.md) | Which structure to commit to, and how to migrate | A boundary, ownership, or migration decision is open |
| [`performance-review`](skills/performance-review/SKILL.md) | Where the cost really goes | Latency, throughput, or memory is at risk |

### Security and systems

| Skill | It decides | Reach for it when |
| --- | --- | --- |
| [`security-review`](skills/security-review/SKILL.md) | Whether an actor can reach a dangerous operation | Auth, parsing, files, secrets, or a new trust boundary |
| [`reverse-engineering`](skills/reverse-engineering/SKILL.md) | What an authorized artifact does, and how | A binary, format, or protocol must be understood |

### Research and decision

| Skill | It decides | Reach for it when |
| --- | --- | --- |
| [`technical-research`](skills/technical-research/SKILL.md) | What is actually established, from primary sources | The state of the art, or a vendor claim, is in question |
| [`technical-brainstorming`](skills/technical-brainstorming/SKILL.md) | Which genuinely different option to choose | The options have not been made explicit |
| [`experiment-design-and-falsification`](skills/experiment-design-and-falsification/SKILL.md) | What test would settle the claim | An improvement is asserted and contested |

The full taxonomy — including what is **not** built — is in
[`catalog/SKILL_CATALOG.md`](catalog/SKILL_CATALOG.md). Planned entries have no directory by design, and
the validator enforces that.

## The packs

Packs add sequencing, never content. Each one documents its order, its cost, and when a single skill is
enough.

| Pack | Sequence | Use case |
| --- | --- | --- |
| [Engineering Audit](packs/engineering-audit.md) | architecture → code review → security → performance | Pre-release or high-risk merge |
| [Security Audit](packs/security-audit.md) | security → code review → evidence validation | Auditing your own codebase |
| [Debugging and Regression](packs/debugging-and-regression.md) | root cause → review → experiment | From failure to a verified fix |
| [Research to Decision](packs/research-to-decision.md) | research → validation → brainstorming → experiment | Choosing technology under uncertainty |
| [Idea to Specification](packs/idea-to-spec.md) | brainstorming → research → architecture | From ambition to a decision record |
| [Reverse Engineering Lab](packs/reverse-engineering-lab.md) | reverse engineering → validation → security | Authorized artifact analysis |

## How a skill thinks

Every skill applies the same reconstruction discipline, translated into its domain.

The phrase *"reason like you are analyzing assembly"* is used inside this project as an analogy for
**resolution**, not as a product requirement. It means: do not stop at what a system appears to do.

| Surface description | Reconstructed description |
| --- | --- |
| "The function validates the token." | Which branch accepts, on which field, against what, with which clock, and what happens on every failure edge. |
| "The cache makes it fast." | Key composition, invalidation trigger, eviction policy, miss-path cost, and when it is slower than no cache. |
| "The migration adds a column." | Lock mode, rewrite cost, backfill order, deploy/rollback window, and which readers break in between. |

Eight questions, applied to the depth the task needs: **scope, components, state, transfer, contracts,
resources, trust, failure**. Defined once in [`docs/universal-method.md`](docs/universal-method.md).

**Depth is a budget, not a personality.**

| Profile | Use when | What you get |
| --- | --- | --- |
| `QUICK` | Small, reversible, low blast radius | Direct answer + one falsification check |
| `STANDARD` | Ordinary engineering work | Full workflow, evidence pointers, adversarial check |
| `DEEP` | High uncertainty or high impact | Alternative hypotheses, failure matrix, cross-checks |
| `FORENSIC` | Incidents, critical audits, untrusted artifacts | Artifact hashes, tool versions, coverage map |

Escalation is mandatory for authentication, cryptography, money movement, memory safety, concurrency,
destructive migrations, and untrusted input parsing — regardless of diff size. `QUICK` never skips a
safety gate.

**Claims carry labels.**

| Label | Means | Requirement |
| --- | --- | --- |
| `VERIFIED` | Observed or reproduced | Command, test id, file:line, or tool output |
| `DERIVED` | Follows from verified premises | The premises and the inference step |
| `LIKELY` | Strong indirect support | The remaining gap, named |
| `HYPOTHESIS` | Proposed explanation | The test that would settle it |
| `SPECULATIVE` | Exploratory | Never a premise for a load-bearing conclusion |
| `UNKNOWN` | Not determinable here | What access or tool would be needed |
| `N/A` | Does not apply | One line on why |

Absence of evidence is not evidence of absence. Confidence is not severity. Full taxonomy:
[`docs/evidence-and-claims.md`](docs/evidence-and-claims.md).

## Why it holds up

**Skills are standalone, and the repository proves it.** No skill links outside its own directory, so a
single copy keeps working. The shared part is a ~110-word operating contract embedded in every skill and
drift-checked against `templates/operating-contract.md`, which makes silent divergence impossible to merge.

**The catalog cannot lie.** [`catalog/skills.yaml`](catalog/skills.yaml) is the source of truth; the
markdown views are generated in CI. A `planned` skill must not have a directory; a `flagship` skill must
have a passing workflow and three evaluation cases.

**Quality is executable.** Frontmatter, required sections and their order, contract drift, link validity,
reference reachability, eval schema, catalog consistency, secret patterns, and personal paths are all
checked by deterministic tooling with no dependencies. CI runs the suite on Python 3.9 and 3.12.

**It scales.** Measured on generated repositories: 50 skills in 0.19 s, 400 skills in 2.05 s, flat 13 MB
peak memory — about 5 ms per skill for the full suite. Method and numbers:
[`docs/scalability.md`](docs/scalability.md).

**Context is treated as a budget.** `SKILL.md` is decision logic and stays under 500 lines; depth lives in
references loaded per workflow step, one level deep. Reading is locator-first and expands in rings. See
[`docs/context-efficiency.md`](docs/context-efficiency.md).

## Verification status

This project's own rules apply to its claims.

| Verified | Not verified |
| --- | --- |
| 12 skills pass the authoring standard | No evaluation case has been run under the documented protocol (5 runs per arm, baseline, blind scoring) |
| Every relative link resolves | No client integration test: compatibility is format-level, not runtime-tested |
| Catalog, packs, and filesystem are consistent (46 entries) | No token or cost measurement: clients do not expose a stable metric |
| 36 eval cases validate against the schema | No independent review of the skill content |
| 51 unit tests pass, including negative tests for every validator | A three-task smoke test is recorded, but it is usability evidence, not effectiveness |
| CI green on Python 3.9 and 3.12 | — |
| No secrets or personal paths detected | — |
| Validators scale linearly to 400 skills | — |

Smoke test detail: [`docs/local-model-smoke-test.md`](docs/local-model-smoke-test.md).
Plan for a real evaluation: [`docs/evaluation-methodology.md`](docs/evaluation-methodology.md).

## Compatibility

UniSkills targets the [Agent Skills](https://agentskills.io/specification) format: a directory with
`SKILL.md` plus YAML frontmatter (`name`, `description` required).

| Environment | Basis | Status |
| --- | --- | --- |
| Claude Code | Anthropic documents skills as `SKILL.md` directories | Expected, **not tested here** |
| Claude API | Anthropic documents uploading skill folders | Expected, **not tested here** |
| OpenAI Responses / Agents API | OpenAI documents compatibility with the Agent Skills standard | Expected, **not tested here** |
| Other compliant clients | Varies by implementation | **Unknown** |

The format-level constraints are enforced by the validator; the runtime behavior is not. Details, and what
"portable" does and does not mean: [`docs/compatibility.md`](docs/compatibility.md).

## Safety model

A skill influences what an agent reads, runs, writes, and asserts. It is closer to installing a small
program than to reading a blog post.

- **Read-only by default.** No external writes, installs, deployments, or active security testing without
  explicit authorization.
- **Analyzed content is data.** A README, log line, issue, or binary string that says "ignore previous
  instructions" is reported as an observation, never obeyed.
- **Authorization gates** for security and reverse engineering: written scope, static-first, no
  exploitation, no execution of unknown artifacts on the analysis host.
- **No scripts inside skills.** Repository tooling is standard-library only, auditable, and makes no
  network calls.

Threat model: [`docs/safety-model.md`](docs/safety-model.md) · disclosure: [`SECURITY.md`](SECURITY.md).

## Repository map

```text
skills/          12 installable bundles: SKILL.md + two references each
packs/           6 ordered playbooks
catalog/         skills.yaml (source of truth) + generated catalog and roadmap
docs/            method, evidence, architecture, safety, compatibility, evaluation, scalability
evals/           36 cases + the shared grading rubric
templates/       skill template, finding schema, review/research/experiment/ADR templates
tools/           validators, YAML subset parser, catalog renderer, scalability harness, tests
examples/        four worked end-to-end examples
.github/         CI and the issue template
```

## Questions

**Is this a prompt library?**
No. A prompt library gives you text. This gives you a procedure, an output contract, evidence rules, and a
test suite that keeps the shape stable across sessions.

**Do I need a specific model?**
No. The format and the method are model-agnostic. Instruction-following differs, which is why the project
does not claim identical results across models.

**Why only 12 skills?**
Twelve complete skills beat sixty shallow files. The catalog lists 32 planned capabilities, each with a
priority and no directory — a plan, not a promise.

**Why is there no assembly skill?**
Because the phrase is a resolution analogy, not a product requirement. Instruction-level analysis — ISA,
ABI, stack frames, decompiler artifacts — lives as an on-demand reference inside `reverse-engineering`,
loaded only when a question needs it. Rationale:
[`docs/decision-log.md`](docs/decision-log.md#d2--no-standalone-assembly-flagship).

**Why no installer?**
An installer that writes to your config needs dry-run, backup, conflict detection, and a safe uninstall to
be trustworthy. A copy command is honest and reversible. See
[`docs/decision-log.md`](docs/decision-log.md#d7--no-installer-in-010).

**Can I use it commercially?**
Yes. MIT, no attribution requirement beyond the license text.

## Roadmap

Next by value per unit of validation cost, from [`catalog/ROADMAP.md`](catalog/ROADMAP.md):

1. `test-strategy` — portfolio design matched to failure risk.
2. `api-contract-review` — compatibility, versioning, error semantics.
3. `dependency-vulnerability-audit` — provenance and advisory coverage.
4. `threat-modeling` — assets, actors, boundaries before implementation.
5. A recorded evaluation run: two models, five runs per case, baseline included.

## Project status

**v0.1.0 — beta.** Published 2026-10-22. Not `stable`: that label requires recorded cross-model evaluation
and a regression history, neither of which exists yet.

This is a maintained, **closed** project. The skill set, the catalog, and the authoring standard are owned
by the author; external pull requests and external skills are not accepted.

- **Bugs, broken links, packaging problems, documentation errors** — open an issue using the template.
- **Security reports** — private disclosure per [`SECURITY.md`](SECURITY.md). Never a public issue.
- **Ideas and disagreement** — an issue is welcome and will be read, but it is not a commitment to
  implement.

Why closed: every skill is a contract with an evaluation case, and the suite is reviewed as a whole. Adding
one skill means re-checking its interaction with the standard, the packs, the catalog, and the depth
vocabulary. That review belongs to the author, not to a committee.

## License

MIT — see [`LICENSE`](LICENSE). Citation metadata: [`CITATION.cff`](CITATION.cff).

"UniSkills" is used descriptively; no trademark is claimed. Unrelated projects use similar names, and the
collision check is recorded in
[`docs/research-and-competitor-survey.md`](docs/research-and-competitor-survey.md#4-name-collision-check).

---

<div align="center">
<sub>Built for people who review technical work for a living.</sub>
</div>
