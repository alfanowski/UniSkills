# Hypotheses and Probes

## 1. Writing a usable hypothesis

Format: **mechanism + prediction + falsifier**.

> "The retry loop duplicates the write because the idempotency key is generated per attempt. If true,
> the DB should contain two rows with the same business key and different request ids for a single
> client retry. If I set the key once per request, duplicates should disappear."

Checklist:

- It names a mechanism, not a category ("a race" is a category).
- It predicts an observation you have not yet made.
- It can be refuted by a cheap probe.
- It explains the *differential* (why here, why now), not just the failure.

## 2. Ranking

Score each hypothesis on:

| Dimension | Question |
| --- | --- |
| Prior | How common is this class of bug in this codebase? |
| Fit | Does it explain all observations, or only some? |
| Discrimination | How many competing hypotheses does the probe eliminate? |
| Cost | How long does the probe take? Does it require production access? |
| Reversibility | Can the probe be run without side effects? |

Run `discrimination / cost` first. Do not run the probe that only confirms the favorite hypothesis.

## 3. Probe design

Good probes are:

- **read-only** where possible (logs, traces, metrics, a snapshot, a debugger breakpoint on a copy);
- **narrow** — one variable changed;
- **observable** — produce a value that distinguishes hypotheses, not a binary "still broken";
- **recorded** — command, timestamp, result, interpretation written before running.

Bad probes: restarting the service (resets state and destroys evidence), adding a `try/catch` to see if
the error disappears, enabling verbose logging on a production hot path without a rate limit.

## 4. Interventional confirmation

The strongest evidence is a controlled change:

1. Reproduce with the suspected cause present → fail.
2. Remove or neutralize the cause → pass.
3. Reintroduce it → fail again.

Two out of three is `PROBABLE`. All three is `CONFIRMED`. If the intervention is impossible (production
data, third-party service), say so and cap the confidence.

## 5. Flaky / nondeterministic failures

1. Quantify: run N times, record pass/fail and any varying field. N ≥ 20 for a rough rate.
2. Look for a varying input: time, randomness, ordering, concurrency, network, locale, hash seed.
3. Freeze each candidate variable one at a time (`--seed`, fixed clock, single worker, sorted iteration).
4. If freezing one variable makes it deterministic, you have found a contributing factor.
5. Use stress amplification (higher concurrency, smaller timeouts, injected latency) to raise the rate,
   not to prove the cause.
6. Record the observed rate before and after the fix; "it stopped happening" is not evidence.

## 6. Instrumentation rules

- Log at boundaries, not inside tight loops.
- Include a correlation id so log lines can be ordered.
- Prefer structured fields over string concatenation.
- Never log secrets or full payloads; log shape, sizes, and hashes.
- Remove temporary instrumentation before declaring done, or convert it into a permanent metric.
- Beware the observer effect: adding a log line can change timing enough to hide a race.

## 7. Bisection

Prerequisites: a known-good revision, a known-bad revision, and a scripted predicate that returns
pass/fail. Without the predicate, bisection becomes manual guessing with extra steps.

- `git bisect run ./check.sh` for code regressions.
- For data or config, bisect by time window and correlate with change records.
- For dependency regressions, bisect the lockfile, not the source tree.
