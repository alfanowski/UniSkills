"""Tests for the skill validator, driven by synthetic repositories."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest

TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS_DIR)

import lintlib  # noqa: E402
import validate_skills  # noqa: E402

REPO_ROOT = os.path.dirname(TOOLS_DIR)
with open(os.path.join(REPO_ROOT, "templates", "operating-contract.md"), encoding="utf-8") as _handle:
    CONTRACT = _handle.read()


def good_skill(name="sample-skill"):
    return """---
name: %s
description: Reviews a bounded technical artifact and returns findings with severity and evidence. Use when asked to inspect a change, a document, or a configuration for defects.
license: MIT
metadata:
  version: "1.0.0"
  status: beta
  updated: "2026-10-22"
  family: engineering
---

# Sample Skill

## Mission

Produce a bounded, evidence-backed verdict on one artifact.

## When to use

Use it for bounded reviews.

### When not to use

- Greenfield design belongs to architecture-design-review.
- Exploit development is out of scope.
- Performance measurement belongs to performance-review.

%s
## Workflow

1. Frame the scope and the deliverable.
2. Read the artifact and record evidence pointers.
3. Test alternative explanations.
4. Produce the verdict with limits.

## Depth profiles

| Profile | Obligations |
| --- | --- |
| QUICK | Direct answer plus one falsification check. |
| STANDARD | Full workflow with evidence pointers. |
| DEEP | Alternative hypotheses and failure matrix. |
| FORENSIC | Hash, timeline, tool versions, coverage gaps. |

## Output contract

```markdown
# Verdict
One finding per record with an evidence pointer and a severity.
```

## Stop conditions

Stop when every claim is labeled and further checks cannot change the verdict.

## References

- Read [details.md](references/details.md) only for domain-specific edge cases.
""" % (name, CONTRACT)


def good_evals(skill_name="sample-skill"):
    return """skill: %s
cases:
  - id: s-001
    title: Standard review
    kind: standard
    depth: STANDARD
    prompt: Review this function for defects.
    expectations:
      must:
        - Names the defect and its trigger
        - Cites the offending line
      must_not:
        - Claims a test was run without running one
    rubric:
      correctness: Identifies the real defect and no invented one.
      evidence: Every finding has a file and line reference.
      safety: Read-only; no execution of untrusted code.
  - id: s-002
    title: Ambiguous artifact
    kind: boundary
    depth: DEEP
    prompt: Review this snippet that is missing its call site.
    expectations:
      must:
        - States which context is missing
        - Labels the conclusion as conditional
      must_not:
        - Invents the caller behavior
    rubric:
      correctness: Handles missing context without guessing.
      evidence: Distinguishes observed from assumed.
      safety: No destructive suggestion.
  - id: s-003
    title: No defect present
    kind: false-positive
    depth: STANDARD
    prompt: Review a correct implementation.
    expectations:
      must:
        - Reports no defect with a scope statement
        - Explains why the obvious suspicious construct is safe
      must_not:
        - Invents a low-severity finding to look useful
    rubric:
      correctness: Does not fabricate findings.
      evidence: Explains the safety argument.
      safety: No unnecessary changes proposed.
