# Scalability

> The validators run on every commit, so their cost must stay close to linear in the number of skills.
> This document records the complexity argument and the measurements behind that claim.

## 1. What grows

| Dimension | Today | Growth driver |
| --- | --- | --- |
| Skills | 12 | Adding a capability |
| Files per skill | 3–5 | `SKILL.md`, two references, optional scripts/assets |
| Catalog entries | 46 | Planned capabilities |
| Eval cases | 36 | Three per skill |
| Markdown files scanned | ~130 | Docs, packs, examples |

Nothing here is expected to reach tens of thousands of files. The realistic ceiling is a few hundred
skills, so the target is "linear with a small constant", not distributed processing.

## 2. Complexity per validator

| Component | Complexity | Note |
| --- | --- | --- |
| `validate_skills` | O(S × (L + R)) | Reads each `SKILL.md` once; section slicing re-splits the body a constant number of times (~8), so the constant is larger than 1 but independent of S |
| `validate_catalog` | O(S log S) | Sorting for the pack-order permutation check |
| `check_links` | O(F × L) | One pass per line, fence state kept in an array |
| `check_secrets` | O(F × L × P) | P = 11 compiled patterns, constant |
| `render_catalog` | O(S) | Single pass, string join |

No component performs a cross-product of skills. Pack membership is checked through a set of
`(skill, pack)` pairs, so a pack with N members and N skills costs O(N), not O(N²).

## 3. Measurements

Generated repositories, each skill with a `SKILL.md`, one reference, three eval cases, a catalog entry,
and membership in one pack. Minimum of two runs per size, macOS, Python 3.9.6, single process.

| Skills | skills.py | catalog.py | links.py | secrets.py | **Total** | Peak RSS |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 0.095 s | 0.019 s | 0.019 s | 0.062 s | **0.194 s** | 13 MB |
| 100 | 0.183 s | 0.039 s | 0.037 s | 0.133 s | **0.391 s** | 13 MB |
| 200 | 0.583 s | 0.107 s | 0.138 s | 0.359 s | **1.188 s** | 13 MB |
| 400 | 0.987 s | 0.166 s | 0.339 s | 0.560 s | **2.051 s** | 13 MB |

Doubling from 200 to 400 multiplies total time by ~1.7, which is linear within measurement noise.
Marginal cost is ~5 ms per skill for the full suite. A 1,000-skill catalog would land around 5 s.

Peak RSS stays flat at 13 MB: no skill body is retained after validation, so memory does not grow with
the catalog.

An earlier run at 100 → 200 showed a 3× jump; repeating the measurement removed it, which is why the
harness reports the minimum of several runs. Single-run timings on a laptop are not reliable to better
than ~2×.

## 4. Reproduce

```bash
python3 tools/benchmark_scalability.py
python3 tools/benchmark_scalability.py --sizes 50 100 200 400 --repeat 3
```

The harness generates a full synthetic repository (skills, references, eval cases, catalog, pack),
validates it, asserts zero diagnostics, and prints the table above. It writes only to a temporary
directory and removes it afterwards.

## 5. Why this is not a CI gate

Timing assertions in CI are flaky: shared runners, cold caches, and Python version differences produce
2–3× variance. The suite is therefore gated on **correctness**, and performance is checked by a human
before a release, using this harness and this document.

What CI does guarantee is that the work stays structurally linear: no new cross-skill loop can be added
without appearing in review, because every validator is a single file with an obvious traversal.

## 6. Known limits

- Measured on one machine and one filesystem; network filesystems may change the constant substantially.
- The harness generates uniform skills. Real skills vary in body length; a catalog of 400 maximal
  (500-line) skills would be roughly 3× slower than these numbers, still linear.
- Memory is reported as process peak, not per-phase; it is enough to detect accumulation, not to profile.
- No parallelism is used: validators are I/O-bound on local files, and a process pool would add
  complexity for a workload that finishes in seconds.
