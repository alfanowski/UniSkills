#!/usr/bin/env python3
"""Check that every relative link and image in repository markdown resolves.

Absolute URLs are not fetched: the validator must work offline and deterministically. External link
rot is a maintenance task, not a CI gate.

Usage:
    python3 tools/check_links.py [--root DIR]
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lintlib  # noqa: E402

SCAN_DIRS = ("docs", "packs", "catalog", "examples", "templates", "skills", "evals")
ROOT_FILES = ("README.md", "SECURITY.md", "CHANGELOG.md")


def iter_markdown(root):
    for name in ROOT_FILES:
        path = os.path.join(root, name)
        if os.path.isfile(path):
            yield path
    for directory in SCAN_DIRS:
        base = os.path.join(root, directory)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules", "__pycache__"))
            for filename in sorted(filenames):
                if filename.endswith(".md"):
                    yield os.path.join(dirpath, filename)


def check(root, lint):
    checked = 0
    for path in iter_markdown(root):
        text = lintlib.read_text(path)
        for target, line in lintlib.markdown_links(text):
            checked += 1
            if not target:
                continue
            if target.startswith("//"):
                continue
            resolved = lintlib.resolve_link(path, target)
            if not resolved.startswith(os.path.abspath(root)):
                # Links that climb out of the repository are meaningless for a public repo.
                lint.error(path, "relative link %r escapes the repository" % target, line)
                continue
            if not os.path.exists(resolved):
                lint.error(path, "broken link %r" % target, line)
    return checked


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check relative markdown links.")
    parser.add_argument("--root", default=lintlib.REPO_ROOT)
    args = parser.parse_args(argv)

    lint = lintlib.Lint()
    checked = check(args.root, lint)
    lint.emit(root=args.root)
    print("links checked: %d  %s" % (checked, lint.summary()))
    return 1 if lint.errors else 0


if __name__ == "__main__":
    sys.exit(main())
