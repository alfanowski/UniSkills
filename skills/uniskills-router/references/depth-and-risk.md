# Depth and Risk

> Depth is a budget decision. This file defines when to spend and when to refuse to.

## 1. Risk matrix

Score the artifact on the highest row it touches, not on its size.

| Signal | Minimum depth | Why |
| --- | --- | --- |
| Read-only question about a local, reversible artifact | QUICK | Wrong answer costs a re-read |
| Code change with tests and a clean rollback | STANDARD | Wrong answer costs a revert |
| Authentication, authorization, session handling | DEEP | Wrong answer costs an account |
| Cryptography, key handling, signature verification | DEEP | Wrong answer costs confidentiality |
| Memory safety, unsafe blocks, FFI boundaries | DEEP | Wrong answer costs a process or a host |
| Concurrency, locking, async cancellation, shared mutable state | DEEP | Wrong answer is intermittent and expensive to find later |
| Money movement, billing, quotas, irreversible side effects | DEEP | Wrong answer costs money |
| Schema or data migration with a backfill | DEEP | Wrong answer costs data |
| Untrusted input parsing (parsers, deserializers, protocol handlers) | DEEP | Wrong answer costs the perimeter |
| Incident, suspected compromise, evidence that may be needed later | FORENSIC | Wrong answer destroys trust in the conclusion |
| Analysis of a binary or artifact of unknown provenance | FORENSIC | Wrong answer risks executing something hostile |
| Public claim, benchmark, or published number | DEEP | Wrong answer damages credibility |

## 2. Escalation rules

Escalate one level when **any** of these is true:

- The artifact is outside the agent's ability to execute or test (no runtime, no network, no debugger).
- Two credible explanations survive the first pass.
- The user's framing contains a causal claim that has not been tested ("this is slow because of the GC").
- The conclusion would be used to approve, deploy, publish, or delete something.

De-escalation requires a written reason. Acceptable: "QUICK — read-only, one call site, revert is
`git revert`, no external effect." Not acceptable: "QUICK — looks simple."

## 3. What each depth must produce

| Depth | Evidence | Adversarial check | Output |
| --- | --- | --- | --- |
| QUICK | One direct pointer | One sentence: what would falsify this | Direct answer |
| STANDARD | Pointer per finding | One alternative explanation tested | Structured report |
| DEEP | Pointer per claim, cross-check of the key claim | Failure matrix + alternative hypotheses | Report + residual risk |
| FORENSIC | Ledger with artifact hash, tool versions, commands | Independent second method or second reviewer | Report + coverage map + reproducibility package |

## 4. Cost guards

- If a verification costs more than the decision it informs, say so and skip it explicitly.
- If the artifact is too large to cover fully, sample deliberately (highest-risk paths first) and
  state the sampling rule and the uncovered region.
- If a tool is unavailable, do not silently reduce depth. Either use a weaker fallback and mark the
  confidence lower, or stop and report the blocker.
- "Maximum effort" means `DEEP` or `FORENSIC` with the obligations above — not more prose.
