# Research and Competitor Survey

**Survey date:** 2026-10-22
**Method:** primary documentation fetched directly; repository metadata and file trees read through the
GitHub API; no project installed, cloned, or executed. Licenses taken from repository metadata
(`license.spdx_id`) and, where relevant, from a license file inside the tree.
**Limits:** this is a targeted survey for design decisions, not a market study. Star counts are a
snapshot and are not a quality signal. Nothing here is legal advice.

## 1. Format and authoring sources

### 1.1 Agent Skills specification

- **URL:** <https://agentskills.io/specification>
- **Accessed:** 2026-10-22
- **License of the page:** not stated on the page. The specification repository
  (`agentskills/agentskills`) is Apache-2.0.
- **Verified directly:** required fields and constraints (`name` 1–64 chars, lowercase alphanumeric plus
  hyphens, no leading/trailing/double hyphen, must match directory; `description` 1–1024 chars,
  non-empty); optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`); recommended
  directories (`scripts/`, `references/`, `assets/`); progressive disclosure model (metadata → body →
  resources); "keep `SKILL.md` under 500 lines"; references one level deep; validation via `skills-ref`.
- **Used for:** the frontmatter contract, directory layout, and the line budget enforced by our validator.

### 1.2 Anthropic skill authoring best practices

- **URL:** <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- **Accessed:** 2026-10-22
- **License:** vendor documentation; not open content. Read for design, not copied.
- **Verified directly:** concise-is-key guidance; "set degrees of freedom" (low freedom for fragile
  operations); gerund naming as a convention, not a requirement; descriptions must be third person and
  include both what and when; avoid deeply nested references because clients may partially read them;
  table of contents for references longer than ~100 lines; evaluation-first development; at least three
  evaluations; anti-patterns (Windows paths, too many options, time-sensitive content).
- **Used for:** the section contract, the one-level reference rule, the third-person description rule, and
  the "eval case before prose" stance.

### 1.3 OpenAI Skills documentation

- **URL:** <https://developers.openai.com/api/docs/guides/tools-skills>
- **Accessed:** 2026-10-22
- **License:** vendor documentation.
- **Verified directly:** skills are directories with a `SKILL.md` manifest; explicit statement that skills
  are compatible with the open Agent Skills standard; hosted vs local shell attachment; Agents API
  capability directories; limits (50 MB zip, 500 files, 25 MB per file); security guidance that skill
  content is privileged and should be inspected, and that arbitrary user-selectable skill catalogs are a
  prompt-injection risk.
- **Used for:** the "no vendor lock-in" design, the safety framing, and confirmation that a directory-based
  bundle is the right packaging unit.

### 1.4 Anthropic public skills repository

- **URL:** <https://github.com/anthropics/skills>
- **Accessed:** 2026-10-22 · **Stars:** ~182.9k · **Repo-level license:** none declared.
- **Licensing detail verified:** individual skills carry `LICENSE.txt` files; the sampled file
  (`skills/academy-guide/LICENSE.txt`) is Apache-2.0. The README states that the document skills
  (`docx`, `pdf`, `pptx`, `xlsx`) are source-available, not open source.
- **Structure observed:** `skills/<name>/SKILL.md`, per-skill license files, `spec/`, `template/`, a
  `.claude-plugin/marketplace.json`, and `THIRD_PARTY_NOTICES.md`.
- **Useful ideas:** a template directory ships alongside the skills; per-skill license text is more precise
  than a repo-wide claim; third-party notices are tracked explicitly.
- **Not adopted:** plugin marketplace packaging (out of scope for 0.1.0) and per-skill license files
  (all first-party skills are MIT, so a single root license is accurate).
- **Limit:** no evaluation harness was observed at repository level; skills are demonstrated, not scored.

### 1.5 Agent Skills specification repository

- **URL:** <https://github.com/agentskills/agentskills>
- **Accessed:** 2026-10-22 · **License:** Apache-2.0 · **Stars:** ~26.4k
- **Verified:** repository contains the docs site, the specification, and `skills-ref` (a Python package
  with `pyproject.toml`, `uv.lock`, and tests) used for validation.
- **Used for:** awareness that an official validator exists. We did not depend on it because it requires a
  Python toolchain and `uv`, and because our validator enforces additional repository-specific rules
  (catalog sync, contract drift, eval schema). Compatibility with `skills-ref` remains unverified and is
  listed as future work.

## 2. Specialized reverse-engineering skills

### 2.1 Reverse Engineer Anything

- **URL:** <https://github.com/erisvulgaris/Reverse-engineer-anything>
- **Accessed:** 2026-10-22 · **License:** MIT · **Stars:** 0 · **Last push:** 2026-10-05
- **Verified from the tree:** a Node/TypeScript-style project with `.github/workflows/` (including
  `real-browser.yml`, `real-ghidra-windows.yml`, `real-hopper-linux.yml`), `.husky` hooks, multiple
  linters/formatters, `release-please` configuration, `AGENTS.md`, `CONTRIBUTING.md`, `CHANGELOG.md`,
  and issue templates. The workflows named after specific RE tools suggest environment-specific
  integration tests.
- **Useful ideas:** testing against real tools in CI, not mocks; release automation; explicit
  agent-facing repository instructions; a pre-commit/pre-push quality gate.
- **Limits:** small project, no license ambiguity but little independent validation; the CI matrix is
  heavy and not portable to a documentation-only repository.
- **Not copied:** no content, scripts, or workflow files.

### 2.2 REx@Skill

- **URL:** <https://github.com/tihanyin/REx-skill>
- **Accessed:** 2026-10-22 · **License:** MIT · **Stars:** ~114 · **Last push:** 2026-09-23
- **Verified from the tree:** `claude-skill/skills/reverse-engineering/SKILL.md` plus twelve numbered
  references (`01-triage.md` … `12-bounds.md`), a set of `agents/re-*.md` role files, and a command file.
- **Observed size:** `SKILL.md` is ~21 KB. For comparison, our largest `SKILL.md` is ~8 KB and the target
  is < 500 lines.
- **Useful ideas:** numbered reference files make the load order legible; splitting triage, dynamic
  analysis, formats, tooling, and advanced topics into separate documents is a sound disclosure pattern.
- **Critique:** a 21 KB main file undercuts progressive disclosure — the whole thing loads on activation,
  before the reader knows which part is relevant. Our design keeps the body procedural and moves
  ISA/ABI detail to a single on-demand reference.
- **Not copied:** no text, structure names, or checklists.

## 3. Comparable collections and the gap

| Project | Form | Strengths | Gap for our purpose |
| --- | --- | --- | --- |
| `anthropics/skills` | Demonstration skills by the format's authors | Authoritative examples, wide domain coverage | Demonstration-oriented; not a method suite; no repo-level evaluation |
| `agentskills/agentskills` | Specification + validator | Normative, precise | Defines the format, not the method |
| `REx-skill` | Single deep RE skill | Deep domain content | Monolithic body; one domain; no evaluation cases |
| `Reverse-engineer-anything` | Tooling + skills for RE | Real-tool CI, release engineering | Narrow domain, heavy stack |
| Prompt collections (general) | Markdown prompt lists | Easy to copy | No exits, no evidence model, no tests, no versioning |

**Differentiation UniSkills claims, and can demonstrate in this repository:**

1. A single documented method applied across domains, with per-domain translations rather than repeated
   generic advice.
2. Evidence labels and pointers as a hard requirement, validated in structure and tested in cases.
3. Depth as an explicit, risk-driven budget with four profiles.
4. Context and tool economy expressed as concrete rules, not slogans.
5. A catalog that separates shipped from planned, generated from a machine-readable source.
6. Deterministic validation of structure, links, secrets, and catalog consistency.

**What UniSkills does not claim:** superior output quality. That requires controlled runs that have not
been performed. See [evaluation-methodology.md](evaluation-methodology.md).

## 4. Name collision check

Method: `gh search repos uniskills` and `gh search users uniskills` on 2026-10-22, plus inspection of the
top results' descriptions.

Observed:

- `KimHanjung/UniSkill` — a CoRL 2025 robotics paper implementation; unrelated domain.
- Several `UniSkill`/`UniSkills` repositories for skill-exchange platforms, hackathon projects, and
  student coursework (for example `riya503/Uniskills`, `harveyjones01/uniSkills`).
- `mehdimkt/UniSkills-VF`, `arifsl65/uniskills`, `samjoy247-max/UniSkills` — small or empty repositories.
- `alfanowski/UniSkills` — this project.

Assessment: the string is used by unrelated projects, and no AI-agent skill suite with this name was
found. There is no trademark claim and no assertion of exclusive availability. The practical risk is
search ambiguity, which the README's first line mitigates by stating the full name and purpose. A future
rename would require updating the catalog and every `../skills/` link; the tooling would catch the breakage.

## 5. Sources deliberately not used

- No vendor blog benchmark was treated as evidence for any design claim.
- No third-party skill text was copied, so no attribution obligation was created beyond citation.
- Client applications were not installed, so no compatibility claim in
  [compatibility.md](compatibility.md) is based on a run.

## 6. References

All URLs above were accessed on 2026-10-22. Repository metadata (stars, license, last push) was read from
the GitHub REST API on the same date and is a snapshot.
