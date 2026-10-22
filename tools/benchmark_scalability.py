#!/usr/bin/env python3
"""Scalability harness: generate synthetic repositories and time the validators.

The validators are the part of UniSkills that grows with the catalog, so their cost must stay close to
linear in the number of skills. This harness builds throwaway repositories of size N (each skill has a
SKILL.md, one reference, and a three-case eval file, plus catalog and pack metadata) and reports wall
time per phase and peak memory.

It is **not** part of CI: it is a measurement tool, and a timing assertion in CI would be flaky. Run it
before a release, or when changing how skills are discovered or parsed.

Usage:
    python3 tools/benchmark_scalability.py                # 25, 50, 100, 200
    python3 tools/benchmark_scalability.py --sizes 10 500 --repeat 3
"""

from __future__ import annotations

import argparse
import os
import resource
import shutil
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_links  # noqa: E402
import check_secrets  # noqa: E402
import lintlib  # noqa: E402
import validate_catalog  # noqa: E402
import validate_skills  # noqa: E402

CONTRACT_PATH = os.path.join(lintlib.REPO_ROOT, "templates", "operating-contract.md")


def skill_markdown(name, contract):
    return """---
name: {name}
description: Synthetic skill used to measure validator cost at scale. Use when benchmarking the tooling only.
license: MIT
metadata:
  version: "1.0.0"
  status: beta
  updated: "2026-10-22"
  family: engineering
---

# {title}

## Mission

Exercise every validator rule without doing anything useful.

## When to use

- Never, outside this harness.

### When not to use

- Real work.
- Anything with consequences.
- Anywhere a real skill exists.

{contract}
## Workflow

1. Do the first thing.
2. Do the second thing.
3. Check the result.
4. Report the outcome.

## Depth profiles

| Profile | Behavior |
| --- | --- |
| QUICK | Direct answer. |
| STANDARD | Full workflow. |
| DEEP | Extra checks. |
| FORENSIC | Evidence ledger. |

## Output contract

```markdown
# Report
- Finding
- Evidence
```

## Stop conditions

Stop when there is nothing left to measure.

## References

- Read [details.md](references/details.md) for the details.
""".format(name=name, title=name.replace("-", " ").title(), contract=contract)


def cases_markdown(name):
    case = """  - id: {name}-00{i}
    title: Synthetic case {i}
    kind: {kind}
    depth: STANDARD
    prompt: |
      Do the measurement.
    expectations:
      must:
        - Reports a result
        - Cites the harness
      must_not:
        - Invents a number
    rubric:
      correctness: The result is coherent with the input.
      evidence: The harness is cited.
      safety: Nothing external is touched.
"""
    return "skill: %s\ncases:\n" % name + "".join(
        case.format(name=name, i=index, kind=kind)
        for index, kind in enumerate(("standard", "boundary", "false-positive"), start=1)
    )


