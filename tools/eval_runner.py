#!/usr/bin/env python3
"""Validate and inspect UniSkills evaluation cases.

This tool deliberately does **not** call any model. It validates case schemas and can assemble a
ready-to-paste prompt for a human or an agent runner. Reporting "eval passed" without a recorded run
would be dishonest, so execution is out of scope by design (see docs/evaluation-methodology.md).

Usage:
    python3 tools/eval_runner.py --check
    python3 tools/eval_runner.py --list
    python3 tools/eval_runner.py --show ucr-001
    python3 tools/eval_runner.py --prompt ucr-001
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lintlib  # noqa: E402
import yamlmini  # noqa: E402

CASE_KINDS = (
    "standard",
    "boundary",
    "adversarial",
    "false-positive",
    "injection",
    "missing-tool",
    "contradictory-evidence",
)
DEPTHS = ("QUICK", "STANDARD", "DEEP", "FORENSIC")
REQUIRED_CASE_FIELDS = ("id", "title", "kind", "depth", "prompt", "expectations", "rubric")


def validate_case_file(path, expected_skill, lint):
    try:
        data = yamlmini.load_file(path)
    except yamlmini.YamlError as exc:
        lint.error(path, "invalid eval YAML: %s" % exc, exc.line)
        return
    except OSError as exc:
        lint.error(path, "cannot read eval file: %s" % exc)
        return

    if not isinstance(data, dict):
        lint.error(path, "eval file must be a mapping")
        return
    if data.get("skill") != expected_skill:
        lint.error(path, "eval 'skill' is %r but should be %r" % (data.get("skill"), expected_skill))

    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 3:
        lint.error(path, "at least three evaluation cases are required")
        return

    kinds = set()
    ids = set()
    for index, case in enumerate(cases):
        where = "cases[%d]" % index
        if not isinstance(case, dict):
            lint.error(path, "%s must be a mapping" % where)
            continue
        for field in REQUIRED_CASE_FIELDS:
            if field not in case or case[field] in (None, "", [], {}):
                lint.error(path, "%s is missing %r" % (where, field))
        case_id = case.get("id")
        if case_id in ids:
            lint.error(path, "duplicate case id %r" % case_id)
        ids.add(case_id)
        if case.get("kind") not in CASE_KINDS:
            lint.error(path, "%s has invalid kind %r" % (where, case.get("kind")))
        else:
            kinds.add(case["kind"])
        if case.get("depth") not in DEPTHS:
            lint.error(path, "%s has invalid depth %r" % (where, case.get("depth")))

        expectations = case.get("expectations") or {}
        must = expectations.get("must") or []
        must_not = expectations.get("must_not") or []
        if len(must) < 2:
            lint.error(path, "%s.expectations.must needs at least two observable requirements" % where)
        if len(must_not) < 1:
            lint.error(path, "%s.expectations.must_not must not be empty (negative space is mandatory)" % where)

        rubric = case.get("rubric") or {}
        if not isinstance(rubric, dict) or len(rubric) < 3:
            lint.error(path, "%s.rubric must define at least three scored dimensions" % where)
        else:
            for key, value in rubric.items():
                if not isinstance(value, str) or len(value) < 20:
                    lint.error(path, "%s.rubric.%s must be a concrete pass/fail description" % (where, key))

        fixture = case.get("fixture")
        if fixture:
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), "..", fixture))
            if not os.path.exists(resolved):
                lint.error(path, "%s.fixture %r does not exist" % (where, fixture))

    if "standard" not in kinds:
        lint.error(path, "at least one case must be kind 'standard'")
    if not kinds & {"boundary", "adversarial", "false-positive", "contradictory-evidence"}:
        lint.error(path, "at least one case must exercise a boundary, adversarial, or false-positive path")


def load_all(root):
    cases_dir = os.path.join(root, "evals", "cases")
    if not os.path.isdir(cases_dir):
        return []
    out = []
    for name in sorted(os.listdir(cases_dir)):
        if not name.endswith(".yaml"):
            continue
        path = os.path.join(cases_dir, name)
        try:
            data = yamlmini.load_file(path)
        except yamlmini.YamlError:
            continue
        for case in (data or {}).get("cases") or []:
            if isinstance(case, dict):
                case["_file"] = path
                case["_skill"] = (data or {}).get("skill")
                out.append(case)
    return out


def build_prompt(root, case):
    skill_path = os.path.join(root, "skills", case["_skill"], "SKILL.md")
    skill_text = lintlib.read_text(skill_path) if os.path.isfile(skill_path) else "(missing SKILL.md)"
    lines = []
    lines.append("# Evaluation run: %s" % case["id"])
    lines.append("")
    lines.append("## Environment")
    lines.append("- Skill under test: `%s`" % case["_skill"])
    lines.append("- Depth profile: `%s`" % case.get("depth"))
    lines.append("- Case kind: `%s`" % case.get("kind"))
    if case.get("fixture"):
        lines.append("- Fixture: `%s` (read it before answering)" % case["fixture"])
    lines.append("")
    lines.append("## Task")
    lines.append(str(case.get("prompt", "")).strip())
    if case.get("context"):
        lines.append("")
        lines.append("## Additional context")
        lines.append(str(case["context"]).strip())
    lines.append("")
    if case.get("fixture"):
        lines.append("")
        lines.append(
            "Runner note: this prompt assumes the runner can read the fixture path above. "
            "If the model has no filesystem access, paste the fixture content inline instead."
        )
    lines.append("")
    lines.append("## Grading contract (do not read before answering)")
    lines.append("The response is scored against the rubric in the case file. Answer as you would for a real user.")
    lines.append("")
    lines.append("## Skill instructions under test")
    lines.append("")
    lines.append(skill_text)
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate and inspect UniSkills eval cases.")
    parser.add_argument("--root", default=lintlib.REPO_ROOT)
    parser.add_argument("--check", action="store_true", help="validate every case file")
    parser.add_argument("--list", action="store_true", help="list all cases")
    parser.add_argument("--show", metavar="CASE_ID", help="print one case as YAML")
    parser.add_argument("--prompt", metavar="CASE_ID", help="assemble a runnable prompt for one case")
    args = parser.parse_args(argv)

    root = args.root
    if args.check or not (args.list or args.show or args.prompt):
        lint = lintlib.Lint()
        cases_dir = os.path.join(root, "evals", "cases")
        total = 0
        for skill_dir in lintlib.iter_skill_dirs(root):
            name = os.path.basename(skill_dir)
            path = os.path.join(cases_dir, name + ".yaml")
            if not os.path.isfile(path):
                lint.error(path, "missing evaluation cases for skill %r" % name)
                continue
            validate_case_file(path, name, lint)
            try:
                total += len(yamlmini.load_file(path).get("cases") or [])
            except Exception:  # noqa: BLE001 - already reported above
                pass
        lint.emit(root=root)
        print("eval cases: %d  %s" % (total, lint.summary()))
        return 1 if lint.errors else 0

    cases = load_all(root)
    if args.list:
        for case in cases:
            print("%-28s %-22s %-11s %s" % (case.get("id"), case.get("_skill"), case.get("kind"), case.get("title")))
        print("\n%d case(s)" % len(cases))
        return 0

    for case in cases:
        if case.get("id") == (args.show or args.prompt):
            if args.prompt:
                print(build_prompt(root, case))
            else:
                printable = {key: value for key, value in case.items() if not key.startswith("_")}
                print(yamlmini.dumps(printable))
            return 0
    sys.stderr.write("case %r not found\n" % (args.show or args.prompt))
    return 2


if __name__ == "__main__":
    sys.exit(main())
