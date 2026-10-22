# The UniSkills Universal Method

> Canonical reference for how every UniSkills skill reasons. Skills embed a compressed version of
> this method in their `SKILL.md`; this document is the full specification, the rationale, and the
> place where domain-specific translations are defined.

## 1. Method over persona

A skill is not a costume. Telling an agent to "act as a world-class principal engineer" changes tone,
not outcomes. What changes outcomes is a procedure: what to look at, in which order, what counts as
proof, when to stop, and what the deliverable must contain.

UniSkills therefore standardizes five things and leaves the rest to the skill author:

1. **Framing** — how the request is turned into a scoped, testable objective.
2. **Resolution** — how far down the causal stack the analysis must go for this task.
3. **Evidence** — what may be asserted, with which label, backed by what.
4. **Adversarial check** — the deliberate attempt to falsify the conclusion before shipping it.
5. **Closure** — output contract, stop conditions, and declared limits.

A skill that cannot be evaluated against these five is a prompt, not a skill.

## 2. The low-level attention principle

The phrase "reason like you are analyzing assembly" is used inside this project as a **methodological
analogy for resolution**, not as a product requirement.

It means: do not stop at a description of what a system appears to do. Reconstruct, to the depth the
task actually needs, **how it does it**.

| Surface description (insufficient) | Reconstructed description (the standard) |
| --- | --- |
| "The function validates the token." | Which branch accepts, on which field, compared against what, with which clock, and what happens on each failure edge. |
| "The cache makes it fast." | Key composition, invalidation trigger, eviction policy, concurrency discipline, miss path cost, and the condition under which it becomes slower than no cache. |
| "The service is stateless." | Where the session actually lives, which request fields carry implicit state, and what breaks on retry or reordering. |
| "The paper shows a 12% improvement." | Dataset, baseline, metric definition, variance, ablation, and whether the comparison is apples-to-apples. |
| "The migration adds a column." | Lock mode, rewrite cost, backfill ordering, deploy/rollback compatibility window, and readers that break on the intermediate state. |

Low-resolution analysis is not wrong because it is short. It is wrong when it **asserts** a mechanism
it never reconstructed. A one-line answer to a one-line question is correct behavior; a confident
mechanism claim without tracing is not.

### 2.1 The eight reconstruction questions

Apply the subset that the task and the risk justify. Skipping a question is allowed; silently
skipping it is not — say which ones you skipped and why.

1. **Scope** — what exactly is in and out, and what would success look like?
2. **Components** — which parts exist, who acts on them, and where are the seams?
3. **State** — which states exist, how is each entered and left, and what is observable in each?
4. **Transfer** — how do data and control move, transform, and get dropped along the way?
5. **Contracts** — which preconditions, postconditions, invariants, and assumptions must hold?
6. **Resources** — what is consumed (time, memory, handles, quotas, money), by whom, and when released?
7. **Trust** — where is the boundary between trusted and untrusted, and who can cross it?
8. **Failure** — how does it break, what is the blast radius, and what would prove the failure exists?

## 3. Domain translations

The vocabulary is fixed; the mapping is not. Use the column that fits the domain.

| Question | Code | Security | Performance | Architecture | Research |
| --- | --- | --- | --- | --- | --- |
| State | variables, objects, DB rows | sessions, credentials, privilege level | cache lines, pools, queues, GC generations | service state, config, data ownership | dataset version, model weights, corpus |
| Transfer | arguments, returns, exceptions | source → transform → sink | bytes moved, syscalls, allocations | requests, events, replication | measurement → statistic → claim |
| Contract | types, pre/postconditions | authn/authz invariants | latency/throughput SLOs | interface + quality attributes | hypothesis, operational definitions |
| Resources | CPU, heap, fds, locks | capabilities, tokens, rate limits | watts, bandwidth, IOPS, tail latency | cost, headcount, operational load | compute budget, sample size |
| Trust | user input, third-party libs | attacker-controlled input | shared hardware, noisy neighbors | organizational + network boundaries | source authority, peer review |
| Failure | exceptions, panics, races | exploit chain, privilege escalation | saturation, thrash, queue collapse | cascading failure, lock-in | confounder, retraction, bias |

## 4. Depth profiles

Depth is a **budget allocation decision**, not a personality. Select it from risk, not from the size
of the diff.

| Profile | Use when | Concrete obligations |
| --- | --- | --- |
| `QUICK` | Small, reversible, low blast radius; an obvious answer already exists | Scope statement + direct answer + the one check that could invalidate it. No ledger required. |
| `STANDARD` | Ordinary engineering work with real consequences | Full workflow, evidence with file/line or source references, one adversarial counter-check, explicit limits. |
| `DEEP` | High uncertainty, cross-module effects, security or data-loss exposure, contested claims | Everything in `STANDARD` plus alternative hypotheses, edge/failure matrix, cross-verification of key claims, and a written falsification attempt. |
| `FORENSIC` | Incidents, critical audits, irreversible actions, adversarial or untrusted artifacts | Everything in `DEEP` plus artifact identity/hashes, timestamped evidence ledger, tool+version pinning, reproducible commands, chain-of-custody notes, coverage gap map. |

