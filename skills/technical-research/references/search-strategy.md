# Search Strategy

> Research quality is mostly a function of query quality and source selection, not of reading speed.

## 1. Query families

Run at least three families for any non-trivial question:

| Family | Purpose | Example shape |
| --- | --- | --- |
| Canonical | Find the normative definition | `<standard> specification <term>`, `RFC <number> <topic>` |
| Implementation | Find how it actually behaves | `<project> <feature> source`, `<project> issue <symptom>` |
| Failure | Find where it breaks | `<tech> limitations`, `<tech> production issues`, `<tech> considered harmful` |
| Comparative | Find alternatives and their trade-offs | `<a> vs <b> benchmark`, `<a> migration postmortem` |
| Historical | Find why it is this way | `<tech> design rationale`, `<tech> changelog <year>` |
| Practitioner | Find field experience | `<tech> at scale`, `<tech> lessons learned` |

## 2. Source selection order

1. The normative text: specification, RFC, standard, language reference.
2. The implementation: source code, tests, type definitions.
3. The project's own record: changelog, release notes, migration guide, issue tracker.
4. Independent measurement: benchmark, paper, reproducible report.
5. Practitioner experience: engineering blog with numbers and method.
6. Aggregators and summaries: only to find 1–5.

If a claim only exists at level 6, it is a lead, not a finding.

## 3. Triage rules

Discard without guilt when:

- the date precedes a major rewrite or version change and the doc has no version selector;
- the source is a marketing page making a comparative performance claim;
- the article has no methodology but has precise numbers;
- the content is an AI-generated summary with no primary citation;
- the source describes a different platform, scale, or workload and does not say so.

Record discarded sources in one line each when the question is contested; the discard list protects
against re-searching the same dead end.

## 4. Reading protocol

For each retained source:

1. Identify the specific section that answers the question.
2. Copy the exact sentence or the code line into the ledger — paraphrase only after quoting.
3. Note the version or commit.
4. Note what the source does **not** say (this is where over-generalization starts).

## 5. Search log

For `DEEP` and `FORENSIC` work, keep:

```text
query | engine/source | date | results triaged | retained | reason for discarding the rest
```

This makes the research reproducible and shows saturation honestly.

## 6. Saturation

Stop searching when three consecutive query families return only sources already in the ledger, or when
new sources repeat the same primary measurement. Report the saturation point; do not claim exhaustiveness.
