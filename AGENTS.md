# Operating notes for AI agents working on this repository

This file is for agents, not for users. It is intentionally short. The authoritative rules are the
validator and [`docs/skill-authoring-standard.md`](docs/skill-authoring-standard.md).

## Non-negotiables

1. **Never invent results.** Do not write that an eval passed, a benchmark ran, or a client was tested
   unless it was executed in this workspace and the output is quoted.
2. **Run the gates before claiming completion.**
   ```bash
   python3 tools/validate_skills.py
   python3 tools/validate_catalog.py
   python3 tools/check_links.py
   python3 tools/check_secrets.py
   python3 tools/render_catalog.py --check
   python3 tools/eval_runner.py --check
   python3 -m unittest discover -s tools/tests -t .
   ```
3. **No new dependencies.** Standard library only. If a task seems to need PyYAML, use `tools/yamlmini.py`.
4. **No secrets, no personal absolute paths** in any file. `check_secrets.py` enforces part of this.
5. **Do not commit or push** unless explicitly asked. This repository has a remote; treat it as
   production-adjacent.

## Editing rules

- `catalog/skills.yaml` is the source of truth. After editing it, run `python3 tools/render_catalog.py`.
  Never hand-edit `catalog/SKILL_CATALOG.md` or `catalog/ROADMAP.md`.
- The operating contract in every `SKILL.md` must stay byte-identical to
  `templates/operating-contract.md` (whitespace-normalized). If you change the contract, change the
  template first, then every skill, then run the validator.
- A `planned` skill must not have a directory. Do not create empty scaffolding "for later".
- A new reference file must be linked from `SKILL.md` and used by a numbered workflow step. References
  must not link to other references.
- Keep `SKILL.md` under 500 lines; move detail to `references/`.

## Writing rules

- Third person, imperative. "Read the diff", not "you should read".
- Every non-obvious claim gets a label: `VERIFIED`, `DERIVED`, `LIKELY`, `HYPOTHESIS`, `SPECULATIVE`,
  `UNKNOWN`, `N/A`.
- Every finding gets a pointer: `path:line`, symbol, offset, commit, URL + date, or test id.
- No time-sensitive claims ("as of 2025 the best tool is...").
- No adjectives standing in for evidence ("robust", "comprehensive", "world-class").

## When something is blocked

Record the blocker in the relevant document and continue with the independent work. Do not simulate the
blocked step. The project's value depends on the difference between "verified" and "assumed" staying
legible.
