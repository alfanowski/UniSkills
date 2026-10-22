# Release Process

## 1. Versioning

Semantic versioning over the **skill behavior**, not the file count:

| Change | Bump |
| --- | --- |
| A skill's workflow, output contract, or verdict vocabulary changes | MINOR at repository level, and the skill's `metadata.version` MAJOR or MINOR per the same rule |
| Wording, references, typos, new examples | PATCH |
| A skill is removed, renamed, or its activation triggers change materially | MAJOR |
| Catalog status changes (`planned` → `flagship`) | MINOR |

Each skill carries its own `metadata.version`. The repository version lives in `CHANGELOG.md`.

## 2. Gates for merging a skill change

All of the following must pass before review:

```bash
python3 tools/validate_skills.py
python3 tools/validate_catalog.py
python3 tools/check_links.py
python3 tools/check_secrets.py
python3 tools/render_catalog.py --check
python3 tools/eval_runner.py --check
python3 -m unittest discover -s tools/tests -t .
```

Plus, for a behavioral change:

- [ ] The skill's eval cases still describe the intended behavior; add a case if the change fixes an
      uncovered failure.
- [ ] `CHANGELOG.md` describes the behavioral change, not the diff.
- [ ] If the operating contract changed, `templates/operating-contract.md` was updated first and all
      skills were synced.
- [ ] If a reference was added, it is linked from `SKILL.md` and used by a workflow step.
- [ ] `metadata.updated` is set to the change date.

## 3. Promoting a skill from `planned` to `flagship`

1. Create `skills/<name>/` with a complete `SKILL.md`, at least two references, and no placeholders.
2. Add `evals/cases/<name>.yaml` with at least three cases: `standard`, a boundary or adversarial case,
   and a false-positive guard.
3. Update `catalog/skills.yaml`: `status: flagship`, `maturity`, `path`, `evals`, `packs`.
4. Add the skill to any pack it belongs to in `catalog/packs.yaml` and to the pack document.
5. Run the full gate list. `render_catalog.py --check` will fail until the views are regenerated.
6. Start at `maturity: beta`, never `stable`. `stable` requires recorded cross-model evaluation.

## 4. Promoting to `stable`

Not yet performed by this project. The requirements:

- All eval cases run at least five times per target model with recorded results.
- Rubric results reported as a distribution, not a single pass/fail.
- At least one documented regression caught by the eval suite.
- Compatibility verified in at least one real client, with the client and version recorded in
  [compatibility.md](compatibility.md).

Until then, `beta` is the ceiling and the catalog says so.

## 5. Release checklist

- [ ] All gates green on the release commit.
- [ ] `CHANGELOG.md` has a dated section with user-visible changes.
- [ ] `docs/compatibility.md` reflects any newly verified environment, with the date.
- [ ] `docs/decision-log.md` updated for any structural decision made during the cycle.
- [ ] No `TODO`/`TBD` markers anywhere (the validator checks skills; check docs manually).
- [ ] `LICENSE` decision confirmed by the owner.
- [ ] Tag created only after the above, and only with explicit authorization.

## 6. Deprecating a skill

1. Set `status: deprecated` in `metadata` and in the catalog, with the reason in `summary`.
2. Keep the directory for one MINOR cycle so existing installs do not break silently.
3. Point to the replacement in the skill's `## Mission` and in `SKILL_CATALOG.md`.
4. Remove the directory at the next MAJOR, and remove its eval cases at the same time.

## 7. What this process does not cover

- Publishing to a marketplace or package registry (no such artifact exists).
- Automated model evaluation (see [decision-log.md](decision-log.md#d8--eval-runner-validates-and-assembles-never-executes)).
- Compatibility testing against real clients (manual, per
  [compatibility.md](compatibility.md)).
