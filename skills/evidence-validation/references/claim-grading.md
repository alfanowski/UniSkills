# Claim Grading

> How to apply the seven labels consistently, and how they are usually misapplied.

## 1. Definitions in operational terms

| Label | Test | Counter-test (if true, downgrade) |
| --- | --- | --- |
| `VERIFIED` | I can point to the observation and reproduce it | I only saw a summary of it |
| `DERIVED` | Premises are labeled and the inference step is written | Any premise is `LIKELY` or weaker and the conclusion depends on it |
| `LIKELY` | Multiple independent supports agree; one gap named | The supports share a single origin |
| `HYPOTHESIS` | A test exists that could confirm or refute it | No test is possible with available means |
| `SPECULATIVE` | It is an idea, clearly framed as one | It is being used to justify an action |
| `UNKNOWN` | Access, tool, or data is missing | I simply did not look |
| `N/A` | The question does not apply | It applies but is inconvenient |

## 2. Worked examples

**Example A — benchmark claim**

> "Switching to the new JSON parser reduced p99 latency by 40%."

- If the reviewer ran the benchmark and has the histogram: `VERIFIED` for *that workload on that
  machine*.
- If the number comes from the vendor blog: `LIKELY` at best, and the workload difference must be
  named.
- If the number comes from a different service: `SPECULATIVE` for this service.
- The correct conclusion is scoped: "on workload W, environment E, version V".

**Example B — causal claim**

> "The cache caused the outage."

Observation: cache hit rate dropped before the outage. That is correlation. `DERIVED` only if you can
show the mechanism (miss storm → origin saturation → queue growth → timeouts) and exclude the
alternative (origin degraded first, causing misses). Otherwise `HYPOTHESIS` with a named test.

**Example C — absence claim**

> "No SQL injection exists in this codebase."

This is almost never `VERIFIED`. The honest form: "No SQL injection was found in the N handlers
reviewed, using parameterization checks; X handlers were not reviewed." Label `LIKELY` with scope, or
`UNKNOWN` if coverage is low.

**Example D — compatibility claim**

> "The library supports Python 3.9+."

`VERIFIED` only if you read the metadata for the exact version **and** either ran it or found the
classifiers/CI matrix. A README sentence is `LIKELY`; a `python_requires` field plus a CI matrix is
stronger.

## 3. Common mislabeling patterns

| Pattern | What it looks like | Correction |
| --- | --- | --- |
| Confidence inflation | "Clearly", "obviously", "definitely" around an untested claim | Remove the adverb, add the label |
| Scope creep | One test result stated as a general law | Add the scope or downgrade |
| Authority transfer | "The docs say" used for behavior the docs do not specify | Check the normative text, not the tutorial |
| Correlation → cause | Timeline adjacency presented as mechanism | Require a mechanism and a counterfactual |
| Survivorship | "All our successful migrations used X" | Ask which migrations failed |
| Cherry-picked baseline | Improvement measured against a deliberately weak baseline | Compare against the strongest reasonable baseline |
| Metric substitution | Throughput claimed, latency measured | State the metric actually measured |
| Single-source stack | Three citations, one origin | Count independent origins, not links |

## 4. Grading a chain

For a chain `A → B → C`, the label of `C` cannot exceed the weakest link. If `A` is `LIKELY` and `B`
is `DERIVED`, then `C` is at most `LIKELY`. Do not re-label the chain as `DERIVED` because the final
step "feels" solid.

## 5. When to upgrade

A claim may be upgraded only by new evidence, never by emphasis. The upgrade path is:

`SPECULATIVE → HYPOTHESIS` (a test exists) → `LIKELY` (independent supports) → `VERIFIED` (direct
observation).

Write down which step produced the upgrade. Future readers need to know whether a claim was verified
or merely promoted.
