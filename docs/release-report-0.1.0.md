# 0.1.0 Validation Report

**Date:** 2026-10-22
**Author:** implementation agent, under the operating profile of the repository owner
**Status:** first scaffold complete; not released, not published, not evaluated against a model

This report records what was verified, what was not, and what remains open. It is written so that a
reviewer can disagree with a specific line rather than with the whole document.

---

## 1. Repository identification

| Item | Value |
| --- | --- |
| Remote | `https://github.com/alfanowski/UniSkills` |
| Owner | `alfanowski` (verified with `gh api user`) |
| Visibility | public |
| State before work | empty — no commits, no files, no license, `defaultBranchRef` empty |
| Local directory | `~/Desktop/Projects/UniSkills` |
| Branch used | `feat/v0.1.0`; root commit `d5137c2`, with follow-up docs commits on top |
| `origin` remote | unchanged (`git@github.com` rewritten by clone as HTTPS, as configured) |

The repository was cloned from the existing remote; no second repository, organization, or remote was
created. `main` remains unborn locally, consistent with the rule of never committing directly to the main
branch. Publish sequence, if authorized:

```bash
git branch -m feat/v0.1.0 main    # or: git checkout -b main && git merge --ff-only feat/v0.1.0
git push -u origin main
```

No push, tag, release, or issue was created.

## 2. Initial and final state

| | Before | After |
| --- | --- | --- |
| Files | 0 | 119 |
| Commits | 0 | 1 (`d5137c2`) |
| Tracked size | — | ~820 KB |
| Package metadata | none | 12 skills, 6 packs, catalog of 46 entries |
| CI | none | `.github/workflows/validate.yml` (Python 3.9 and 3.12) |
| License | none | MIT (`LICENSE`), pending owner confirmation |

No pre-existing file was overwritten: the working tree was empty.

## 3. Architecture

Three layers, downward references only:

1. **Standard** — `docs/universal-method.md`, `docs/evidence-and-claims.md`,
   `docs/skill-authoring-standard.md`, `docs/context-efficiency.md`, `docs/safety-model.md`.
2. **Skills** — self-contained bundles under `skills/<name>/`, each with `SKILL.md` plus two references.
3. **Packs** — ordered playbooks under `packs/`, referencing skills without duplicating content.

Key decisions and their rationale are in [`decision-log.md`](decision-log.md). Divergences from the
starting specification are itemized in [`spec-reconciliation.md`](spec-reconciliation.md). The four that
shape everything else:

- **D2 — no standalone assembly skill.** The "reason like assembly" instruction is treated as a resolution
  analogy, not a product requirement. Instruction-level analysis lives as an on-demand reference inside
  `reverse-engineering`. The catalog lists `assembly-machine-code-analysis` as `deferred` with the reason.
- **D4 — a compact contract duplicated into every skill.** ~110 words, drift-checked by the validator.
  Chosen over path-based imports (breaks single-skill install) and generated bundles (build complexity).
- **D3 — standard library only.** Includes an in-repo YAML subset parser, differential-tested against
  PyYAML when available.
- **D8 — the eval runner never calls a model.** Schema and prompt assembly only.

## 4. Skills implemented

All 12 are `maturity: beta`, each with 2 references and 3 evaluation cases.

| Skill | Path |
| --- | --- |
| `uniskills-router` | `skills/uniskills-router/` |
| `context-efficiency` | `skills/context-efficiency/` |
| `evidence-validation` | `skills/evidence-validation/` |
| `universal-code-review` | `skills/universal-code-review/` |
| `root-cause-debugging` | `skills/root-cause-debugging/` |
| `architecture-design-review` | `skills/architecture-design-review/` |
| `performance-review` | `skills/performance-review/` |
| `security-review` | `skills/security-review/` |
| `technical-research` | `skills/technical-research/` |
| `technical-brainstorming` | `skills/technical-brainstorming/` |
| `experiment-design-and-falsification` | `skills/experiment-design-and-falsification/` |
| `reverse-engineering` | `skills/reverse-engineering/` |

Packs: `engineering-audit`, `security-audit`, `debugging-and-regression`, `research-to-decision`,
`idea-to-spec`, `reverse-engineering-lab`.

Catalog: 46 entries — 12 flagship, 32 planned, 2 deferred. Planned entries have no directory by design.

## 5. Sources consulted

Full detail, including what was verified versus assumed, is in
[`research-and-competitor-survey.md`](research-and-competitor-survey.md).

| Source | Accessed | License observed |
| --- | --- | --- |
| `agentskills.io/specification` | 2026-10-22 | page: not stated; spec repo: Apache-2.0 |
| `platform.claude.com/.../agent-skills/best-practices` | 2026-10-22 | vendor documentation |
| `developers.openai.com/api/docs/guides/tools-skills` | 2026-10-22 | vendor documentation |
| `github.com/anthropics/skills` | 2026-10-22 | none at repo level; per-skill files, sampled Apache-2.0; doc skills source-available |
| `github.com/agentskills/agentskills` | 2026-10-22 | Apache-2.0 |
| `github.com/erisvulgaris/Reverse-engineer-anything` | 2026-10-22 | MIT |
| `github.com/tihanyin/REx-skill` | 2026-10-22 | MIT |

Nothing was copied. Patterns were reinterpreted; the critique of the 21 KB monolithic `SKILL.md` in
REx-skill is stated in the survey as a design input, not as a claim about that project's quality.

## 6. Validation executed

All commands were run from the repository root on 2026-10-22 with the system Python 3.9.6.