Rules:

- **Escalation is mandatory** when the change touches authentication, authorization, cryptography,
  money movement, memory safety, concurrency primitives, destructive migrations, or untrusted input
  parsing — even if the diff is four lines.
- **De-escalation is allowed** only with a one-line reason, e.g. "QUICK: read-only, single call site,
  revert is `git revert`."
- `QUICK` never skips safety gates or the falsification check; it only skips ceremony.
- "Maximum effort" is not a profile. If the user asks for it, use `DEEP` or `FORENSIC` as the risk
  warrants and say what you actually did.

## 5. Evidence discipline

Full rules live in [evidence-and-claims.md](evidence-and-claims.md). The method depends on three
habits:

1. **Label every non-obvious claim** as `VERIFIED`, `DERIVED`, `LIKELY`, `HYPOTHESIS`, `SPECULATIVE`,
   `UNKNOWN`, or `N/A`.
2. **Cite the smallest sufficient pointer** — `path:line`, commit, symbol, offset, URL + date, test id.
3. **Separate observation from interpretation** in the artifact itself, not just in your head.

An analysis that says "probably a race" without a label and without the trace that suggests it is
worse than one that says `HYPOTHESIS` and names the interleaving it would need.

## 6. Adversarial check (mandatory above `QUICK`)

Before presenting a conclusion, run this loop once:

1. State the conclusion in one falsifiable sentence.
2. Ask: *what observation would make this false?*
3. Go look for that observation, cheaply. If it is expensive, say why you skipped it.
4. Check the two most common failure modes of your own reasoning:
   - **Confirmation** — did I only read evidence that supports the first hypothesis?
   - **Substitution** — did I answer an easier adjacent question instead of the asked one?
5. If a plausible alternative survives, present it as such instead of collapsing to one answer.

The output does not need to describe this loop. It must reflect it.

## 7. Uncertainty handling

- **Missing evidence is a finding**, not a failure. Record it under `Limits` / `Unknowns`.
- **Absence of evidence is not evidence of absence.** "No vulnerability found" never means "secure".
- **Never fabricate**: no invented line numbers, test results, benchmarks, citations, tool output,
  API options, or compatibility claims.
- **Distinguish "could not run" from "ran and passed".**
- When a decision is blocked by missing information, state the minimum unblocking question and,
  where safe, proceed on a declared assumption instead of stalling.

## 8. Output proportionality

| Request shape | Correct output |
| --- | --- |
| "Does this loop have an off-by-one?" | Two sentences + the boundary condition. |
| "Review this PR" | Findings ordered by severity, each with evidence and impact. |
| "Design the migration" | Options, trade-offs, chosen path, rollback, acceptance criteria. |
| "Is this library safe to adopt?" | Criteria, evidence per criterion, residual risk, recommendation with conditions. |

Proportionality is not laziness. It is refusing to spend the user's attention on structure they did
not ask for. The rule is: **every section in the output must earn its header.**

## 9. Stop conditions

Stop when all of the following hold:

- The stated deliverable is complete against its own contract.
- Each significant claim has an evidence label and a pointer, or is explicitly marked unknown.
- Further investigation is unlikely to change the recommendation, or its cost exceeds its decision
  value — and that judgment is written down.
- Residual risks and open questions are listed.

Additional stop conditions that override completeness:

- The next action would cross an authorization boundary.
- The next action would be destructive, irreversible, or externally visible.
- Evidence is being re-collected without changing the conclusion (loop detected).

## 10. Anti-ritual clause

The method must not become bureaucracy. All of the following are violations:

- Reading every file in a repository to "get context" before knowing the question.
- Producing a `FORENSIC` ledger for a typo fix.
- Restating the user's request as a "requirements analysis" section.
- Adding a table because tables look rigorous.
- Listing twelve "risks" of which ten are generic.
- Emitting a confidence percentage with no defined meaning.
- Declaring an analysis exhaustive.

If a step produced no decision-relevant information, drop it from the output and say so if asked.

## 11. Composition

Skills compose by **reference, not by duplication**:

- A review skill calls `evidence-validation` for claim grading rather than restating the taxonomy.
- A research skill calls `technical-research` for source work and `experiment-design-and-falsification`
  for the experiment.
- Packs are ordered playbooks over existing skills; they never fork skill content.

See [architecture.md](architecture.md) for the layering rules and
[skill-authoring-standard.md](skill-authoring-standard.md) for how this method is embedded in a
`SKILL.md` without turning every skill into a copy of this document.
