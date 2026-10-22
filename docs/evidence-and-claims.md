# Evidence and Claims

> Every UniSkills skill uses this vocabulary. It is the contract that lets a reader tell what you
> know from what you guessed.

## 1. Claim labels

| Label | Meaning | Minimum requirement |
| --- | --- | --- |
| `VERIFIED` | Directly observed or reproduced by the agent | Command, test id, file:line, or tool output you actually saw |
| `DERIVED` | Follows by explicit reasoning from verified facts | The verified premises + the inference step, stated |
| `LIKELY` | Strong but indirect support; one gap remains | Name the gap and what would close it |
| `HYPOTHESIS` | Proposed explanation, not yet tested | State the test that would confirm or refute it |
| `SPECULATIVE` | Exploratory idea with weak support | Marked as idea, never used as a premise for a load-bearing conclusion |
| `UNKNOWN` | Not determinable with available access/tools | Say what access or tool would be needed |
| `N/A` | The question does not apply here | One line on why it does not apply |

Rules:

- A `VERIFIED` claim must be reproducible from its pointer. "I checked it" is not a pointer.
- `DERIVED` chains are only as strong as their weakest `LIKELY` premise. Do not launder a guess into
  a fact by putting it three steps into a deduction.
- `SPECULATIVE` items may appear in brainstorming outputs; they may not appear in verdicts,
  severity ratings, or remediation steps without being upgraded first.
- When a claim cannot be labeled confidently, it is `UNKNOWN`. That is a legitimate answer.

## 2. Evidence strength ladder

For a factual question, prefer the highest applicable rung:

1. **Reproduction** — you ran it and observed the result.
2. **Direct inspection** — source, binary, config, spec text, or measurement you read yourself.
3. **Primary documentation** — official spec, RFC, vendor docs, changelog for the exact version.
4. **Maintainer statement** — issue/PR/commit message from the owning project.
5. **Secondary technical writing** — well-sourced articles, books, conference talks.
6. **Community/aggregator** — forum posts, wikis, AI-generated summaries.
7. **Recall/inference** — your own prior knowledge.

Rung 6 and 7 are lead generators, not evidence. If a load-bearing claim rests on them, either upgrade
it or label it `LIKELY` with the gap named.

## 3. Source hygiene for external material

- Record **URL, access date, and version** (of the doc, package, or spec) for anything you cite.
- Distinguish **documented behavior** from **observed behavior**: a README claim is not a test result.
- Prefer the doc for the version in use over the latest doc.
- Check whether a source is **primary** (the project itself) or **derivative** (a blog about it).
- Check publication date against the question (deprecated APIs, superseded specs, retracted papers).
- For academic claims: distinguish preprint, peer-reviewed, and industry report; check for retraction;
  look for independent replication before treating a single result as established.
- Never cite a source you did not open. Never invent a URL, DOI, author, or quotation.

## 4. Corroboration and contradiction

- **A single source is a single point of failure.** For high-impact claims, seek a second,
  *independent* source — not a second article repeating the first.
- **Search for the contradiction on purpose.** Query for the failure case, the dissenting issue, the
  benchmark that did not reproduce.
- When sources conflict, do not average them. Report: what each says, why they may differ
  (version, environment, methodology), and which one your decision depends on.
- Unresolved contradictions stay visible in the output. They are not smoothed away in the summary.

## 5. Absence of evidence

- "I did not find X" is a statement about your search, not about the world. Report the search scope
  alongside it: what you looked at, with which tools, for how long.
- A clean scan is not a security certification. A green test suite is not a correctness proof.
- For reviews, the correct phrasing is "no issue found within the reviewed scope", never "no issues".

## 6. Confidence

Use confidence qualitatively (`high` / `medium` / `low`) and tie it to the *evidence*, not to how
strongly you feel:

- **high** — reproduced or directly inspected, and the alternative explanations were checked.
- **medium** — direct evidence for part of the chain, one unverified link.
- **low** — inference from indirect signals; a plausible alternative exists.

Avoid numeric percentages. They imply a calibrated distribution that no one measured. If a domain
genuinely requires probability (risk models, reliability math), then define the model explicitly and
treat its output as `DERIVED` from stated assumptions.

**Confidence is not severity.** A high-confidence low-severity issue stays low severity. A
low-confidence high-impact issue is reported as high impact with `confidence: low` and a test plan.

## 7. What "verified" means per domain

| Domain | Counts as verification |
| --- | --- |
| Code review | The code path is read end-to-end and the failure is reachable from a real call site |
| Security | The source→sink path is traced, the precondition is reachable, and the control is absent |
| Performance | A measurement with stated environment, or a complexity argument with the input model stated |
| Debugging | A reproduction that fails before the fix and passes after |
| Research | The primary source says it, in the version cited, and no contradicting primary source was found |
| Architecture | The quality attribute scenario is satisfied under stated load and failure assumptions |
| Reverse engineering | The behavior is observed in the artifact and cross-checked by a second method (static vs dynamic) |

If you cannot reach the bar for the domain, downgrade the label — do not lower the bar.

## 8. Reporting template for graded claims

When a task requires an auditable result, the evidence table is:

```markdown
| # | Claim | Label | Evidence | Pointer | Gap / next check |
|---|-------|-------|----------|---------|------------------|
| 1 | ... | VERIFIED | ... | path:line / URL (date) / test id | — |
| 2 | ... | LIKELY | ... | ... | needs integration test |
```

Keep it to the claims that carry the decision. A table of thirty trivia items is not rigor.