""" % skill_name


class Fixture(object):
    """A throwaway repository that satisfies the authoring standard."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="uniskills-test-")
        os.makedirs(os.path.join(self.root, "templates"))
        os.makedirs(os.path.join(self.root, "skills", "sample-skill", "references"))
        os.makedirs(os.path.join(self.root, "skills", "second-skill", "references"))
        os.makedirs(os.path.join(self.root, "evals", "cases"))
        shutil.copy(
            os.path.join(REPO_ROOT, "templates", "operating-contract.md"),
            os.path.join(self.root, "templates", "operating-contract.md"),
        )
        self.write("skills/sample-skill/SKILL.md", good_skill())
        self.write("skills/sample-skill/references/details.md", "# Details\n\nEdge cases.\n")
        self.write("evals/cases/sample-skill.yaml", good_evals())
        self.write("skills/second-skill/SKILL.md", good_skill("second-skill"))
        self.write("skills/second-skill/references/details.md", "# Details\n\nEdge cases.\n")
        self.write("evals/cases/second-skill.yaml", good_evals("second-skill"))

    def path(self, relative):
        return os.path.join(self.root, relative)

    def write(self, relative, content):
        path = self.path(relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def append(self, relative, extra):
        with open(self.path(relative), "a", encoding="utf-8") as handle:
            handle.write(extra)

    def rewrite(self, relative, old, new):
        path = self.path(relative)
        text = lintlib.read_text(path)
        if old not in text:
            raise AssertionError("fixture rewrite target not found: %r" % old)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text.replace(old, new, 1))

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()

    def tearDown(self):
        self.fixture.cleanup()

    def messages(self):
        lint, _ = validate_skills.validate(self.fixture.root)
        return [message for _, _, _, message in lint.items], lint

    def test_good_skill_passes(self):
        messages, lint = self.messages()
        self.assertEqual(lint.errors, [], messages)

    def test_name_directory_mismatch(self):
        self.fixture.rewrite("skills/sample-skill/SKILL.md", "name: sample-skill", "name: other-skill")
        messages, _ = self.messages()
        self.assertTrue(any("does not match directory" in m for m in messages), messages)

    def test_missing_use_when_trigger(self):
        self.fixture.rewrite("skills/sample-skill/SKILL.md", "Use when asked", "Applies to")
        messages, _ = self.messages()
        self.assertTrue(any("Use when" in m for m in messages), messages)

    def test_contract_drift_detected(self):
        self.fixture.rewrite("skills/sample-skill/SKILL.md", "Falsify once.", "Falsify twice.")
        messages, _ = self.messages()
        self.assertTrue(any("operating contract drifted" in m for m in messages), messages)

    def test_link_escaping_skill_is_rejected(self):
        self.fixture.rewrite(
            "skills/sample-skill/SKILL.md",
            "Read [details.md](references/details.md)",
            "Read [x](../other-skill/SKILL.md)",
        )
        messages, _ = self.messages()
        self.assertTrue(any("escapes the skill directory" in m for m in messages), messages)

    def test_unlinked_reference_detected(self):
        self.fixture.write("skills/sample-skill/references/orphan.md", "# Orphan\n")
        messages, _ = self.messages()
        self.assertTrue(any("not linked from SKILL.md" in m for m in messages), messages)

    def test_placeholder_marker_detected(self):
        self.fixture.append("skills/sample-skill/SKILL.md", "\n## Anti-patterns\n\nTODO: write this later.\n")
        messages, _ = self.messages()
        self.assertTrue(any("placeholder" in m for m in messages), messages)

    def test_missing_section_detected(self):
        self.fixture.rewrite("skills/sample-skill/SKILL.md", "## Stop conditions", "## Ending")
        messages, _ = self.messages()
        self.assertTrue(any("Stop conditions" in m for m in messages), messages)

    def test_missing_eval_file_detected(self):
        os.remove(self.fixture.path("evals/cases/sample-skill.yaml"))
        messages, _ = self.messages()
        self.assertTrue(any("missing evaluation cases" in m for m in messages), messages)

    def test_two_case_eval_file_rejected(self):
        text = lintlib.read_text(self.fixture.path("evals/cases/sample-skill.yaml"))
        self.fixture.write("evals/cases/sample-skill.yaml", text.split("  - id: s-003")[0])
        messages, _ = self.messages()
        self.assertTrue(any("at least three evaluation cases" in m for m in messages), messages)

    def test_empty_must_not_rejected(self):
        self.fixture.rewrite(
            "evals/cases/sample-skill.yaml",
            "      must_not:\n        - Claims a test was run without running one\n",
            "      must_not: []\n",
        )
        messages, _ = self.messages()
        self.assertTrue(any("must_not" in m for m in messages), messages)

    def test_absolute_personal_path_rejected(self):
        # Built at runtime so the repository's own secret/path scanner stays clean.
        linux_home = "/" + "Users/" + "someone/project"
        self.fixture.append("skills/sample-skill/SKILL.md", "\nSee %s for details.\n" % linux_home)
        messages, _ = self.messages()
        self.assertTrue(any("absolute personal path" in m for m in messages), messages)


if __name__ == "__main__":
    unittest.main(verbosity=2)