| Command | Result |
| --- | --- |
| `python3 tools/validate_skills.py` | `skills: 12  0 error(s), 0 warning(s)` |
| `python3 tools/validate_catalog.py` | `catalog: 46 skills  0 error(s), 0 warning(s)` |
| `python3 tools/check_links.py` | `links checked: 124  0 error(s), 0 warning(s)` |
| `python3 tools/check_secrets.py` | `secret candidates: 0  personal paths: 0  0 error(s), 0 warning(s)` |
| `python3 tools/render_catalog.py --check` | `catalog views are up to date` |
| `python3 tools/eval_runner.py --check` | `eval cases: 36  0 error(s), 0 warning(s)` |
| `python3 -m unittest discover -s tools/tests -t .` | `Ran 51 tests ... OK` |

Scalability of the validator suite was measured on generated repositories (50–400 skills): total cost
grows linearly at ~5 ms per skill with constant 13 MB peak memory. Method and numbers:
[`scalability.md`](scalability.md).

The unit suite includes negative tests for every validator: a missing section, a drifted contract, an
escaping link, an unlinked reference, a placeholder marker, a two-case eval file, an empty `must_not`,
a stale catalog entry, a broken pack permutation, a broken link, a fixture secret, and an invalid eval
schema.

## 7. Evaluation status

- **36 cases designed**, 3 per skill: 12 `standard`, 12 `false-positive`, 11 `boundary`, 1 `injection`.
- Every case declares `must` (≥ 2) and `must_not` (≥ 1) expectations plus a three-dimension rubric.
- **0 cases executed against a model.** Therefore: no pass rate, no comparison to a baseline, no claim
  that any skill improves output quality.

The protocol for a real run is specified in
[`evaluation-methodology.md`](evaluation-methodology.md): same model and tools, ≥ 5 runs per arm,
blinding, distribution reported.

## 8. Problems found and fixed during the adversarial review

These were found by reviewing this work, not by a third party.

| # | Problem | Fix |
| --- | --- | --- |
| 1 | The YAML parser accepted `key: value: more`, which is invalid YAML and would have failed in PyYAML | Parser now rejects plain scalars containing `": "`; one catalog summary was rewritten |
| 2 | Section detection counted `##` headings inside fenced code blocks, so an output template could satisfy a required section | `lintlib` is now fence-aware for headings, bullets, numbered steps, and links |
| 3 | Block scalars inside sequence items (a case's `prompt:` field) were parsed as a literal `\|` | `_parse_value` handles block scalars in both mapping and sequence positions |
| 4 | `validate_catalog` treated an empty `packs` list as a missing field, rejecting transversal skills | Empty membership allowed; presence of the key still required |
| 5 | Generated catalog linked to `../skills/<id>/SKILL.md` for planned skills that do not exist | Only flagship rows are links; planned rows are code spans |
| 6 | `universal-code-review` used `MINOR`/`NIT`, which are not in its own severity vocabulary | Replaced with `LOW`/`INFO`/`MEDIUM` |
| 7 | Secret scanner skipped `.pem`, so a private key file would pass | Extensions added; a test now asserts detection |
| 8 | Differential YAML test compared GitHub Actions files, where YAML 1.1 coerces `on:` to a boolean | Scope narrowed to catalog and eval files, with the reason documented |
| 9 | Test fixtures embedded a literal personal path and a literal key-shaped string, tripping the repository's own scanners | Both assembled at runtime |
| 10 | README and CHANGELOG claimed 38 tests after the suite had grown | Corrected to 51 |

## 9. Designed but not implemented

| Item | Why it is not here |
| --- | --- |
| 32 planned skills (see `catalog/ROADMAP.md`) | Each needs a workflow, two references, and three eval cases; shipping them thin would violate the standard |
| `stable` maturity | Requires recorded cross-model runs and a regression history |
| Installer / marketplace packaging | Needs dry-run, backup, conflict detection, and uninstall to be safe |
| `skills-ref` as a second validator | Not installed; compatibility unverified |
| Model-backed eval runner | Needs credentials, budget, and determinism controls |
| Contract tests against real clients | No client installed in this environment |
| `evals/fixtures/` content | Current cases carry their context inline; conventions documented |
| Machine-readable finding linter | The JSON schema exists; no validator consumes it yet |

## 10. Limits, assumptions, residual risks

**Environmental**

- Python 3.9.6 is the local interpreter; CI is configured for 3.9 and 3.12 but has not run.
- No network access was used for validation; compatibility claims are therefore format-level.
- macOS only; path handling on Windows is untested.

**Assumptions**

- The reader has a client that loads `SKILL.md` directories.
- The repository owner confirms MIT (see open decisions).
- Catalog entries marked `planned` are acceptable as public roadmap.

**Residual risks**

- Rubrics and skills share an author; shared blind spots are likely.
- Descriptions are validated for shape, not for routing accuracy in a real client.
- The operating contract is duplicated by design; a change requires a repository-wide edit.
- Prompt-injection defenses are instruction-level, not a sandbox.
- The catalog is larger than the implementation, which is a standing invitation to over-claim. The
  generated views label status per row and the validator forbids directories for planned entries.

## 11. Priority roadmap

1. Confirm the license and publish the repository (owner action).
2. Run a real compatibility test in one client and record it in `docs/compatibility.md`.
3. Execute the 36 cases with a recorded protocol; publish the distribution, including failures.
4. Add `test-strategy` and `api-contract-review` — highest value per unit of validation cost.
5. Adopt `skills-ref` as a second structural validator, or document why not.
6. Add a finding linter that consumes `templates/finding-schema.json`.

## 12. Actions requiring authorization

| Action | Status |
| --- | --- |
| Push `feat/v0.1.0` to `origin` / create `main` | not performed |
| Create a tag or GitHub release | not performed |
| Switch license to Apache-2.0 | not performed |
| Install a client or call a model API | not performed |
| Modify repository settings, topics, or description | not performed |
| Delete or rename anything outside the repository | not performed |
