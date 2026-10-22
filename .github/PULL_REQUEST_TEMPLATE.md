## What changed

<!-- One paragraph. Name the artifact, not the diff. -->

## Why

<!-- The failure this prevents, or the capability it adds. -->

## Kind of change

- [ ] New skill
- [ ] Behavioral change to an existing skill
- [ ] New or updated evaluation case
- [ ] Tooling / validator
- [ ] Documentation
- [ ] Catalog / pack metadata
- [ ] Chore

## Gates run

<!-- Paste the actual output tail, or mark as not run and say why. -->

```text
$ python3 tools/validate_skills.py
$ python3 tools/validate_catalog.py
$ python3 tools/check_links.py
$ python3 tools/check_secrets.py
$ python3 tools/render_catalog.py --check
$ python3 tools/eval_runner.py --check
$ python3 -m unittest discover -s tools/tests -t .
```

## Not verified

<!--
Be explicit. Examples: "no model run against the new eval case", "did not test on Windows",
"compatibility not re-checked". An empty section is a claim that everything was verified.
-->

## Checklist

- [ ] Every requirement in `docs/skill-authoring-standard.md` is met (if a skill changed).
- [ ] The operating contract was not paraphrased.
- [ ] New references are linked from `SKILL.md` and used by a workflow step.
- [ ] `metadata.version` and `metadata.updated` were bumped (behavioral change).
- [ ] `CHANGELOG.md` describes the behavioral change.
- [ ] No secrets, tokens, or personal absolute paths were added.
- [ ] I did not hand-edit generated files (`catalog/SKILL_CATALOG.md`, `catalog/ROADMAP.md`).

## Related issues

<!-- Closes #... -->
