# Routing Table

> Read after extracting the request frame. Match on **artifact + verb**, never on topic keywords alone
> ("security" appears in design, review, and research requests and means three different things).

## 1. Primary-output test

Ask what the user must be able to *do* after reading the answer. That single question resolves most
ties.

| The user must be able to... | Route |
| --- | --- |
| Decide whether to merge | `universal-code-review` |
| Trust a component in an adversarial environment | `security-review` |
| Know where time or memory actually goes | `performance-review` |
| Understand why a failure happens | `root-cause-debugging` |
| Commit to a structure and live with it | `architecture-design-review` |
| Choose between genuinely different approaches | `technical-brainstorming` |
| Rely on a fact, number, or prior-art claim | `technical-research` |
| Trust a measured or claimed effect size | `experiment-design-and-falsification` |
| Explain what an artifact does | `reverse-engineering` |
| Check that a claim in the current work is supported | `evidence-validation` |
| Stop wasting context or tool calls | `context-efficiency` |

## 2. Artifact → skill

| Artifact | Default skill | Escalate to |
| --- | --- | --- |
| Pull request, patch, commit, single function | `universal-code-review` | `security-review` if it parses untrusted input, handles auth, or deserializes data |
| Service, module boundary, data ownership, deployment topology | `architecture-design-review` | `security-review` for trust boundaries; `performance-review` for SLO feasibility |
| Stack trace, failing test, crash, flaky behavior | `root-cause-debugging` | `reverse-engineering` if the artifact is a stripped binary |
| Heap profile, latency histogram, benchmark result | `performance-review` | `experiment-design-and-falsification` if the benchmark method itself is contested |
| Spec, RFC, paper, changelog, vendor docs | `technical-research` | `evidence-validation` when sources conflict |
| Open-ended "what should we build / how could we do X" | `technical-brainstorming` | `architecture-design-review` once one option must be committed |
| Binary, firmware, proprietary format, protocol capture | `reverse-engineering` | `security-review` only inside an authorized defensive scope |
| Existing draft analysis with claims to check | `evidence-validation` | the originating skill if new analysis is needed |

## 3. Verb → skill

| Verb | Meaning in the request | Route |
| --- | --- | --- |
| review / check / audit this code | judge a change | `universal-code-review` |
| is this secure / can this be exploited | adversarial judgment | `security-review` |
| why is it slow / make it faster | cost analysis | `performance-review` |
| why does it fail / it crashes | causal reconstruction | `root-cause-debugging` |
| design / should we use X or Y / structure | commitment under constraints | `architecture-design-review` or `technical-brainstorming` |
| research / what is the state of the art / is it true that | source-backed answer | `technical-research` |
| prove / measure / does X actually help | falsifiable test | `experiment-design-and-falsification` |
| what does this binary do / recover this format | behavior reconstruction | `reverse-engineering` |
| are you sure / where did this number come from | claim audit | `evidence-validation` |
| this is too slow to work with / too many files | process cost | `context-efficiency` |

## 4. Tie-breaks

1. **Specificity beats breadth.** `security-review` beats `universal-code-review` if the user's stated
   concern is exploitable behavior; the reverse if they asked about correctness.
2. **Evidence beats opinion.** If the user supplies measurements or logs and asks for a judgment,
   route to the skill that consumes that evidence, not the one that would regenerate it.
3. **Commitment beats exploration.** If a decision must be made now with known options →
   `architecture-design-review`. If options are not yet distinct → `technical-brainstorming`.
4. **The cheaper sufficient skill wins.** If `QUICK` `universal-code-review` answers it, do not invoke
   a security audit because the topic mentions passwords.
5. **Never route to two skills that would restate each other.** Review + security is acceptable when
   the security skill goes deeper on a disjoint lens; review + "best practices" is not a chain.

## 5. Known non-matches

Do not force a UniSkills skill onto:

- pure operations ("deploy this", "restart the service") — that is an action request, not an analysis;
- tool configuration questions answerable from one doc page;
- legal, licensing, or compliance determinations — provide evidence, not a ruling;
- requests whose real goal is emotional support or career advice.

For these, answer directly or say the request is out of scope.

## 6. Chaining rules

A chain is valid only if every arrow carries a **named artifact**:

```text
root-cause-debugging  --(reproduction + causal chain)-->  universal-code-review
universal-code-review --(findings list)---------------->  technical-brainstorming
technical-research    --(source ledger)---------------->  experiment-design-and-falsification
reverse-engineering   --(behavior map + unknowns)------>  security-review
```

Invalid chains: two review skills on the same artifact (duplicate findings), or a research step whose
output is never consumed. Maximum length is three; beyond that, the routing is hiding a bad plan.
