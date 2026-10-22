"""Tests for the link checker, the secret scanner, and the eval schema validator."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest

TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS_DIR)

import check_links  # noqa: E402
import check_secrets  # noqa: E402
import eval_runner  # noqa: E402
import lintlib  # noqa: E402


class TempRepo(object):
    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="uniskills-checks-")

    def write(self, relative, content):
        path = os.path.join(self.root, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.repo = TempRepo()

    def tearDown(self):
        self.repo.cleanup()

    def test_broken_relative_link_detected(self):
        self.repo.write("docs/a.md", "See [missing](missing.md).\n")
        lint = lintlib.Lint()
        check_links.check(self.repo.root, lint)
        self.assertEqual(len(lint.errors), 1)
        self.assertIn("broken link", lint.errors[0][3])

    def test_existing_link_passes(self):
        self.repo.write("docs/a.md", "See [b](b.md).\n")
        self.repo.write("docs/b.md", "# B\n")
        lint = lintlib.Lint()
        check_links.check(self.repo.root, lint)
        self.assertEqual(lint.errors, [])

    def test_external_and_anchor_links_ignored(self):
        self.repo.write("docs/a.md", "[web](https://example.com) [here](#section)\n")
        lint = lintlib.Lint()
        check_links.check(self.repo.root, lint)
        self.assertEqual(lint.errors, [])

    def test_link_inside_code_fence_ignored(self):
        self.repo.write("docs/a.md", "```markdown\n[example](does-not-exist.md)\n```\n")
        lint = lintlib.Lint()
        check_links.check(self.repo.root, lint)
        self.assertEqual(lint.errors, [])

    def test_link_escaping_repository_rejected(self):
        self.repo.write("docs/a.md", "[up](../../outside.md)\n")
        lint = lintlib.Lint()
        check_links.check(self.repo.root, lint)
        self.assertEqual(len(lint.errors), 1)
        self.assertIn("escapes the repository", lint.errors[0][3])


class SecretTests(unittest.TestCase):
    def setUp(self):
        self.repo = TempRepo()

    def tearDown(self):
        self.repo.cleanup()

    def test_aws_key_detected_without_leaking_value(self):
        # Assembled at runtime so this test file does not itself contain a key-like literal.
        fake_key = "AKIA" + "ABCDEFGHIJKLMNOP"
        self.repo.write("config.env", "AWS_KEY=%s\n" % fake_key)
        lint = lintlib.Lint()
        found, _ = check_secrets.scan(self.repo.root, lint)
        self.assertEqual(found, 1)
        self.assertIn("aws-access-key-id", lint.errors[0][3])
        self.assertNotIn(fake_key, lint.errors[0][3])

    def test_private_key_block_detected(self):
        marker = "-----BEGIN " + "RSA PRIVATE KEY-----"
        self.repo.write("key.pem", marker + "\n")
        lint = lintlib.Lint()
        found, _ = check_secrets.scan(self.repo.root, lint)
        self.assertEqual(found, 1)

    def test_benign_text_does_not_trigger(self):
        self.repo.write("docs/a.md", "The token bucket refills at 10 requests per second.\n")
        lint = lintlib.Lint()
        found, paths = check_secrets.scan(self.repo.root, lint)
        self.assertEqual((found, paths), (0, 0))

    def test_binary_extension_skipped(self):
        self.repo.write("asset.bin", "AKIA" + "ABCDEFGHIJKLMNOP")
        lint = lintlib.Lint()
        found, _ = check_secrets.scan(self.repo.root, lint)
        self.assertEqual(found, 0)


class EvalSchemaTests(unittest.TestCase):
    def setUp(self):
        self.repo = TempRepo()

    def tearDown(self):
        self.repo.cleanup()

    def base(self, cases):
        return "skill: sample-skill\ncases:\n" + cases

    def one_case(self, case_id, kind, must_not="- something"):
        return """  - id: %s
    title: A case
    kind: %s
    depth: STANDARD
    prompt: Do the thing.
    expectations:
      must:
        - produces a verdict
        - cites a pointer
      must_not:
        %s
    rubric:
      correctness: Finds the real issue and no invented one.
      evidence: Every finding has a file pointer.
      safety: Read-only analysis with no execution of untrusted code.
""" % (case_id, kind, must_not)

    def validate(self, text):
        path = self.repo.write("cases.yaml", text)
        lint = lintlib.Lint()
        eval_runner.validate_case_file(path, "sample-skill", lint)
        return [message for _, _, _, message in lint.items], lint

    def test_valid_file_passes(self):
        text = self.base(
            self.one_case("a-1", "standard")
            + self.one_case("a-2", "boundary")
            + self.one_case("a-3", "false-positive")
        )
        messages, lint = self.validate(text)
        self.assertEqual(lint.errors, [], messages)

    def test_two_cases_rejected(self):
        text = self.base(self.one_case("a-1", "standard") + self.one_case("a-2", "boundary"))
        messages, _ = self.validate(text)
        self.assertTrue(any("at least three" in m for m in messages), messages)

    def test_missing_negative_case_rejected(self):
        text = self.base(
            self.one_case("a-1", "standard")
            + self.one_case("a-2", "standard")
            + self.one_case("a-3", "standard")
        )
        messages, _ = self.validate(text)
        self.assertTrue(any("boundary, adversarial, or false-positive" in m for m in messages), messages)

    def test_wrong_skill_name_rejected(self):
        text = self.base(
            self.one_case("a-1", "standard")
            + self.one_case("a-2", "boundary")
            + self.one_case("a-3", "false-positive")
        ).replace("skill: sample-skill", "skill: other-skill")
        messages, _ = self.validate(text)
        self.assertTrue(any("should be 'sample-skill'" in m for m in messages), messages)


if __name__ == "__main__":
    unittest.main(verbosity=2)
