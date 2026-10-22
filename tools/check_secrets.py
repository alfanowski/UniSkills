#!/usr/bin/env python3
"""Scan the repository for committed secrets and personal absolute paths.

Findings print the matching *pattern name and location*, never the matched value.

Usage:
    python3 tools/check_secrets.py [--root DIR]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lintlib  # noqa: E402

TEXT_EXTENSIONS = {
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".sh",
    ".txt",
    ".cff",
    ".toml",
    ".cfg",
    ".ini",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".svg",
    ".pem",
    ".key",
    ".env",
}

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode", "dist", "build"}

# (name, compiled pattern). Keep these high-precision: a noisy secret scanner gets disabled.
SECRET_PATTERNS = (
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("aws-secret-access-key", re.compile(r"aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("github-fine-grained-token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("openai-style-key", re.compile(r"\bsk-[A-Za-z0-9]{24,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("stripe-live-key", re.compile(r"\bsk_live_[0-9A-Za-z]{20,}\b")),
    ("generic-assignment", re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{24,}['\"]")),
)

PERSONAL_PATH_RE = re.compile(r"(/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+)")


def scan(root, lint):
    secrets = 0
    paths = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for filename in sorted(filenames):
            extension = os.path.splitext(filename)[1].lower()
            if extension not in TEXT_EXTENSIONS and filename not in ("LICENSE", ".gitignore"):
                continue
            path = os.path.join(dirpath, filename)
            try:
                if os.path.getsize(path) > 2_000_000:
                    continue
                text = lintlib.read_text(path)
            except (OSError, UnicodeDecodeError):
                continue
            for name, pattern in SECRET_PATTERNS:
                for match in pattern.finditer(text):
                    line = text.count("\n", 0, match.start()) + 1
                    lint.error(path, "possible %s (value withheld)" % name, line)
                    secrets += 1
            for match in PERSONAL_PATH_RE.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                lint.warn(path, "personal absolute path (portability/privacy)", line)
                paths += 1
    return secrets, paths


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan for committed secrets and personal paths.")
    parser.add_argument("--root", default=lintlib.REPO_ROOT)
    args = parser.parse_args(argv)

    lint = lintlib.Lint()
    secrets, paths = scan(args.root, lint)
    lint.emit(root=args.root)
    print("secret candidates: %d  personal paths: %d  %s" % (secrets, paths, lint.summary()))
    return 1 if lint.errors else 0


if __name__ == "__main__":
    sys.exit(main())