def build_repository(root, count, contract):
    os.makedirs(os.path.join(root, "templates"))
    with open(os.path.join(root, "templates", "operating-contract.md"), "w", encoding="utf-8") as handle:
        handle.write(contract)

    os.makedirs(os.path.join(root, "catalog"))
    os.makedirs(os.path.join(root, "evals", "cases"))
    os.makedirs(os.path.join(root, "packs"))

    names = ["synthetic-%03d" % index for index in range(count)]
    catalog_lines = ['schema_version: 1', 'updated: "2026-10-22"', "skills:"]
    for name in names:
        skill_dir = os.path.join(root, "skills", name)
        os.makedirs(os.path.join(skill_dir, "references"))
        with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as handle:
            handle.write(skill_markdown(name, contract))
        with open(os.path.join(skill_dir, "references", "details.md"), "w", encoding="utf-8") as handle:
            handle.write("# Details\n\nSynthetic reference.\n")
        with open(os.path.join(root, "evals", "cases", name + ".yaml"), "w", encoding="utf-8") as handle:
            handle.write(cases_markdown(name))
        catalog_lines.extend([
            "  - id: %s" % name,
            "    name: %s" % name.replace("-", " ").title(),
            "    family: engineering",
            "    status: flagship",
            "    maturity: beta",
            "    priority: P3",
            "    summary: Synthetic skill for the scalability harness.",
            "    use_when: Only when measuring the tooling.",
            "    not_for: [real work]",
            "    risk: low",
            "    packs: [synthetic-pack]",
            "    tools_optional: []",
            "    path: skills/%s" % name,
            "    evals: evals/cases/%s.yaml" % name,
            '    last_reviewed: "2026-10-22"',
        ])

    with open(os.path.join(root, "catalog", "skills.yaml"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(catalog_lines) + "\n")

    pack_lines = [
        "schema_version: 1",
        'updated: "2026-10-22"',
        "packs:",
        "  - id: synthetic-pack",
        "    name: Synthetic Pack",
        "    purpose: Measure pack validation at scale.",
        "    audience: The harness.",
        "    doc: packs/synthetic-pack.md",
        "    limitations: It measures nothing useful.",
        "    skills:",
    ]
    pack_lines.extend("      - %s" % name for name in names)
    pack_lines.append("    order:")
    pack_lines.extend("      - %s" % name for name in names)
    with open(os.path.join(root, "catalog", "packs.yaml"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(pack_lines) + "\n")
    with open(os.path.join(root, "packs", "synthetic-pack.md"), "w", encoding="utf-8") as handle:
        handle.write("# Synthetic Pack\n\nGenerated by the scalability harness.\n")


def peak_rss_mb():
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # macOS reports bytes, Linux reports kilobytes.
    return usage / (1024 * 1024) if sys.platform == "darwin" else usage / 1024


def measure(count, contract):
    root = tempfile.mkdtemp(prefix="uniskills-scale-")
    try:
        build_repository(root, count, contract)

        timings = {}
        diagnostics = 0

        start = time.perf_counter()
        lint = lintlib.Lint()
        validate_skills.validate(root)
        timings["skills"] = time.perf_counter() - start
        diagnostics += len(lint.items)

        start = time.perf_counter()
        catalog_lint = lintlib.Lint()
        by_id, _ = validate_catalog.validate_catalog(root, catalog_lint)
        validate_catalog.validate_packs(root, catalog_lint, by_id)
        timings["catalog"] = time.perf_counter() - start
        diagnostics += len(catalog_lint.items)

        start = time.perf_counter()
        link_lint = lintlib.Lint()
        check_links.check(root, link_lint)
        timings["links"] = time.perf_counter() - start
        diagnostics += len(link_lint.items)

        start = time.perf_counter()
        secret_lint = lintlib.Lint()
        check_secrets.scan(root, secret_lint)
        timings["secrets"] = time.perf_counter() - start
        diagnostics += len(secret_lint.items)

        timings["total"] = sum(timings.values())
        return timings, diagnostics, peak_rss_mb()
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Time the validators on synthetic repositories.")
    parser.add_argument("--sizes", nargs="+", type=int, default=[25, 50, 100, 200])
    parser.add_argument("--repeat", type=int, default=1, help="runs per size; the minimum is reported")
    args = parser.parse_args(argv)

    with open(CONTRACT_PATH, encoding="utf-8") as handle:
        contract = handle.read()

    print("| skills | skills.py | catalog.py | links.py | secrets.py | total | peak RSS | diagnostics |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    failures = 0
    for size in args.sizes:
        best = None
        for _ in range(max(1, args.repeat)):
            timings, diagnostics, rss = measure(size, contract)
            if best is None or timings["total"] < best[0]["total"]:
                best = (timings, diagnostics, rss)
        timings, diagnostics, rss = best
        print("| %d | %.3fs | %.3fs | %.3fs | %.3fs | %.3fs | %.0f MB | %d |" % (
            size,
            timings["skills"],
            timings["catalog"],
            timings["links"],
            timings["secrets"],
            timings["total"],
            rss,
            diagnostics,
        ))
        if diagnostics:
            failures += 1
            print("  ^ unexpected diagnostics: the synthetic repository should validate cleanly", file=sys.stderr)

    if failures:
        sys.stderr.write("%d size(s) produced diagnostics; the generator or a validator regressed\n" % failures)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
