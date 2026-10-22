# Security Policy

## What is in scope

UniSkills is a collection of instructions plus deterministic tooling. Security issues include:

| Category | Examples |
| --- | --- |
| Instruction injection | A skill that would follow instructions embedded in analyzed content |
| Privilege escalation | A skill or script that installs, writes outside its directory, or touches global config |
| Unsafe defaults | Guidance that leads an agent to execute unknown binaries or exfiltrate data |
| Data exposure | Secrets or personal data committed to the repository, or logged by tooling |
| Supply chain | A dependency, template, or copied asset with unclear provenance |
| Tooling flaws | Path traversal in a validator, unsafe YAML parsing, command injection in a script |
| Over-triggering | A description crafted to activate on unrelated requests |

Vulnerabilities in **third-party projects that UniSkills discusses** are out of scope here. Report those
to their maintainers.

## How to report

Use GitHub's private vulnerability reporting on this repository:

1. Go to the **Security** tab.
2. Choose **Report a vulnerability**.
3. Include: affected file and line, the mechanism, the impact, and a minimal reproduction if one exists.

If private reporting is unavailable, contact the maintainer through the profile linked on the repository
and ask for a private channel. **Do not open a public issue for a vulnerability.**

## What to include

- The affected skill, script, or document, with a path.
- The precondition and the reachable path (for instruction issues, the exact text that would be
  misinterpreted or obeyed).
- The impact: what an agent would do that it should not.
- The smallest fix you can see.
- Whether you want attribution.

Do not include real credentials, personal data, or live malware. A synthetic sample is enough.

## What to expect

- Acknowledgment within 7 days.
- An assessment (accepted / needs more information / out of scope) within 14 days.
- A coordinated disclosure timeline agreed with you before any public write-up.
- Credit in the changelog if you want it.

This is a volunteer project; these are targets, not contractual guarantees.

## Safe harbor

We will not pursue action against researchers who:

- test against their own installation or a fork they control;
- avoid privacy violations, data destruction, and service disruption;
- report privately and give reasonable time to fix before disclosure.

## Hardening already in place

- No runtime dependencies and no network access in tooling.
- `tools/check_secrets.py` runs in CI on every change.
- Skills are read-only by default and state authorization gates explicitly.
- Skills ship no executable scripts in this release.
- The operating contract requires treating analyzed content as data, and injection resistance is covered
  by evaluation cases (`ctx-002`, `sec-003`, `re-002`).

## Known limitations

Instruction-level defenses are not a sandbox. A model can still be persuaded by adversarial content in
ways a document cannot prevent. The mitigations reduce probability and make the failure observable; they
do not make it impossible. Treat any skill as potentially untrusted until you have read it.
