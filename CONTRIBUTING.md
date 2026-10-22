# Contributing to UniSkills

Thanks for considering a contribution. This project is opinionated about method and strict about
evidence, so the contribution path is explicit.

## Before you start

- Read [`docs/vision.md`](docs/vision.md) and [`docs/skill-authoring-standard.md`](docs/skill-authoring-standard.md).
- Read one existing skill end to end: `skills/universal-code-review/` is a good reference.
- For anything larger than a typo, open an issue first. A skill that duplicates an existing one will be
  declined regardless of quality.

## What we accept

| Contribution | Accepted when |
| --- | --- |
| New flagship skill | It covers a capability in `catalog/skills.yaml` with status `planned`, has a distinct workflow, and ships three eval cases |
| New eval case | It targets a real failure mode, especially a false positive or a refusal |
| Bug fix in tooling | It includes a test that fails before the fix |
| Documentation fix | It is accurate; we prefer fewer, sharper sentences |
| New planned catalog entry | It names a capability, not a technology, and does not duplicate an existing row |
| Refactor | It preserves behavior and passes all gates without weakening a check |

## What we decline

- Prompt collections, persona skills, or "act as a 10x engineer" content.
- A skill that wraps one tool invocation.
- Content copied from another project, even with attribution, unless the license permits it **and** the
  value is not reproducible from a primary source.
- Claims of benchmark or quality improvements without a reproducible method and recorded runs.
- Vendored dependencies, installers, or anything requiring network access at validation time.

## Development workflow

```bash
git clone https://github.com/alfanowski/UniSkills.git
cd UniSkills
python3 tools/validate_skills.py     # must pass
python3 tools/validate_catalog.py    # must pass
python3 tools/check_links.py         # must pass
python3 tools/check_secrets.py       # must pass
python3 tools/render_catalog.py --check
python3 tools/eval_runner.py --check
python3 -m unittest discover -s tools/tests -t .
```

No virtualenv is required. Do not add runtime dependencies: the tooling must run on a bare Python 3.8+.

## Adding a skill

1. Copy `templates/skill-template/` to `skills/<your-skill>/`.
2. Fill every required section. The validator enforces names and order:
   `Mission`, `When to use`, `Operating contract`, `Workflow`, `Depth profiles`, `Output contract`,
   `Stop conditions`, `References`.
3. Keep the operating contract **verbatim** from `templates/operating-contract.md`. Do not paraphrase it.
4. Add at least two references. Each must be loaded by a specific workflow step, referenced from
   `SKILL.md`, and must not link to another reference.
5. Write `evals/cases/<your-skill>.yaml` with three cases: `standard`, a boundary/adversarial case, and a
   `false-positive` guard. `must_not` is mandatory and must be specific.
6. Register the skill in `catalog/skills.yaml` (`status: flagship`, `maturity: beta`, `path`, `evals`,
   `packs`) and, if applicable, in `catalog/packs.yaml` and the pack document.
7. Run `python3 tools/render_catalog.py`.
8. Run every gate above.

A skill is reviewed against the checklist in
[`docs/skill-authoring-standard.md`](docs/skill-authoring-standard.md#10-review-checklist-for-a-new-skill),
not against how impressive it sounds.

## Changing an existing skill

Behavioral changes (workflow, output contract, severity vocabulary, activation triggers) require:

- a `CHANGELOG.md` entry describing **what behavior changed**, not which lines moved;
- a new or updated eval case that would have caught the previous gap;
- a `metadata.version` bump and an updated `metadata.updated` date.

Wording improvements do not require a case, but they do require passing gates.

## Tests

- Put tooling tests in `tools/tests/` using `unittest`. No pytest, no fixtures library.
- Test both directions: a validator that never fails is untested.
- For the YAML parser, add the construct to the differential test if PyYAML is available.

## Commit and PR conventions

- One logical change per PR.
- Commit messages: `type(scope): summary`, where `type` is `feat`, `fix`, `docs`, `test`, `refactor`,
  `chore`. Example: `feat(skills): add api-contract-review`.
- PR description must state: what changed, why, which gates were run, and what was **not** verified.
- Do not include generated files by hand; run the renderer instead.
- Do not add an AI co-author trailer naming any tool.

## Review process

Two things are checked, in order:

1. **Structure and evidence** — gates pass, every claim has a pointer, no invented results.
2. **Judgment** — would a competent engineer produce the same shape of output? Does the skill
   over-trigger? Is any step unfalsifiable?

A well-formed skill that gives generic advice will be sent back. That is the point of the project.

## Security-sensitive contributions

If your contribution touches authorization boundaries, execution of untrusted artifacts, or secret
handling, say so in the PR. Do not include real credentials, private data, or live malware samples in
tests or fixtures. See [`SECURITY.md`](SECURITY.md).

## License of contributions

By contributing, you agree that your contribution is licensed under the MIT license of this repository.
