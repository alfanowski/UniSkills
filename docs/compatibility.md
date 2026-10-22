# Compatibility

> Claim only what was checked. Everything else is labeled as expected or unverified.

## 1. Format target

UniSkills targets the **Agent Skills** format: a directory containing `SKILL.md` with YAML frontmatter
(`name`, `description` required) plus optional `references/`, `scripts/`, and `assets/`.

Specification: <https://agentskills.io/specification> (accessed 2026-10-22).

Constraints taken from the specification and enforced by `tools/validate_skills.py`:

| Constraint | Limit | Enforced |
| --- | --- | --- |
| `name` length | 1–64 chars | yes |
| `name` alphabet | `a-z`, `0-9`, `-`; no leading/trailing/double hyphen | yes |
| `name` matches directory | required | yes |
| Reserved words in `name` | `anthropic`, `claude` | yes |
| `description` length | 1–1024 chars | yes |
| `description` XML tags | none | yes |
| `license` / `compatibility` / `metadata` / `allowed-tools` | optional | parsed and type-checked |
| Body length | ≤ 500 lines recommended | warned, hard fail at 700 |

## 2. Our additions (non-breaking)

UniSkills requires `metadata.version`, `metadata.status`, `metadata.updated`, and `metadata.family`.
These are inside the spec's `metadata` map, so a conforming client ignores them rather than failing.
They are required **by our validator**, not by the format.

No custom top-level frontmatter fields are used, because unknown top-level fields are not guaranteed to be
accepted by every client.

## 3. Verified here, in this repository

| Check | Method | Result |
| --- | --- | --- |
| Frontmatter parses as YAML | `yamlmini`, cross-checked against PyYAML 6.0.3 | pass (2026-10-22) |
| Spec field constraints | `tools/validate_skills.py` | pass for all 12 skills |
| Local links resolve | `tools/check_links.py` | pass |
| Skills are standalone (no links outside their directory) | validator, link-escape check | pass |
| Eval schema valid | `tools/eval_runner.py --check` | pass, 36 cases |

## 4. Expected but not verified

These are reasonable expectations from the format, not test results. Treat them as claims to verify in
your environment.

| Environment | Basis for expectation | Status |
| --- | --- | --- |
| Claude Code (project or user skills directory) | Anthropic documents skills as directories with `SKILL.md` | **not tested here** |
| Claude API (skills upload) | Anthropic documents uploading skill folders | **not tested here** |
| OpenAI Responses API (shell tool, hosted or local skills) | OpenAI documents compatibility with the Agent Skills standard | **not tested here** |
| OpenAI Agents API capability directories | OpenAI documents discovery of `SKILL.md` in capability directories | **not tested here** |
| Other clients implementing the standard | Community implementations follow the spec to varying degrees | **unknown** |

No client was installed or called during this work. The repository therefore does **not** claim
"works everywhere", and does not list a version matrix it never ran.

## 5. What "portable" means here

Portable means:

- the artifact is a directory with a text manifest, not an API payload;
- no vendor SDK, endpoint, or credential is referenced by a skill;
- every tool mention includes a fallback when the tool is absent;
- no absolute paths, no user-specific configuration;
- the method is expressed in domain terms, not in the vocabulary of one model.

Portable does **not** mean identical behavior across models. Instruction-following differs; a skill that
works well on one model may need tightening on another. That is why the evaluation methodology asks for
per-model runs rather than a single score.

## 6. Known deviations and edge cases

1. **`allowed-tools`** is parsed but unused. It is marked experimental in the specification, and support
   varies by client. UniSkills does not rely on it for safety.
2. **`license: MIT`** is a short identifier, as the spec recommends. The full text is at the repository
   root.
3. **References depth.** The specification recommends one level of nesting; UniSkills enforces it. If a
   client only partially reads references, a single level limits the damage.
4. **Description length.** Some clients truncate long descriptions. Ours are written so the first
   sentence already states the capability.
5. **Token counts.** The specification's "~100 tokens" metadata estimate and "<5000 tokens" body
   estimate were used as design targets. They were not measured per skill, because tokenization depends
   on the client.

## 7. Installing one skill

```bash
cp -R skills/universal-code-review ~/.claude/skills/          # example destination
```

The destination depends on your client. Verify by asking for a task the skill should trigger and
confirming the skill is listed. If the client requires a different catalog format, wrap the directory —
do not edit `SKILL.md` fields, or you lose validator coverage.

## 8. Maintenance rule

When the upstream specification changes, the order of work is:

1. update `tools/validate_skills.py` constraints;
2. update this document with the date and the change;
3. re-run the validators and record the result in `CHANGELOG.md`.

Do not update the frontmatter first: the validator is the contract.
