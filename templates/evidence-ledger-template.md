# Evidence Ledger

> Use for `DEEP` and `FORENSIC` work. The ledger is what lets another person check the conclusion without
> replaying your session.

## Run header

```text
Task:        <one line>
Artifact:    <repository + commit> | <file + sha256> | <system + version>
Environment: <OS, runtime, tool versions>
Mode:        <static | dynamic | hybrid> | Depth: <DEEP | FORENSIC>
Started:     <ISO 8601, timezone>
```

## Claims

| # | Claim | Label | Method | Pointer | Gap |
| --- | --- | --- | --- | --- | --- |
| 1 | | | | | |

Rules:

- One row per **load-bearing** claim. Background facts do not belong here.
- `Pointer` must be reproducible: `path:line`, `commit`, `0x<offset>`, `test id`, `URL (date)`.
- `Gap` is mandatory when the label is `LIKELY`, `HYPOTHESIS`, or `UNKNOWN`.

## Commands run

| # | Command | Working dir | Output size | Purpose |
| --- | --- | --- | --- | --- |
| 1 | | | | |

Record the filtered form actually used (`rg -n -C2 ...`), not an idealized command.

## Refuted hypotheses

| Hypothesis | Probe | Observed | Why refuted |
| --- | --- | --- | --- |
| | | | |

Keeping these prevents the next person from re-walking the same dead end.

## Unknowns

| Unknown | Why it matters | What would resolve it | Cost |
| --- | --- | --- | --- |
| | | | |

## Reproduction

```bash
# exact sequence from a clean checkout, with the artifact pinned
```

If the sequence cannot be reproduced from a clean environment, say so — a ledger that only works on your
machine is a diary.
