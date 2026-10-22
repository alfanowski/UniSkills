"""Dependency-free YAML subset parser used by the UniSkills validators.

Why this exists
---------------
UniSkills must be installable and checkable with a bare Python 3 interpreter: no PyYAML, no pip
install, no network. The repository only needs a small, well-defined slice of YAML, so we implement
that slice explicitly and *reject* everything else instead of silently mis-parsing it.

Supported subset
----------------
- Block mappings:            ``key: value`` with 2-space (or any consistent) indentation
- Block sequences:           ``- item`` and ``- key: value``, indented under their parent key
- Nested combinations of the two
- Plain scalars, single-quoted, double-quoted (with ``\\n``, ``\\t``, ``\\"``, ``\\\\`` escapes)
- Block scalars:             ``|`` (literal) and ``>`` (folded), with optional ``-`` chomping
- Flow sequences of scalars: ``[a, b, c]``
- Comments starting with ``#`` outside quotes
- ``true`` / ``false`` / ``null`` / ``~`` / integers / floats

Deliberately unsupported (raises ``YamlError`` with a line number)
-------------------------------------------------------------------
anchors/aliases (``&``, ``*``), tags (``!!``), flow mappings (``{a: b}``), multi-document streams,
complex keys, tabs used for indentation, sequences at the same indent as their key.

The parser is validated against PyYAML in ``tools/tests/test_yamlmini.py`` when PyYAML happens to be
installed, and against hand-written expectations in every other case.
"""

from __future__ import annotations

import json
import re


class YamlError(ValueError):
    """Raised for malformed or unsupported YAML input."""

    def __init__(self, message, line=None):
        self.line = line
        super().__init__("line %s: %s" % (line, message) if line else message)


_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")
_KEY_RE = re.compile(r"^([A-Za-z0-9_.\-/]+)\s*:(?:\s+(.*))?$")


def load(text, source="<string>"):
    """Parse a YAML document from ``text`` and return Python data."""
    parser = _Parser(text, source)
    return parser.parse()


def load_file(path):
    """Parse a YAML document from a filesystem path."""
    with open(path, "r", encoding="utf-8") as handle:
        return load(handle.read(), source=str(path))


# --------------------------------------------------------------------------------------------
# internals
# --------------------------------------------------------------------------------------------


class _Line(object):
    __slots__ = ("number", "indent", "content", "raw")

    def __init__(self, number, indent, content, raw):
        self.number = number
        self.indent = indent
        self.content = content
        self.raw = raw


