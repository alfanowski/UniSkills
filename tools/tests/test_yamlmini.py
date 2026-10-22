"""Unit tests for the dependency-free YAML subset parser."""

from __future__ import annotations

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yamlmini  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:  # optional: used only for differential testing
    import yaml as pyyaml
except ImportError:  # pragma: no cover
    pyyaml = None


def _normalize(value):
    """Make PyYAML output comparable with ours (dates -> ISO strings, tuples -> lists)."""
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value


class ScalarTests(unittest.TestCase):
    def test_plain_scalars(self):
        self.assertEqual(yamlmini.load("a: hello world"), {"a": "hello world"})
        self.assertEqual(yamlmini.load("a: 42"), {"a": 42})
        self.assertEqual(yamlmini.load("a: 4.5"), {"a": 4.5})
        self.assertEqual(yamlmini.load("a: true"), {"a": True})
        self.assertEqual(yamlmini.load("a: null"), {"a": None})
        self.assertEqual(yamlmini.load("a: ~"), {"a": None})
        self.assertEqual(yamlmini.load("a:"), {"a": None})

    def test_quoted_scalars(self):
        self.assertEqual(yamlmini.load('a: "1.0.0"'), {"a": "1.0.0"})
        self.assertEqual(yamlmini.load('a: "line\\nbreak"'), {"a": "line\nbreak"})
        self.assertEqual(yamlmini.load("a: 'it''s fine'"), {"a": "it's fine"})

    def test_colon_space_in_plain_scalar_is_rejected(self):
        # YAML treats 'foo: bar' as a nested mapping; our parser must not silently accept it.
        with self.assertRaises(yamlmini.YamlError):
            yamlmini.load("description: foo: bar")
        self.assertEqual(
            yamlmini.load("a: see http://example.com/x")["a"], "see http://example.com/x"
        )

    def test_comment_handling(self):
        self.assertEqual(yamlmini.load("a: value # trailing"), {"a": "value"})
        self.assertEqual(yamlmini.load('a: "value # kept"'), {"a": "value # kept"})
        self.assertEqual(yamlmini.load("# whole line\na: 1"), {"a": 1})


class StructureTests(unittest.TestCase):
    def test_nested_mapping(self):
        text = "outer:\n  inner: 1\n  other: two\n"
        self.assertEqual(yamlmini.load(text), {"outer": {"inner": 1, "other": "two"}})

    def test_sequence_of_scalars(self):
        self.assertEqual(yamlmini.load("items:\n  - a\n  - b\n"), {"items": ["a", "b"]})

    def test_sequence_of_mappings(self):
        text = "items:\n  - id: one\n    value: 1\n  - id: two\n    value: 2\n"
        self.assertEqual(
            yamlmini.load(text),
            {"items": [{"id": "one", "value": 1}, {"id": "two", "value": 2}]},
        )

    def test_sequence_item_with_nested_block(self):
        text = "items:\n  - name: a\n    tags:\n      - x\n      - y\n"
        self.assertEqual(yamlmini.load(text), {"items": [{"name": "a", "tags": ["x", "y"]}]})

    def test_flow_sequence(self):
        self.assertEqual(yamlmini.load("a: [x, y, z]"), {"a": ["x", "y", "z"]})
        self.assertEqual(yamlmini.load("a: []"), {"a": []})

    def test_block_literal(self):
        text = "body: |\n  line one\n  line two\nnext: 1\n"
        self.assertEqual(yamlmini.load(text)["body"], "line one\nline two\n")

    def test_block_folded(self):
        text = "body: >\n  one\n  two\n"
        self.assertEqual(yamlmini.load(text)["body"], "one two\n")

    def test_empty_document(self):
        self.assertIsNone(yamlmini.load(""))
        self.assertIsNone(yamlmini.load("# only a comment\n"))


class ErrorTests(unittest.TestCase):
    def test_tab_indentation_rejected(self):
        with self.assertRaises(yamlmini.YamlError):
            yamlmini.load("a:\n\tb: 1\n")

    def test_anchor_rejected(self):
        with self.assertRaises(yamlmini.YamlError):
            yamlmini.load("a: &anchor value\n")

    def test_flow_mapping_rejected(self):
        with self.assertRaises(yamlmini.YamlError):
            yamlmini.load("a: {b: c}\n")

    def test_duplicate_key_rejected(self):
        with self.assertRaises(yamlmini.YamlError):
            yamlmini.load("a: 1\na: 2\n")

    def test_sequence_at_parent_indent_rejected(self):
        # Explicitly unsupported; the message must point at the offending line.
        with self.assertRaises(yamlmini.YamlError) as caught:
            yamlmini.load("a:\n- one\n- two\n")
        self.assertIsNotNone(caught.exception.line)


@unittest.skipIf(pyyaml is None, "PyYAML not installed; differential test skipped")
class DifferentialTests(unittest.TestCase):
    """Every YAML document our tooling parses must parse identically with PyYAML.

    Scope is deliberate: catalog and evaluation files. CI workflow files are never read by ``yamlmini``,
    and they use YAML 1.1 spellings (``on:``) that PyYAML coerces to a boolean — comparing them would test
    a YAML-version difference, not a parser bug.
    """

    ROOTS = ("catalog", "evals")

    def test_repository_yaml_matches_pyyaml(self):
        checked = 0
        for base in self.ROOTS:
            for dirpath, dirnames, filenames in os.walk(os.path.join(REPO_ROOT, base)):
                dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
                for filename in sorted(filenames):
                    if not filename.endswith((".yaml", ".yml")):
                        continue
                    path = os.path.join(dirpath, filename)
                    with open(path, "r", encoding="utf-8") as handle:
                        text = handle.read()
                    with self.subTest(path=os.path.relpath(path, REPO_ROOT)):
                        self.assertEqual(
                            yamlmini.load(text, source=path),
                            _normalize(pyyaml.safe_load(text)),
                        )
                    checked += 1
        self.assertGreater(checked, 0, "no YAML files found to compare")


if __name__ == "__main__":
    unittest.main(verbosity=2)
