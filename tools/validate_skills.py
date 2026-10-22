#!/usr/bin/env python3
"""Validate every UniSkills skill against the authoring standard.

Checks (see docs/skill-authoring-standard.md):
  * SKILL.md presence and YAML frontmatter validity
  * name / description / license / metadata constraints
  * required H2 sections, in order
  * canonical operating-contract block (byte-identical after whitespace normalization)
  * body length budget
  * depth-profile coverage
  * "when not to use" has real exclusions
  * local links resolve and stay inside the skill directory
  * every reference file is reachable from SKILL.md, one level deep
  * no placeholder markers, no absolute personal paths

Usage:
    python3 tools/validate_skills.py [--root DIR] [--strict] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lintlib  # noqa: E402
import yamlmini  # noqa: E402

PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX|WIP|coming soon|lorem ipsum)\b", re.I)
ABSOLUTE_PATH_RE = re.compile(r"(/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|[A-Za-z]:\\\\Users)")
DEPTH_PROFILES = ("QUICK", "STANDARD", "DEEP", "FORENSIC")


def load_contract(root):
    """Return the normalized inner text of the canonical operating contract."""
    path = os.path.join(root, "templates", "operating-contract.md")
    if not os.path.isfile(path):
        return None
    text = lintlib.read_text(path)
    if "<!-- uni:contract -->" not in text or "<!-- /uni:contract -->" not in text:
        return None
    inner = text.split("<!-- uni:contract -->", 1)[1].split("<!-- /uni:contract -->", 1)[0]
    return lintlib.normalize_block(inner)


def check_frontmatter(lint, skill_dir, data, path):
    if not isinstance(data, dict):
        lint.error(path, "frontmatter must be a mapping")
        return

    name = data.get("name")
    dirname = os.path.basename(skill_dir)
    if not isinstance(name, str) or not name:
        lint.error(path, "frontmatter field 'name' is required")
    else:
        if not lintlib.SKILL_NAME_RE.match(name):
            lint.error(path, "name %r must be lowercase alphanumeric words separated by single hyphens" % name)
        if len(name) > 64:
            lint.error(path, "name is %d characters (max 64)" % len(name))
        if name != dirname:
            lint.error(path, "name %r does not match directory %r" % (name, dirname))
        for word in lintlib.RESERVED_NAME_WORDS:
            if word in name:
                lint.error(path, "name must not contain reserved word %r" % word)

    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        lint.error(path, "frontmatter field 'description' is required")
    else:
        if len(description) > lintlib.MAX_DESCRIPTION:
            lint.error(path, "description is %d characters (max %d)" % (len(description), lintlib.MAX_DESCRIPTION))
        if len(description) < 80:
            lint.warn(path, "description is only %d characters; it must let a router decide without reading the body" % len(description))
        if re.search(r"<[A-Za-z/]", description):
            lint.error(path, "description must not contain XML tags")
        if not re.search(r"\buse when\b", description, re.I):
            lint.error(path, "description must contain an explicit 'Use when' trigger clause")
        if re.match(r"^(I|You|We)\b", description):
            lint.error(path, "description must be written in third person")

    license_name = data.get("license")
    if not license_name:
        lint.error(path, "frontmatter field 'license' is required")

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        lint.error(path, "frontmatter field 'metadata' must be a mapping")
        return
    version = metadata.get("version")
    if not isinstance(version, str) or not lintlib.SEMVER_RE.match(version):
        lint.error(path, "metadata.version must be a quoted SemVer string")
    status = metadata.get("status")
    if status not in lintlib.STATUSES:
        lint.error(path, "metadata.status must be one of %s" % ", ".join(lintlib.STATUSES))
    updated = metadata.get("updated")
    if not isinstance(updated, str) or not lintlib.DATE_RE.match(updated):
        lint.error(path, "metadata.updated must be a YYYY-MM-DD string")
    family = metadata.get("family")
    if family not in lintlib.FAMILIES:
        lint.error(path, "metadata.family must be one of %s" % ", ".join(lintlib.FAMILIES))

    compatibility = data.get("compatibility")
    if compatibility is not None and (not isinstance(compatibility, str) or len(compatibility) > 500):
        lint.error(path, "compatibility must be a string of at most 500 characters")


def check_body(lint, skill_dir, body, body_line, path, canonical_contract):
    sections = lintlib.h2_sections(body)
    if not body.lstrip().startswith("# "):
        lint.error(path, "body must start with a level-1 title")

    missing = [section for section in lintlib.REQUIRED_SECTIONS if section not in sections]
    for section in missing:
        lint.error(path, "missing required section '## %s'" % section)

    if not missing:
        positions = [sections.index(section) for section in lintlib.REQUIRED_SECTIONS]
        if positions != sorted(positions):
            lint.error(path, "required sections are out of order: expected %s" % " -> ".join(lintlib.REQUIRED_SECTIONS))

    line_count = len(body.split("\n"))
    if line_count > lintlib.HARD_BODY_LINES:
        lint.error(path, "body has %d lines (hard limit %d)" % (line_count, lintlib.HARD_BODY_LINES))
    elif line_count > lintlib.MAX_BODY_LINES:
        lint.warn(path, "body has %d lines (target <= %d); move detail into references/" % (line_count, lintlib.MAX_BODY_LINES))

    contract = lintlib.section_body(body, "Operating contract")
    if canonical_contract:
        if "<!-- uni:contract -->" not in contract or "<!-- /uni:contract -->" not in contract:
            lint.error(path, "operating contract must be delimited by <!-- uni:contract --> markers")
        else:
            embedded = contract.split("<!-- uni:contract -->", 1)[1].split("<!-- /uni:contract -->", 1)[0]
            if lintlib.normalize_block(embedded) != canonical_contract:
                lint.error(
                    path,
                    "operating contract drifted from templates/operating-contract.md; copy it verbatim",
                )
    elif "<!-- uni:contract -->" not in contract:
        lint.warn(path, "operating contract markers missing")

    depth = lintlib.section_body(body, "Depth profiles")
    for profile in DEPTH_PROFILES:
        if profile not in depth:
            lint.error(path, "depth profiles section does not mention %s" % profile)
    if "|" not in depth:
        lint.error(path, "depth profiles must be a table")

    when_not = lintlib.subsection_body(body, "When not to use")
    if not when_not:
        lint.error(path, "missing '### When not to use' subsection")
    elif lintlib.count_bullets(when_not) < 3:
        lint.error(path, "'When not to use' must list at least three concrete exclusions")

    workflow = lintlib.section_body(body, "Workflow")
    numbered = lintlib.count_numbered(workflow)
    if numbered < 4:
        lint.error(path, "workflow must have at least four numbered steps (found %d)" % numbered)

    output = lintlib.section_body(body, "Output contract")
    if len(output.split("\n")) < 4:
        lint.error(path, "output contract is too thin; define the artifact shape")

    references_section = lintlib.section_body(body, "References")
    if not references_section:
        lint.error(path, "references section is empty")

    for marker in PLACEHOLDER_RE.finditer(body):
        lint.error(path, "placeholder marker %r found in body" % marker.group(0))

    for match in ABSOLUTE_PATH_RE.finditer(body):
        lint.error(path, "absolute personal path %r must not appear in a skill" % match.group(0))

    for target, line_number in lintlib.markdown_links(body):
        resolved = lintlib.resolve_link(path, target)
        skill_root = os.path.abspath(skill_dir) + os.sep
        if not os.path.abspath(resolved).startswith(skill_root):
            lint.error(path, "link %r escapes the skill directory (skills must be standalone)" % target, line_number)
        elif not os.path.exists(resolved):
            lint.error(path, "link target %r does not exist" % target, line_number)

    references_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(references_dir):
        on_disk = sorted(
            "references/" + name for name in os.listdir(references_dir) if name.endswith(".md")
        )
        if not on_disk:
            lint.error(path, "references/ exists but contains no markdown files")
        linked = set()
        for target, _ in lintlib.markdown_links(body):
            if target.startswith("references/"):
                linked.add(os.path.normpath(target).replace(os.sep, "/"))
        for name in on_disk:
            if name not in linked:
                lint.error(path, "%s is not linked from SKILL.md" % name)
        for name in linked:
            if name not in on_disk:
                lint.error(path, "linked reference %r is missing on disk" % name)

    # Nested reference chains are a documented anti-pattern: references must not link to references.
    for entry in sorted(os.listdir(references_dir)) if os.path.isdir(references_dir) else []:
        if not entry.endswith(".md"):
            continue
        ref_path = os.path.join(references_dir, entry)
        ref_text = lintlib.read_text(ref_path)
        for target, line_number in lintlib.markdown_links(ref_text):
            if target.endswith(".md") and not os.path.basename(target).startswith(("http", "#")):
                lint.warn(ref_path, "reference links to another document (%r); keep references one level deep" % target, line_number)


def validate(root=None, strict=False):
    root = root or lintlib.REPO_ROOT
    lint = lintlib.Lint()
    canonical_contract = load_contract(root)
    skill_dirs = lintlib.iter_skill_dirs(root)
    if not skill_dirs:
        lint.error(os.path.join(root, "skills"), "no skill directories found")

    for skill_dir in skill_dirs:
        skill_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.isfile(skill_path):
            lint.error(skill_dir, "missing SKILL.md")
            continue
        text = lintlib.read_text(skill_path)
        frontmatter, body, body_line = lintlib.split_frontmatter(text)
        if frontmatter is None:
            lint.error(skill_path, "missing YAML frontmatter delimited by '---'")
            continue
        try:
            data = yamlmini.load(frontmatter, source=skill_path)
        except yamlmini.YamlError as exc:
            lint.error(skill_path, "invalid frontmatter YAML: %s" % exc, exc.line)
            continue
        check_frontmatter(lint, skill_dir, data, skill_path)
        check_body(lint, skill_dir, body, body_line, skill_path, canonical_contract)

        # Eval wiring: every skill in the repo needs at least three cases.
        cases_path = os.path.join(root, "evals", "cases", os.path.basename(skill_dir) + ".yaml")
        if not os.path.isfile(cases_path):
            lint.error(skill_path, "missing evaluation cases at evals/cases/%s.yaml" % os.path.basename(skill_dir))
        else:
            import eval_runner

            eval_runner.validate_case_file(cases_path, os.path.basename(skill_dir), lint)

    if strict:
        for level, path, line, message in list(lint.items):
            if level == "WARN":
                lint.error(path, message, line)
        lint.items = [item for item in lint.items if item[0] == "ERROR"]

    return lint, len(skill_dirs)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate UniSkills skills.")
    parser.add_argument("--root", default=lintlib.REPO_ROOT, help="repository root")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    lint, total = validate(args.root, strict=args.strict)
    if args.json:
        payload = {
            "skills": total,
            "errors": [{"level": l, "path": p, "line": n, "message": m} for l, p, n, m in lint.items],
            "summary": lint.summary(),
        }
        print(json.dumps(payload, indent=2))
    else:
        lint.emit(root=args.root)
        print("skills: %d  %s" % (total, lint.summary()))
    return 1 if lint.errors else 0


if __name__ == "__main__":
    sys.exit(main())
