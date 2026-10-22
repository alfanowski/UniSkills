"""Shared linting helpers for the UniSkills validators.

Everything here is standard library only. The goal is deterministic checks with precise locations so
that a contributor can fix a failure without guessing.
"""

from __future__ import annotations

import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RESERVED_NAME_WORDS = ("anthropic", "claude")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.\-]+)?$")
STATUSES = ("draft", "prototype", "beta", "stable", "deprecated")
FAMILIES = (
    "core",
    "engineering",
    "security",
    "performance",
    "systems",
    "research",
    "architecture",
    "ai-ml",
    "documentation",
)

REQUIRED_SECTIONS = (
    "Mission",
    "When to use",
    "Operating contract",
    "Workflow",
    "Depth profiles",
    "Output contract",
    "Stop conditions",
    "References",
)

MAX_BODY_LINES = 500
HARD_BODY_LINES = 700
MAX_DESCRIPTION = 1024

H2_RE = re.compile(r"^##\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")


class Lint(object):
    """Collects diagnostics with a stable, greppable format."""

    def __init__(self):
        self.items = []

    def error(self, path, message, line=None):
        self.items.append(("ERROR", path, line, message))

    def warn(self, path, message, line=None):
        self.items.append(("WARN", path, line, message))

    @property
    def errors(self):
        return [item for item in self.items if item[0] == "ERROR"]

    @property
    def warnings(self):
        return [item for item in self.items if item[0] == "WARN"]

    def extend(self, other):
        self.items.extend(other.items)

    def emit(self, stream=None, root=None):
        import sys

        stream = stream or sys.stdout
        root = root or REPO_ROOT
        for level, path, line, message in self.items:
            try:
                shown = os.path.relpath(path, root)
            except ValueError:
                shown = path
            location = "%s:%s" % (shown, line) if line else shown
            stream.write("%-5s %s: %s\n" % (level, location, message))

    def summary(self):
        return "%d error(s), %d warning(s)" % (len(self.errors), len(self.warnings))


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def split_frontmatter(text):
    """Return ``(frontmatter_text, body, body_start_line)`` or ``(None, body, 1)``.

    The frontmatter must start on the first line with ``---`` and be closed by a ``---`` line.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text, 1
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :]), index + 2
    return None, text, 1


def fence_mask(lines):
    """Return a boolean per line: True when the line is inside (or delimits) a fenced code block.

    Handles nested fences by requiring a closing fence at least as long as the opening one, so a
    four-backtick block can safely contain three-backtick examples.
    """
    mask = [False] * len(lines)
    fence = None
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        match = FENCE_RE.match(stripped)
        if fence is None:
            if match:
                fence = match.group(1)
                mask[index] = True
            continue
        mask[index] = True
        if match and stripped.strip().strip(fence[0]) == "" and len(match.group(1)) >= len(fence):
            fence = None
    return mask


def strip_fences(text):
    """Blank out fenced code blocks while preserving line numbering."""
    lines = text.split("\n")
    mask = fence_mask(lines)
    return "\n".join("" if mask[index] else line for index, line in enumerate(lines))


def h2_sections(body):
    """Return the ordered list of real H2 headings (ignoring fenced examples)."""
    lines = body.split("\n")
    mask = fence_mask(lines)
    sections = []
    for index, line in enumerate(lines):
        if mask[index]:
            continue
        match = H2_RE.match(line)
        if match:
            sections.append(match.group(1).strip())
    return sections


def section_bounds(body, title, level=2):
    """Return ``(start, end)`` line indexes for a heading section, or ``None``."""
    lines = body.split("\n")
    mask = fence_mask(lines)
    prefix = "#" * level
    heading = re.compile(r"^%s\s+(.+?)\s*$" % prefix)
    start = None
    for index, line in enumerate(lines):
        if mask[index]:
            continue
        match = heading.match(line)
        if match and match.group(1).strip() == title:
            start = index + 1
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start, len(lines)):
        if mask[index]:
            continue
        if re.match(r"^#{1,%d}\s+" % level, lines[index]):
            end = index
            break
    return start, end


def section_body(body, title):
    """Return the raw text under an H2 heading, up to the next H2 or H1."""
    bounds = section_bounds(body, title, level=2)
    if bounds is None:
        return ""
    lines = body.split("\n")
    return "\n".join(lines[bounds[0] : bounds[1]]).strip()


def subsection_body(body, title):
    """Return the raw text under an H3 heading, up to the next H3/H2/H1."""
    bounds = section_bounds(body, title, level=3)
    if bounds is None:
        return ""
    lines = body.split("\n")
    return "\n".join(lines[bounds[0] : bounds[1]]).strip()


def iter_skill_dirs(root=None):
    root = root or REPO_ROOT
    skills_root = os.path.join(root, "skills")
    if not os.path.isdir(skills_root):
        return []
    return sorted(
        os.path.join(skills_root, name)
        for name in os.listdir(skills_root)
        if os.path.isdir(os.path.join(skills_root, name)) and not name.startswith(".")
    )


def markdown_links(text):
    """Yield ``(target, line_number)`` for inline links, ignoring images, anchors, and code fences."""
    lines = text.split("\n")
    mask = fence_mask(lines)
    for line_number, line in enumerate(lines, start=1):
        if mask[line_number - 1]:
            continue
        for match in re.finditer(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)", line):
            target = match.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            yield target.split("#", 1)[0], line_number


def resolve_link(source_path, target):
    base = os.path.dirname(source_path)
    return os.path.normpath(os.path.join(base, target))


def count_bullets(text):
    return len(re.findall(r"^\s*[-*]\s+\S", strip_fences(text), re.M))


def count_numbered(text):
    return len(re.findall(r"^\s*\d+\.\s+\S", strip_fences(text), re.M))


def normalize_block(text):
    """Normalize whitespace so the canonical contract can be compared byte-insensitively."""
    return re.sub(r"\s+", " ", text).strip()
