# Context Efficiency: Repository-Level Policy

> The skill `context-efficiency` carries the procedure. This document explains what UniSkills does at the
> repository level, what it can measure, and what it refuses to claim.

## 1. Why this is a first-class concern

An agent's context is a shared budget: system prompt, conversation, tool output, and skill bodies
compete for the same window. A skill that teaches a good method but drags 8,000 tokens into every
session makes the agent worse at the actual task.

The Agent Skills format already provides the main mechanism — metadata is loaded up front, the body on
activation, references on demand. UniSkills's contribution is to use that mechanism consistently and to
enforce it structurally.

## 2. What is enforced by the repository

| Rule | Enforcement |
| --- | --- |
| `SKILL.md` ≤ 500 lines (warn), ≤ 700 (fail) | `tools/validate_skills.py` |
| Description ≤ 1024 characters, states what and when | validator |
| References one level deep, all linked from `SKILL.md` | validator, including a warning for reference→reference links |
| Every reference must be reachable and used by a workflow step | manual review + link check |
| No encyclopedia content in `SKILL.md` | review; the section contract keeps the body procedural |
| No duplication of shared doctrine | canonical contract is the only duplicated block, and it is drift-checked |
| Deterministic work in scripts, not prose | review; `tools/` is the proof for this repo |

## 3. What a skill must do at runtime

1. **Locate before reading.** Directory listings, `git diff --stat`, `rg -l`, symbol search, table of
   contents. Reading a file is a decision, not a reflex.
2. **Expand in rings.** Ring 0 = the exact lines defining behavior; ring 1 = callers, callees, contracts;
   ring 2 = tests and docs that constrain it. Stop when the next ring cannot change the answer.
3. **Shape tool output.** `--stat` before full diffs, `-C2` before whole files, `jq` projections before
   raw JSON, explicit `head`/`tail` counts, `sort | uniq -c` before raw event lists.
4. **Reuse only with a cache key.** Artifact identity + operation + parameters + tool version. Otherwise
   re-derive. Mark reused evidence as `REUSED`.
5. **Checkpoint.** ≤ 20 lines: goal, verified facts with pointers, refuted hypotheses, open questions,
   next action.
6. **Stop on marginal value.** Two consecutive calls returning no decision-relevant information means
   stop.

## 4. The anti-optimization clause

A reduction in context that loses a critical bug is not an optimization. The policy therefore includes
explicit exceptions:

- Short security-relevant code (crypto, auth, parsing) is read fully, always.
- Legal text, configuration precedence, and schema definitions are read in full when the question
  depends on exact wording.
- A profile or log slice must be accompanied by the filter, the window, and the total count, so the
  reader can judge representativeness.

Efficiency is measured in **decision-relevant information per unit of context**, not in tokens saved.

## 5. Measurement: what is possible and what is not

| Metric | Availability | Status |
| --- | --- | --- |
| Skill body size in lines/characters | Always | Measured by the validator |
| Description length | Always | Measured by the validator |
| Number of tool calls in a session | Runtime-dependent | Not measured by this repo |
| Bytes of tool output read | Runtime-dependent | Not measured |
| Input/output tokens | Runtime-dependent, often not exposed | Explicitly not claimed |
| Duplicate reads | Detectable in a transcript | Manual review only |
| Task success | Requires an eval harness and a model | Not run in this release |

UniSkills does **not** publish a "token savings" percentage. Any such number would either be a proxy
presented as a measurement, or would depend on a specific client's tokenizer and context accounting.

## 6. How to run a fair comparison later

If you want to test whether a skill helps, the protocol is:

1. Same model and version, same tool set, same task, same starting repository state.
2. Two arms: with the skill installed and without it. Same depth profile.
3. N ≥ 5 runs per arm, because LLM output varies.
4. Score against the eval rubric, not against length or confidence.
5. Record tool calls, wall time, and any client-exposed token counts, labeling proxies as proxies.
6. Report the distribution, not the mean alone.

A single run, or a comparison across different models, is not evidence of anything.

## 7. Practical guidance for contributors

- If you are writing a `SKILL.md` and it is approaching 500 lines, you are probably writing a reference.
- If a reference is shorter than ~40 lines and is always relevant, inline it.
- If two skills need the same checklist, the checklist is wrong: it is either general doctrine (docs) or
  it belongs to one skill and the other should reference the skill.
- If a workflow step says "read the repository", it is not a step. Replace it with a locator.

## 8. Why no subagent mandate

Parallel subagents multiply context, not reduce it: each one re-reads its own slice and returns a
summary that may lose the evidence. UniSkills allows parallelism only when workstreams are independent,
each has a verifiable output, and the merge cost is lower than the time saved. This is stated in
`context-efficiency` and in every skill that might chain work.
