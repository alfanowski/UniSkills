# Tooling

Deterministic checks for the repository. Python 3.8+ standard library only. No network access. No writes
outside the repository (except temporary directories during tests).

| Script | Purpose | Exit code |
| --- | --- | --- |
| `yamlmini.py` | Dependency-free YAML subset parser | raises `YamlError` with a line number |
| `lintlib.py` | Shared diagnostics, fence-aware markdown scanning | library |
| `validate_skills.py` | Frontmatter, sections, contract drift, links, length, eval wiring | 1 on error |
| `validate_catalog.py` | Catalog ↔ filesystem ↔ packs consistency | 1 on error |
| `check_links.py` | Relative markdown links | 1 on broken link |
| `check_secrets.py` | Secret patterns and personal absolute paths | 1 on secret |
| `eval_runner.py` | Eval schema validation, listing, prompt assembly | 1 on invalid case |
| `render_catalog.py` | Generates `SKILL_CATALOG.md` and `ROADMAP.md` | 1 with `--check` if stale |

## Usage

```bash
python3 tools/validate_skills.py
python3 tools/validate_catalog.py
python3 tools/check_links.py
python3 tools/check_secrets.py
python3 tools/render_catalog.py --check
python3 tools/eval_runner.py --check
python3 -m unittest discover -s tools/tests -t .
```

Every script accepts `--root DIR` (except `eval_runner`, which accepts `--root` too) so it can run against
a fixture repository in tests.

## Why a custom YAML parser

The repository must be checkable with no installation step. `yamlmini` supports the subset this project
uses and **rejects** everything else with a line number instead of guessing. Its behaviour is
differential-tested against PyYAML on every catalog and eval file when PyYAML happens to be installed.

Supported: block mappings and sequences, nested combinations, plain/quoted scalars, literal and folded
block scalars, flow sequences of scalars, comments.

Rejected on purpose: anchors and aliases, tags, flow mappings, multi-document streams, tabs for
indentation, sequences at the same indent as their key.

## Design constraints for new tooling

1. Standard library only.
2. Read-only by default; any write must be explicit and inside the repository.
3. Errors must name the file and, where possible, the line.
4. No check may pass silently when its input is unparseable.
5. Every check needs a test that makes it fail.
