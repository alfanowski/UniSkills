# Fixtures

Synthetic artifacts used by evaluation cases, when the prompt alone is not enough.

## Rules

- **Synthetic only.** No real credentials, customer data, private repositories, or live malware.
- **Small.** A fixture should be readable in under a minute; if it needs more, the case is testing the
  model's stamina rather than the skill.
- **Stable.** A case that depends on a fixture must pin it by path; do not edit a fixture without
  reviewing every case that references it.
- **Self-describing.** Each fixture starts with a comment stating that it is synthetic and what defect (if
  any) it contains — on a line the analyzed code does not depend on.

## Naming

```text
fixtures/<skill>/<case-topic>/
```

Reference from a case with a path relative to `evals/`:

```yaml
fixture: fixtures/universal-code-review/off-by-one
```

## Current state

No case in this release requires a fixture: every prompt carries its own minimal context, and the four
worked examples under `../examples/` are illustrative rather than executable. This directory exists so
that adding a fixture is a documented, reviewable action rather than an ad-hoc one.
