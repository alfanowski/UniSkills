# Decision Log

Architecture decisions, in the order they were made, with the alternatives that were rejected. A decision
is only "closed" when the consequence is visible somewhere in the repository.

---

## D1 — License: MIT

**Status:** proposed, pending owner confirmation.

**Context.** The project is a personal open-source suite of text and tooling, intended for maximum
reuse and easy embedding into other agents' contexts.

**Options.**

| License | Advantage | Cost |
| --- | --- | --- |
| MIT | Shortest, universally understood, no patent clause, trivial to embed | No explicit patent grant; no trademark protection |
| Apache-2.0 | Explicit patent grant, trademark clause, contributor clarity | Long text, notice obligations, more friction when copying snippets |
| CC BY 4.0 (content only) | Natural fit for prose | Mixing licenses for code and text complicates contribution |
| No license | — | Defaults to all rights reserved; blocks adoption |

**Decision.** MIT for the whole repository. For a method-and-text project, the patent grant of Apache-2.0
protects against a risk that is not realistic here, while the notice obligations add friction to the exact
use case (copy a skill into an agent) the project is designed for.

**Consequence.** `LICENSE` at the root. If the owner prefers Apache-2.0, it is a single-file change plus
the `license:` field in 12 frontmatters; the validator checks only that the field is present, not its
value.

---

## D2 — No standalone assembly flagship

**Status:** accepted.

**Context.** The originating brief described reasoning "like during assembly analysis" and listed
`assembly-machine-code-analysis` among the flagship skills. That phrasing is an analogy for analytical
resolution, not a product requirement.

**Decision.** Do not ship an assembly or machine-code skill. Deliver instruction-level analysis as an
on-demand reference (`skills/reverse-engineering/references/low-level-verification.md`) inside the
reverse-engineering capability, and record the entry in the catalog as `deferred` with the reason.

**Consequences.**

- The flagship count is 12 only because `evidence-validation` was added to the original list; the
  catalog documents both the removal and the addition.
- Low-level content still exists where it has value: ISA/ABI, calling conventions, width and signedness,
  decompiler artifacts, and what cannot be recovered.
- The taxonomy keeps `assembly-machine-code-analysis` visible as deferred so a future contributor does
  not re-add it by accident.

**Alternative rejected.** A thin assembly skill that restates the same evidence discipline with an ISA
table. It would duplicate `reverse-engineering` and would be impossible to evaluate meaningfully without a
corpus of binaries.

---

## D3 — Python standard library only

**Status:** accepted.

**Context.** The repository must be checkable by anyone who clones it, including in CI and on a machine
with no package manager access.

**Decision.** No runtime dependencies. No `requirements.txt`. YAML handled by a documented subset parser.

**Consequences.** `tools/yamlmini.py` is maintained in-repo and differential-tested against PyYAML when
available. Unsupported YAML constructs fail loudly rather than being silently misparsed. Contributors
must stay inside the subset when editing catalog or eval files.

**Alternative rejected.** Requiring PyYAML. It is one line to install, and it turns "clone and run the
validator" into "set up an environment first" — a real adoption cost for a project whose audience is
evaluating whether to trust the tooling at all.

---

## D4 — Duplicate a compact operating contract into every skill

**Status:** accepted.

**Context.** Shared doctrine cannot be imported by path without breaking single-skill installation.

**Decision.** A ~110-word contract block is embedded verbatim in each `SKILL.md`, delimited by HTML
comments, and checked for drift by the validator against `templates/operating-contract.md`.

**Consequences.** ~1,300 words duplicated across 12 skills. Any change to the contract requires a
repository-wide edit, enforced by CI. Depth stays in `docs/universal-method.md` and is never duplicated.

**Alternatives rejected.** Generated bundles from a template (build complexity, noisy diffs, contributors
editing generated files); path-based imports (breaks the format's install model).

---

## D5 — Twelve flagship skills, thirty-four planned or deferred

**Status:** accepted.

**Context.** The brief suggested twelve flagship skills including assembly analysis. Quality per skill
matters more than catalog size.

**Decision.** Ship twelve, replacing `assembly-machine-code-analysis` with `evidence-validation`, which is
load-bearing for every other skill. Everything else is a catalog entry with no directory.

**Consequences.** The catalog is intentionally longer than the implementation, and
`catalog/SKILL_CATALOG.md` labels status per row so nobody mistakes a plan for a capability. The validator
fails if a `planned` entry has a directory.

---

## D6 — Catalog YAML is the source of truth; markdown is generated

**Status:** accepted.

**Decision.** `catalog/skills.yaml` drives `SKILL_CATALOG.md` and `ROADMAP.md` through
`tools/render_catalog.py`. CI runs `--check`.

**Consequence.** Contributors edit YAML, not tables. Drift is a build failure rather than an editorial
problem.

---

## D7 — No installer in 0.1.0

**Status:** accepted.

**Context.** Every client has a different skills directory, and some have plugin systems.

**Decision.** Document manual installation. An installer would need dry-run, backup, conflict detection,
and uninstall to be safe; shipping a partial one would be worse than none.

**Consequence.** Setup is two commands and one verification step. The README states it plainly instead of
promising a one-liner.

---

## D8 — Eval runner validates and assembles, never executes

**Status:** accepted.

**Decision.** `tools/eval_runner.py` checks schemas and builds prompts. It does not call a model.

**Rationale.** Model calls need credentials, money, and determinism controls that the repository does not
have. A runner that silently called an API would also make CI dependent on a paid service. Reporting a
pass rate without recorded runs would violate the project's own evidence rules.

**Consequence.** The evaluation layer is a specification plus a harness contract. Results are the
responsibility of whoever runs them, with the protocol in
[evaluation-methodology.md](evaluation-methodology.md).

---

## D9 — Safety posture: read-only by default, authorization for everything external

**Status:** accepted.

**Decision.** No skill performs external writes, installs, deployments, or active security testing without
explicit authorization. Analyzed content is data, never instruction. Unknown binaries are not executed on
the analysis host.

**Consequence.** Some requests end with "this needs authorization" rather than an answer. That is the
intended behavior, and it is tested by eval cases that require refusal (for example `sec-003`, `re-002`,
`ctx-002`).

---

## D10 — Status vocabulary split between catalog and skill maturity

**Status:** accepted.

**Context.** Two different questions: does this exist (catalog), and how proven is it (maturity)?

**Decision.** Catalog `status` is `flagship | prototype | planned | deferred | deprecated`. Skill
`metadata.status` (maturity) is `draft | prototype | beta | stable | deprecated`. The validator requires
them to agree for flagship entries.

**Consequence.** Nothing in this release is marked `stable`. `stable` requires cross-model evaluation and
recorded regressions, which have not been performed.

---

## Open decisions

| # | Question | Owner | Blocks |
| --- | --- | --- | --- |
| O1 | Confirm MIT, or switch to Apache-2.0 | Repository owner | Public release |
| O2 | Whether to publish the planned skill list publicly or keep it internal | Repository owner | README roadmap section |
| O3 | Whether to adopt `skills-ref` as a second validator in CI | Maintainer | Compatibility claim |
| O4 | Target clients for the first verified compatibility run | Maintainer | `docs/compatibility.md` |
