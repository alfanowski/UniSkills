#!/usr/bin/env python3
"""Validate the skill catalog, pack manifests, and their consistency with the filesystem.

Usage:
    python3 tools/validate_catalog.py [--root DIR] [--json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lintlib  # noqa: E402
import yamlmini  # noqa: E402

STATUSES = ("flagship", "prototype", "planned", "deferred", "deprecated")
MATURITY = ("draft", "prototype", "beta", "stable", "deprecated")
REQUIRED_FIELDS = (
    "id",
    "name",
    "family",
    "status",
    "priority",
    "summary",
    "use_when",
    "not_for",
    "risk",
    "last_reviewed",
)
FLAGSHIP_FIELDS = ("maturity", "path", "evals", "packs")


def _load(path, lint):
    try:
        return yamlmini.load_file(path)
    except yamlmini.YamlError as exc:
        lint.error(path, "invalid YAML: %s" % exc, exc.line)
        return None
    except OSError as exc:
        lint.error(path, "cannot read file: %s" % exc)
        return None


def validate_catalog(root, lint):
    path = os.path.join(root, "catalog", "skills.yaml")
    data = _load(path, lint)
    if not isinstance(data, dict):
        lint.error(path, "catalog must be a mapping with a 'skills' list")
        return {}, {}

    skills = data.get("skills")
    if not isinstance(skills, list) or not skills:
        lint.error(path, "catalog must contain a non-empty 'skills' list")
        return {}, {}

    by_id = {}
    for index, entry in enumerate(skills):
        where = "skills[%d]" % index
        if not isinstance(entry, dict):
            lint.error(path, "%s must be a mapping" % where)
            continue
        for field in REQUIRED_FIELDS:
            if field not in entry or entry[field] in (None, "", []):
                lint.error(path, "%s is missing required field %r" % (where, field))
        skill_id = entry.get("id")
        if not isinstance(skill_id, str) or not lintlib.SKILL_NAME_RE.match(skill_id):
            lint.error(path, "%s has an invalid id %r" % (where, skill_id))
            continue
        if skill_id in by_id:
            lint.error(path, "duplicate skill id %r" % skill_id)
        by_id[skill_id] = entry

        status = entry.get("status")
        if status not in STATUSES:
            lint.error(path, "%s has invalid status %r" % (skill_id, status))
        if entry.get("family") not in lintlib.FAMILIES:
            lint.error(path, "%s has invalid family %r" % (skill_id, entry.get("family")))
        reviewed = entry.get("last_reviewed")
        if not isinstance(reviewed, str) or not lintlib.DATE_RE.match(reviewed):
            lint.error(path, "%s.last_reviewed must be YYYY-MM-DD" % skill_id)

        not_for = entry.get("not_for")
        if not isinstance(not_for, list) or len(not_for) < 1:
            lint.error(path, "%s.not_for must list at least one exclusion" % skill_id)

        if status == "flagship":
            for field in FLAGSHIP_FIELDS:
                if field not in entry:
                    lint.error(path, "flagship %s is missing field %r" % (skill_id, field))
                elif field != "packs" and entry[field] in (None, "", []):
                    lint.error(path, "flagship %s is missing field %r" % (skill_id, field))
            if entry.get("maturity") not in MATURITY:
                lint.error(path, "%s has invalid maturity %r" % (skill_id, entry.get("maturity")))
            skill_dir = os.path.join(root, entry.get("path", ""))
            skill_md = os.path.join(skill_dir, "SKILL.md")
            if not os.path.isfile(skill_md):
                lint.error(path, "flagship %s points to a missing skill at %r" % (skill_id, entry.get("path")))
            else:
                frontmatter, _, _ = lintlib.split_frontmatter(lintlib.read_text(skill_md))
                try:
                    meta = yamlmini.load(frontmatter or "", source=skill_md)
                except yamlmini.YamlError:
                    meta = None
                if isinstance(meta, dict):
                    declared = (meta.get("metadata") or {}).get("status")
                    if declared != entry.get("maturity"):
                        lint.error(
                            path,
                            "%s maturity %r disagrees with SKILL.md metadata.status %r"
                            % (skill_id, entry.get("maturity"), declared),
                        )
            evals = os.path.join(root, entry.get("evals", ""))
            if not os.path.isfile(evals):
                lint.error(path, "flagship %s points to missing evals at %r" % (skill_id, entry.get("evals")))
        elif status in ("planned", "deferred"):
            if entry.get("path"):
                lint.error(path, "%s is %s but declares a path; planned skills must not exist on disk" % (skill_id, status))

    # Filesystem -> catalog direction: no orphan skill directories.
    for skill_dir in lintlib.iter_skill_dirs(root):
        skill_id = os.path.basename(skill_dir)
        if skill_id not in by_id:
            lint.error(skill_dir, "skill directory is not registered in catalog/skills.yaml")
        elif by_id[skill_id].get("status") != "flagship":
            lint.error(skill_dir, "skill directory exists but catalog status is %r" % by_id[skill_id].get("status"))

    return by_id, data


def validate_packs(root, lint, by_id):
    path = os.path.join(root, "catalog", "packs.yaml")
    data = _load(path, lint)
    if not isinstance(data, dict):
        lint.error(path, "packs catalog must be a mapping with a 'packs' list")
        return

    packs = data.get("packs")
    if not isinstance(packs, list) or not packs:
        lint.error(path, "packs catalog must contain a non-empty 'packs' list")
        return

    seen = set()
    for index, pack in enumerate(packs):
        where = "packs[%d]" % index
        if not isinstance(pack, dict):
            lint.error(path, "%s must be a mapping" % where)
            continue
        pack_id = pack.get("id")
        if not isinstance(pack_id, str) or not lintlib.SKILL_NAME_RE.match(pack_id):
            lint.error(path, "%s has an invalid id %r" % (where, pack_id))
            continue
        if pack_id in seen:
            lint.error(path, "duplicate pack id %r" % pack_id)
        seen.add(pack_id)

        members = pack.get("skills")
        if not isinstance(members, list) or len(members) < 2:
            lint.error(path, "%s must reference at least two skills" % pack_id)
            continue
        for member in members:
            if member not in by_id:
                lint.error(path, "%s references unknown skill %r" % (pack_id, member))
            elif by_id[member].get("status") != "flagship":
                lint.warn(path, "%s references %r which is not a flagship skill yet" % (pack_id, member))
        order = pack.get("order")
        if not isinstance(order, list) or sorted(order) != sorted(members):
            lint.error(path, "%s.order must be a permutation of its skills" % pack_id)

        doc = pack.get("doc")
        if not isinstance(doc, str) or not os.path.isfile(os.path.join(root, doc)):
            lint.error(path, "%s.doc must point to an existing pack document" % pack_id)

        for field in ("purpose", "audience", "limitations"):
            if not pack.get(field):
                lint.error(path, "%s is missing %r" % (pack_id, field))

    # Catalog -> packs direction: declared pack membership must exist in packs.yaml.
    declared = set()
    for pack in packs:
        if isinstance(pack, dict) and isinstance(pack.get("skills"), list):
            for member in pack["skills"]:
                declared.add((member, pack.get("id")))
    for skill_id, entry in by_id.items():
        for pack_id in entry.get("packs") or []:
            if (skill_id, pack_id) not in declared:
                lint.error(path, "%s declares membership in %r which does not list it" % (skill_id, pack_id))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate the UniSkills catalog and packs.")
    parser.add_argument("--root", default=lintlib.REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = args.root
    lint = lintlib.Lint()
    by_id, data = validate_catalog(root, lint)
    validate_packs(root, lint, by_id)

    if args.json:
        print(json.dumps({"skills": len(by_id), "diagnostics": [
            {"level": l, "path": p, "line": n, "message": m} for l, p, n, m in lint.items
        ], "summary": lint.summary()}, indent=2))
    else:
        lint.emit(root=root)
        print("catalog: %d skills  %s" % (len(by_id), lint.summary()))
    return 1 if lint.errors else 0


if __name__ == "__main__":
    sys.exit(main())
