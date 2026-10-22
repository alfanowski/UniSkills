# Source Assessment

> A source is a claim about reliability. Evaluate it, do not inherit its authority.

## 1. Hierarchy

| Tier | Source type | Typical use | Failure mode |
| --- | --- | --- | --- |
| 1 | Reproduction you performed | Settles behavior | Environment-specific; scope it |
| 2 | Primary artifact (source, binary, spec text, schema, measurement) | Settles mechanism | Misread; version mismatch |
| 3 | Official docs, RFC, normative standard, changelog | Settles intended behavior | Docs drift from implementation |
| 4 | Maintainer statement (issue, PR, release note) | Explains intent and known bugs | Optimistic or outdated |
| 5 | Independent measurement or peer-reviewed study | Settles effect size | Narrow sample; non-replication |
| 6 | Practitioner write-up, book, talk | Lead generation | Unstated environment |
| 7 | Forum, wiki, aggregator, AI summary | Hint only | Circular sourcing |

Tier 7 is not evidence. If a load-bearing claim rests on it, either upgrade it or label `LIKELY` and
name the gap.

## 2. Questions per source type

**Documentation**

- Which version? Does a version selector exist and is it set correctly?
- Is the statement normative (`MUST`) or illustrative ("for example")?
- Does the changelog show a behavior change near the version in use?

**Research paper**

- Preprint, peer-reviewed, or industry report?
- Sample size, population, and task — do they match your case?
- Was it independently replicated? Any retraction or correction?
- Are the baselines the strongest reasonable ones?
- Is the metric the one you care about (accuracy vs latency vs cost)?

**Repository / library**

- Release cadence, open critical issues, maintenance status.
- Test coverage of the specific feature you depend on, not the badge number.
- License compatibility for your use, checked per file when a repo mixes licenses.
- The actual implementation for the edge case you rely on — not only the README example.

**Benchmark / performance claim**

- Hardware, OS, runtime version, dataset, warmup, repetitions, variance.
- Median or mean? Tail reported? Outliers removed and by which rule?
- Is the comparison apples-to-apples (same work, same constraints)?
- Who ran it, and do they benefit from the result?

## 3. Independence

Two sources are independent only if they do not share the underlying measurement, dataset, or author
incentive. Check:

1. Does source B cite source A for the number? → one origin.
2. Do both use the same public dataset? → partially dependent; the dataset's biases are shared.
3. Are both authored by the vendor? → one interested party.

Count origins, not links. "Three articles agree" often means one blog post was paraphrased twice.

## 4. Citation laundering

Symptoms:

- A specific number with no methodology, repeated verbatim across posts.
- "Studies show" with no study named.
- A citation chain that terminates in a dead link or a press release.
- Metrics with suspicious precision (`37.4%`) and no sample size.

Response: find the primary source or downgrade the claim to `SPECULATIVE`. Do not repeat the number
just because it is widely repeated.

## 5. Conflict resolution

When sources disagree:

1. Check whether they describe different versions, environments, or definitions. Most conflicts
   dissolve here.
2. If they genuinely conflict, prefer the source closer to the artifact (tier 2 over tier 3 over tier
   6), and note the disagreement.
3. Never average conflicting numbers. A mean of two incompatible measurements is a third, meaningless
   measurement.
4. If the decision depends on the conflicting value, state the decision threshold: "if the true value
   is below X we choose A, otherwise B".

## 6. Recording

For every cited source, record:

```text
URL | title | publisher | publication or version date | access date | tier | what it actually says
```

"What it actually says" is a short paraphrase of the specific sentence used. If you cannot paraphrase
it, you have not read it.