class _Parser(object):
    def __init__(self, text, source):
        self.source = source
        self.raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        self.lines = self._tokenize(self.raw_lines)
        self.pos = 0

    # -- tokenizing ---------------------------------------------------------------------------

    def _tokenize(self, raw_lines):
        lines = []
        for index, raw in enumerate(raw_lines, start=1):
            if "\t" in raw[: len(raw) - len(raw.lstrip())]:
                raise YamlError("tabs are not allowed for indentation", index)
            stripped = raw.strip()
            if not stripped:
                lines.append(_Line(index, -1, "", raw))
                continue
            if stripped.startswith("#"):
                lines.append(_Line(index, -1, "", raw))
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            content = _strip_comment(raw[indent:]).rstrip()
            if not content:
                lines.append(_Line(index, -1, "", raw))
                continue
            if content.startswith("%"):
                raise YamlError("directives are not supported", index)
            if content.startswith("&") or content.startswith("*"):
                raise YamlError("anchors and aliases are not supported", index)
            if content.startswith("!!") or content.startswith("!"):
                raise YamlError("tags are not supported", index)
            if content == "---" or content == "...":
                raise YamlError("multi-document streams are not supported", index)
            lines.append(_Line(index, indent, content, raw))
        return lines

    def _peek(self):
        while self.pos < len(self.lines) and self.lines[self.pos].indent < 0:
            self.pos += 1
        if self.pos >= len(self.lines):
            return None
        return self.lines[self.pos]

    # -- entry point --------------------------------------------------------------------------

    def parse(self):
        first = self._peek()
        if first is None:
            return None
        value = self._parse_block(first.indent)
        trailing = self._peek()
        if trailing is not None:
            raise YamlError("unexpected content (check indentation)", trailing.number)
        return value

    def _parse_block(self, indent):
        first = self._peek()
        if first is None:
            return None
        if first.content.startswith("-"):
            return self._parse_sequence(indent)
        return self._parse_mapping(indent)

    # -- sequences ----------------------------------------------------------------------------

    def _parse_sequence(self, indent):
        items = []
        while True:
            line = self._peek()
            if line is None or line.indent != indent or not line.content.startswith("-"):
                break
            rest = line.content[1:]
            if rest and not rest.startswith(" "):
                raise YamlError("malformed sequence entry", line.number)
            rest = rest.strip()
            self.pos += 1
            if not rest:
                child = self._peek()
                if child is not None and child.indent > indent:
                    items.append(self._parse_block(child.indent))
                else:
                    items.append(None)
            elif _looks_like_mapping(rest):
                items.append(self._parse_inline_mapping(rest, line, indent))
            else:
                items.append(_parse_scalar(rest, line.number))
        return items

    def _parse_inline_mapping(self, text, line, parent_indent):
        """Parse ``- key: value`` where the map may continue on following lines."""
        mapping = {}
        key_indent = parent_indent + 2
        key, value = _split_key_value(text, line.number)
        mapping[key] = self._parse_value(value, key_indent, line.number)
        while True:
            nxt = self._peek()
            if nxt is None or nxt.indent < key_indent:
                break
            if nxt.indent > key_indent:
                raise YamlError("unexpected indentation inside a sequence item", nxt.number)
            if nxt.content.startswith("-"):
                break
            key, value = _split_key_value(nxt.content, nxt.number)
            if key in mapping:
                raise YamlError("duplicate key %r" % key, nxt.number)
            self.pos += 1
            mapping[key] = self._parse_value(value, key_indent, nxt.number)
        return mapping

    def _parse_value(self, value, parent_indent, number):
        """Parse the value part of ``key: <value>``, including nested blocks and block scalars."""
        if not value:
            child = self._peek()
            if child is not None and child.indent > parent_indent:
                return self._parse_block(child.indent)
            return None
        if value[0] in "|>":
            return self._parse_block_scalar(value, parent_indent, number)
        return _parse_scalar(value, number)

    # -- mappings -----------------------------------------------------------------------------

    def _parse_mapping(self, indent):
        mapping = {}
        while True:
            line = self._peek()
            if line is None or line.indent != indent:
                break
            if line.content.startswith("-"):
                raise YamlError("sequence entry where a mapping key was expected", line.number)
            key, value = _split_key_value(line.content, line.number)
            if key in mapping:
                raise YamlError("duplicate key %r" % key, line.number)
            self.pos += 1
            mapping[key] = self._parse_value(value, indent, line.number)
        return mapping

    def _parse_block_scalar(self, header, parent_indent, number):
        style = header[0]
        chomp = header[1:2]
        if style not in "|>":
            raise YamlError("unsupported block scalar indicator %r" % header, number)
        if chomp not in ("", "-", "+"):
            raise YamlError("unsupported block scalar chomping %r" % header, number)
        collected = []
        block_indent = None
        index = self.pos
        while index < len(self.lines):
            line = self.lines[index]
            if line.indent < 0:
                collected.append("")
                index += 1
                continue
            if line.indent <= parent_indent:
                break
            if block_indent is None:
                block_indent = line.indent
            collected.append(line.raw[block_indent:] if len(line.raw) >= block_indent else "")
            index += 1
        self.pos = index
        while collected and collected[-1] == "":
            collected.pop()
        if style == "|":
            text = "\n".join(collected)
        else:
            folded = []
            for entry in collected:
                if entry == "":
                    folded.append("\n")
                elif folded and folded[-1] not in ("", "\n"):
                    folded[-1] = folded[-1] + " " + entry.strip()
                else:
                    folded.append(entry.strip())
            text = "".join(folded)
        if chomp == "-":
            return text.rstrip("\n")
        return text + "\n" if text else text


