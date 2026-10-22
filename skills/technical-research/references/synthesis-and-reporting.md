# Synthesis and Reporting

> Synthesis is not concatenation. The report must answer the question, not narrate the reading.

## 1. Reconciliation ladder

When sources disagree, work down this list before concluding that one is wrong:

1. **Different versions** — check the version selector and changelog.
2. **Different definitions** — the same word may mean different things (latency: p50 vs p99; size:
   compressed vs raw; throughput: requests vs records).
3. **Different environments** — hardware, network, dataset, concurrency.
4. **Different methods** — synthetic benchmark vs production trace; microbenchmark vs end-to-end.
5. **Different incentives** — vendor claim vs independent measurement.
6. **Genuine error** — retraction, bug, or outdated claim.

Most apparent contradictions dissolve at steps 1–3. Only claim a real conflict after checking them.

## 2. Structuring by question

Bad structure: "Source A says..., Source B says..., Source C says..." — the reader must synthesize.

Good structure:

```text
Q: Does X improve Y at our scale?
Established: X improves Y in <conditions> (source, date).
Not established: the effect at <our scale>; the closest measurement is at 1/10th the volume.
Contested: source B reports no improvement, but uses a different baseline.
Implication: adopt X for <narrow case>; do not assume the headline number.
```

Each question ends with an implication, not a summary.

## 3. Confidence language

| Phrase | Means |
| --- | --- |
| "Established" | Multiple independent primary sources agree, or one authoritative normative source |
| "Supported" | One strong primary source; no contradiction found |
| "Reported" | A source claims it; not independently verified |
| "Contested" | Credible sources disagree |
| "Not established" | No adequate evidence either way |
| "Unknowable with current access" | Would require access or measurement you do not have |

Never write "studies show" without naming the studies.

## 4. Benchmark comparability checklist

Before citing any performance number:

- same metric definition and unit;
- same workload and data distribution;
- same hardware class and runtime version;
- warmup and repetition policy stated;
- variance or tail reported;
- baseline is the strongest reasonable alternative, not a strawman;
- author has no direct incentive in the result (or the incentive is disclosed).

Any unchecked box downgrades the claim to "reported".

## 5. The "so what" paragraph

Every research output ends with one short paragraph that answers: given this evidence, what should the
reader do differently? If the answer is "nothing", say that — it is a legitimate and useful result.

## 6. Anti-patterns

- **Bibliography padding** — citing ten sources that were skimmed to look thorough.
- **False balance** — presenting a vendor claim and a peer-reviewed result as equally weighted.
- **Recency bias** — assuming the newest source is the most correct; check for regressions.
- **Silent generalization** — dropping the scope qualifier when moving from finding to recommendation.
- **Narrative smoothing** — hiding a contradiction because it complicates the story.
