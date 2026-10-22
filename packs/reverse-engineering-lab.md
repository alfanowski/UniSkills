# Reverse Engineering Lab

**Pack id:** `reverse-engineering-lab` · **Skills:** 3 · **Typical effort:** one day to several weeks

## Purpose

Characterize an authorized artifact, reconstruct what it does, then check whether the reconstruction
implies exposure that the owner needs to fix. The pack is defensive by construction: it produces
knowledge and remediation, not exploitation.

## Audience

Defenders, interoperability engineers, and researchers working on artifacts they own or are explicitly
authorized to analyze.

## Members and roles

| Order | Skill | Role in the pack | Produces |
| --- | --- | --- | --- |
| 1 | `reverse-engineering` | Identify, triage, and reconstruct structure and behavior | Behavior map + evidence ledger |
| 2 | `evidence-validation` | Separate observation from inference in the reconstruction | Graded claims |
| 3 | `security-review` | Turn the behavior map into trust boundaries and reachable weaknesses | Security findings |

## Recommended order and why

Reconstruction first: you cannot assess exposure in a system you cannot describe. Validation second:
decompiler output and dynamic traces are hypothesis generators, and the ledger is what keeps the report
honest. Security last: it consumes the behavior map rather than re-deriving it.

## Cost and permissions

- Written authorization is mandatory before step 1 for anything not owned by the user.
- Dynamic analysis requires an isolated environment; a container is not automatically a sandbox.
- No exploitation, persistence, or evasion work, even in an authorized scope, unless separately
  contracted and lawful.

## When a single skill is enough

- "What format is this file?" → `reverse-engineering` with `QUICK` (triage only).
- "Does this reconstructed parser have a memory-safety issue?" → `security-review` on the reconstruction.
- "Is this write-up credible?" → `evidence-validation`.

## Limitations

- The pack does not recover original source and must not claim to.
- Packing, virtualization-based obfuscation, and anti-analysis can stop progress; the report says so
  instead of guessing.
- Dynamic conclusions are only as good as the environment fidelity.

## Validation

Structural checks only. Each skill ships three evaluation cases covering a standard path, a boundary
case, and a safety refusal. End-to-end pack runs are manual and not claimed as automated.
