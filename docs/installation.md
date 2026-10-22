# Installation

UniSkills skills are directories. Installation is a copy, and uninstallation is a delete. There is no
installer in 0.1.0 — deliberately, see [decision-log.md](decision-log.md#d7--no-installer-in-010).

## 1. Prerequisites

- Git, to obtain the repository.
- A client that supports the Agent Skills format (a directory with `SKILL.md`).
- Nothing else. No package manager, no runtime, no account.

## 2. Get the repository

```bash
git clone https://github.com/alfanowski/UniSkills.git
cd UniSkills
```

## 3. Install a single skill

Copy the skill directory into the location your client scans for skills. Replace the destination with the
path your client documents.

```bash
# example destinations — confirm yours in your client's documentation
cp -R skills/universal-code-review ~/.claude/skills/
cp -R skills/universal-code-review ./.claude/skills/        # project-scoped
```

Rules that keep the skill working:

- Copy the **whole directory**, including `references/`. The skill is self-contained by design; splitting
  it breaks its internal links.
- Do not copy `docs/`, `catalog/`, or `tools/` into a skill. They are repository-level, not skill-level.
- Do not edit frontmatter fields to fit a different catalog format. Wrap or convert instead, and run
  `python3 tools/validate_skills.py` afterwards if you keep a checkout.

## 4. Install a pack

A pack is a recommended set plus an order, not a single artifact. Install the skills you want to use
together, and read the pack document first:

```bash
cp -R skills/root-cause-debugging skills/universal-code-review \
      skills/experiment-design-and-falsification ~/.claude/skills/
cat packs/debugging-and-regression.md
```

## 5. Verify the installation

1. Ask a task the skill is designed for, using the trigger phrasing from its description. For example:
   *"Review this diff and tell me whether it is safe to merge."*
2. Confirm the client lists the skill (most clients expose a skill listing or a `/skills` command).
3. If nothing happens, the description did not match the request. Re-read the `description` field and use
   its vocabulary, or invoke the skill by name explicitly.

## 6. Uninstall

```bash
rm -rf ~/.claude/skills/universal-code-review
```

No state is written outside the skill directory. Nothing registers globally. No background process exists.

## 7. Running the repository checks locally

```bash
python3 tools/validate_skills.py     # frontmatter, sections, contract, links, evals
python3 tools/validate_catalog.py    # catalog <-> filesystem consistency
python3 tools/check_links.py         # relative markdown links
python3 tools/check_secrets.py       # secret and personal-path scan
python3 tools/render_catalog.py --check
python3 -m unittest discover -s tools/tests -t .
```

All of them are read-only and require only Python 3.8+.

## 8. Using a skill without a client that supports skills

Paste the `SKILL.md` body into the system prompt or the first user message. Keep the frontmatter out —
it is metadata for clients, not instructions. If the task needs the depth, also paste the specific
reference the workflow step points to.

This works, but it loses the two properties that make skills useful: on-demand loading and versioning. If
you find yourself pasting the same file repeatedly, that is the signal to set up a proper skills
directory.

## 9. Updating

```bash
git pull
cp -R skills/<name> ~/.claude/skills/     # overwrite the old copy
```

Check `CHANGELOG.md` before overwriting: workflow changes alter output shape, and your notes or prompts
may depend on the previous one.

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Skill never activates | Description does not match your phrasing | Use the trigger words from the description, or invoke by name |
| Skill activates for unrelated tasks | Your client matches loosely on the description | Report it; descriptions are tuned to avoid this and each skill lists exclusions |
| Broken reference after copying | Only `SKILL.md` was copied | Copy the whole directory |
| Validator fails on your edited copy | Frontmatter or section contract changed | Read the error; it names the file, line, and rule |
| Skill produces a huge report for a small question | Depth not set | Say `QUICK`, or state the expected deliverable explicitly |