# --------------------------------------------------------------------------------------------
# scalar handling
# --------------------------------------------------------------------------------------------


def _looks_like_mapping(text):
    return bool(_KEY_RE.match(text)) and not text.startswith(("'", '"', "["))


def _split_key_value(text, number):
    match = _KEY_RE.match(text)
    if not match:
        raise YamlError("expected 'key: value' (unsupported key or flow mapping)", number)
    key = match.group(1)
    value = (match.group(2) or "").strip()
    return key, value


def _strip_comment(text):
    in_single = False
    in_double = False
    for index, char in enumerate(text):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            if index == 0 or text[index - 1] in " \t":
                return text[:index]
    return text


def _parse_scalar(text, number):
    text = text.strip()
    if text == "":
        return None
    if text[0] in "&*":
        raise YamlError("anchors and aliases are not supported", number)
    if text[0] == "!":
        raise YamlError("tags are not supported", number)
    if text.startswith("{"):
        raise YamlError("flow mappings are not supported", number)
    if text.startswith("["):
        return _parse_flow_sequence(text, number)
    if text.startswith('"'):
        return _parse_double_quoted(text, number)
    if text.startswith("'"):
        return _parse_single_quoted(text, number)
    if ": " in text or text.endswith(":"):
        raise YamlError("plain scalars must not contain ': ' (quote the value)", number)
    lowered = text.lower()
    if lowered in ("true", "false"):
        return lowered == "true"
    if lowered in ("null", "~"):
        return None
    if _INT_RE.match(text):
        return int(text)
    if _FLOAT_RE.match(text):
        return float(text)
    return text


def _parse_flow_sequence(text, number):
    if not text.endswith("]"):
        raise YamlError("unterminated flow sequence", number)
    inner = text[1:-1].strip()
    if not inner:
        return []
    parts = _split_top_level(inner, number)
    return [_parse_scalar(part, number) for part in parts]


def _split_top_level(text, number):
    parts = []
    depth = 0
    in_single = False
    in_double = False
    current = []
    for char in text:
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        if not in_single and not in_double:
            if char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
            elif char == "," and depth == 0:
                parts.append("".join(current).strip())
                current = []
                continue
        current.append(char)
    if in_single or in_double or depth != 0:
        raise YamlError("unbalanced quoting or brackets", number)
    parts.append("".join(current).strip())
    return [part for part in parts if part != ""]


def _parse_double_quoted(text, number):
    if len(text) < 2 or not text.endswith('"'):
        raise YamlError("unterminated double-quoted string", number)
    body = text[1:-1]
    out = []
    index = 0
    escapes = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "0": "\0"}
    while index < len(body):
        char = body[index]
        if char == "\\":
            index += 1
            if index >= len(body):
                raise YamlError("dangling escape in double-quoted string", number)
            out.append(escapes.get(body[index], body[index]))
        else:
            out.append(char)
        index += 1
    return "".join(out)


def _parse_single_quoted(text, number):
    if len(text) < 2 or not text.endswith("'"):
        raise YamlError("unterminated single-quoted string", number)
    return text[1:-1].replace("''", "'")


def dumps(value, indent=0):
    """Minimal dump used only for debugging and test fixtures."""
    pad = " " * indent
    if isinstance(value, dict):
        if not value:
            return "{}"
        out = []
        for key in value:
            rendered = dumps(value[key], indent + 2)
            if isinstance(value[key], (dict, list)) and value[key]:
                out.append("%s%s:\n%s" % (pad, key, rendered))
            else:
                out.append("%s%s: %s" % (pad, key, json.dumps(value[key])))
        return "\n".join(out)
    if isinstance(value, list):
        if not value:
            return "[]"
        out = []
        for item in value:
            if isinstance(item, (dict, list)):
                out.append("%s-\n%s" % (pad, dumps(item, indent + 2)))
            else:
                out.append("%s- %s" % (pad, json.dumps(item)))
        return "\n".join(out)
    return "%s%s" % (pad, json.dumps(value))
