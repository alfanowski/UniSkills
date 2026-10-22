# Changelog

All notable changes are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) applied to skill behavior.

## [0.1.0] — 2026-10-22

First public draft. Status: **beta**, not stable.

### Added

**Twelve flagship skills**

- `uniskills-router` — request classification, skill selection, depth assignment, tool-reality check.
- `context-efficiency` — reading rings, tool-output shaping, evidence reuse keys, checkpoint discipline.
- `evidence-validation` — claim inventory, seven evidence labels, inference audit, source independence.
- `universal-code-review` — eight review lenses, severity/priority/confidence, merge verdicts.
- `root-cause-debugging` — hypothesis ranking, discriminating probes, interventional confirmation.
- `architecture-design-review` — quality-attribute scenarios, failure catalogue, migration and rollback.
- `performance-review` — cost layer model, measurement protocol, bottleneck ranking by decision value.
- `security-review` — trust boundaries, source-to-sink tracing, control register, exploitability gating.
- `technical-research` — query families, source ledger, contradiction search, synthesis by question.
- `technical-brainstorming` — ideation lenses, mechanism-distinctness test, pre-mortem, discriminating
  experiment.
- `experiment-design-and-falsification` — operationalization, confounders, pre-registration, negative
  results.
- `reverse-engineering` — triage, method selection, structure and behavior recovery, ISA/ABI verification
  as an on-demand reference.

**Packs** — engineering-audit, security-audit, debugging-and-regression, research-to-decision,
idea-to-spec, reverse-engineering-lab.

**Catalog** — `catalog/skills.yaml` with 46 entries (12 flagship, 32 planned, 2 deferred), generated
`SKILL_CATALOG.md` and `ROADMAP.md`.

**Evaluation lab** — 36 cases (3 per skill), each with `must` / `must_not` expectations and a
three-dimension rubric.

**Tooling** — dependency-free skill validator, catalog validator, link checker, secret scanner, YAML
subset parser with differential tests, catalog renderer, eval schema validator and prompt assembler.

**Documentation** — vision, architecture, universal method, evidence taxonomy, context policy, safety
model, compatibility, evaluation methodology, installation, release process, decision log, competitor
survey.

**Templates** — skill template, finding JSON schema, evidence ledger, review report, research brief,
experiment plan, ADR.

**Examples** — four worked end-to-end examples with synthetic artifacts.

### Changed from the originating brief

- Removed `assembly-machine-code-analysis` as a flagship skill. Instruction-level analysis is delivered
  as an on-demand reference inside `reverse-engineering`; the catalog records the entry as `deferred`
  with the rationale. See [docs/decision-log.md](docs/decision-log.md#d2--no-standalone-assembly-flagship).
- Added `evidence-validation` as the twelfth flagship, because every other skill depends on claim
  grading.

### Verified

- `tools/validate_skills.py`: 12 skills, 0 errors, 0 warnings.
- `tools/validate_catalog.py`: 46 entries, packs consistent, 0 errors.
- `tools/check_links.py`: all relative links resolve.
- `tools/check_secrets.py`: no secret patterns, no personal absolute paths.
- `tools/eval_runner.py --check`: 36 cases valid.
- `python3 -m unittest discover -s tools/tests -t .`: 51 tests pass.
- Three smoke tasks executed with one cloud model (`beam:cloud` via Ollama): routing produced `NO_SKILL`
  correctly, and two self-contained tasks held the injection boundary and the review output contract.
  Recorded in [docs/local-model-smoke-test.md](docs/local-model-smoke-test.md).

### Not verified

- No evaluation case executed under the documented protocol (five runs per arm, baseline, blind
  scoring). The three-task smoke test is a usability check, not an effectiveness measurement.
- No client integration test. Compatibility is format-level and untested at runtime.
- No performance or token-consumption measurement.
- No independent review of the skill content by a second party.

### Known limitations

- Rubrics and skills were written by the same author; shared blind spots are possible.
- Descriptions are the only routing signal in most clients and are validated only for shape.
- The YAML subset parser rejects valid YAML constructs outside its subset by design.
- Catalog is larger than the implementation; `planned` rows are clearly marked but still a surface for
  over-claiming.

### Pending decisions

- License confirmation (MIT proposed, see [docs/decision-log.md](docs/decision-log.md#open-decisions)).
- Whether the planned-skill list should be public.
- Which client to verify first.
