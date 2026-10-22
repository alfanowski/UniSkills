"""Tests for the catalog and pack validator."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest

TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lintlib  # noqa: E402
import validate_catalog  # noqa: E402
import validate_skills  # noqa: E402
from test_validate_skills import Fixture  # noqa: E402


GOOD_CATALOG = """schema_version: 1
updated: "2026-10-22"
skills:
  - id: sample-skill
    name: Sample Skill
    family: engineering
    status: flagship
    maturity: beta
    priority: P1
    summary: Reviews a bounded artifact and returns findings.
    use_when: A bounded review is requested.
    not_for:
      - Greenfield design
    risk: low
    packs:
      - sample-pack
    tools_optional:
      - git
    path: skills/sample-skill
    evals: evals/cases/sample-skill.yaml
    last_reviewed: "2026-10-22"
  - id: second-skill
    name: Second Skill
    family: systems
    status: flagship
    maturity: beta
    priority: P2
    summary: A second skill used to make pack validation meaningful.
    use_when: The pack needs two members.
    not_for:
      - Everything else
    risk: low
    packs:
      - sample-pack
    tools_optional: []
    path: skills/second-skill
    evals: evals/cases/second-skill.yaml
    last_reviewed: "2026-10-22"
  - id: future-skill
    name: Future Skill
    family: systems
    status: planned
    priority: P3
    summary: Not built yet.
    use_when: Later.
    not_for:
      - Now
    risk: medium
    packs: []
    last_reviewed: "2026-10-22"
"""

GOOD_PACKS = """schema_version: 1
updated: "2026-10-22"
packs:
  - id: sample-pack
    name: Sample Pack
    purpose: Exercise the validator.
    audience: Testers.
    doc: packs/sample-pack.md
    limitations: Only two skills.
    skills:
      - sample-skill
      - second-skill
    order:
      - second-skill
      - sample-skill
"""


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()
        self.fixture.write("catalog/skills.yaml", GOOD_CATALOG)
        self.fixture.write("catalog/packs.yaml", GOOD_PACKS)
        self.fixture.write("packs/sample-pack.md", "# Sample Pack\n\nA pack.\n")

    def tearDown(self):
        self.fixture.cleanup()

    def run_validators(self):
        lint = lintlib.Lint()
        by_id, _ = validate_catalog.validate_catalog(self.fixture.root, lint)
        validate_catalog.validate_packs(self.fixture.root, lint, by_id)
        skill_lint, _ = validate_skills.validate(self.fixture.root)
        lint.extend(skill_lint)
        return [message for _, _, _, message in lint.items], lint

    def test_consistent_catalog_passes(self):
        messages, lint = self.run_validators()
        self.assertEqual(lint.errors, [], messages)

    def test_orphan_skill_directory_detected(self):
        self.fixture.write(
            "skills/orphan-skill/SKILL.md",
            lintlib.read_text(self.fixture.path("skills/sample-skill/SKILL.md")).replace(
                "name: sample-skill", "name: orphan-skill", 1
            ),
        )
        messages, _ = self.run_validators()
        self.assertTrue(any("not registered in catalog" in m for m in messages), messages)

    def test_planned_skill_with_directory_detected(self):
        self.fixture.write("skills/future-skill/SKILL.md", "# Placeholder\n")
        messages, _ = self.run_validators()
        self.assertTrue(any("catalog status is 'planned'" in m for m in messages), messages)

    def test_pack_order_must_be_permutation(self):
        self.fixture.write(
            "catalog/packs.yaml",
            GOOD_PACKS.replace("    order:\n      - second-skill\n      - sample-skill\n", "    order: []\n"),
        )
        messages, _ = self.run_validators()
        self.assertTrue(any("permutation" in m for m in messages), messages)

    def test_pack_referencing_unknown_skill(self):
        text = GOOD_PACKS.replace(
            "      - second-skill\n    order:",
            "      - second-skill\n      - ghost-skill\n    order:",
        ).replace("      - sample-skill\n", "      - sample-skill\n      - ghost-skill\n")
        self.fixture.write("catalog/packs.yaml", text)
        messages, _ = self.run_validators()
        self.assertTrue(any("unknown skill" in m for m in messages), messages)

    def test_maturity_mismatch_detected(self):
        self.fixture.write("catalog/skills.yaml", GOOD_CATALOG.replace("maturity: beta", "maturity: stable", 1))
        messages, _ = self.run_validators()
        self.assertTrue(any("disagrees with SKILL.md" in m for m in messages), messages)

    def test_missing_pack_document(self):
        os.remove(self.fixture.path("packs/sample-pack.md"))
        messages, _ = self.run_validators()
        self.assertTrue(any("existing pack document" in m for m in messages), messages)

    def test_declared_pack_membership_must_exist(self):
        self.fixture.write(
            "catalog/packs.yaml",
            GOOD_PACKS.replace("      - second-skill\n    order:", "    order:"),
        )
        messages, _ = self.run_validators()
        self.assertTrue(any("does not list it" in m for m in messages), messages)


if __name__ == "__main__":
    unittest.main(verbosity=2)
