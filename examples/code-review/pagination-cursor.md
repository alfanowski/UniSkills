# Example: Reviewing a Pagination Cursor Change

> Synthetic example. The code, repository, and numbers are invented to demonstrate output shape and
> evidence discipline. Not a real pull request.

## The change under review

```diff
-    next := lastID + 1
+    next := lastID
     rows, err := db.Query(ctx, "SELECT id, name FROM items WHERE id > $1 ORDER BY id LIMIT $2", next, limit)
```

Intent from the commit message: *"fix duplicate row on page boundary"*.

## What a UniSkills review returns

**Verdict:** BLOCK
**Intent:** make the cursor inclusive so the row at the boundary is not skipped.
**Scope:** `internal/items/list.go`, `internal/items/list_test.go`, plus call sites of `listPage`.
**Not reviewed:** the export endpoint that reuses `listPage` with a different cursor source.
**Tests run:** `go test ./internal/items/...` — pass (does not cover the boundary).

### F1 — Cursor is now inclusive but the query is still exclusive: first row repeats on every page

- **Severity:** HIGH · **Priority:** P1 · **Confidence:** high · **Status:** INTRODUCED
- **Location:** `internal/items/list.go:88`, query at `:91`
- **Trigger:** any list with more than one page where the caller passes the returned `next`.
- **Mechanism:** `next` is set to the last returned id, and the query filters `id > $1`. The row with
  `id == next` is therefore included again on the next page. The comment claims an inclusive cursor, but
  the predicate was not changed with it.
- **Impact:** every page after the first repeats its first row; clients that concatenate pages produce
  duplicates and any client that de-duplicates silently loses the repeated item's position.
- **Evidence:** `list.go:88` assigns `lastID`; `list.go:91` keeps `>`. The diff touches only the
  assignment.
- **Fix:** return `lastID` and change the predicate to `id >= $1`, or keep `> $1` and return
  `lastID + 1`. Pick one and make the test assert the boundary.
- **Acceptance:** a test that inserts ids 1..5, requests `limit=2` twice, and asserts the second page
  starts at id 3 — fails on this revision, passes after either fix.

### F2 — No regression test for the behavior the commit claims to fix

- **Severity:** MINOR · **Priority:** P2 · **Confidence:** high · **Status:** INTRODUCED
- **Location:** `internal/items/list_test.go:41`
- **Mechanism:** the only list test uses a single page, so both the old and new code pass. The commit
  message describes a boundary fix that the suite cannot observe.
- **Impact:** the defect in F1 reached review undetected, and the original duplicate bug is still not
  covered.
- **Fix:** add the two-page test described in F1's acceptance criteria.

### Finding considered and rejected

The diff also removes a `+1` that a reader might flag as an off-by-one in the *limit* calculation. It is
not: `limit` is unchanged and bounds the page size only. Reporting it would have been a false positive.
Recorded here because a review that only lists findings hides the discrimination work.

### Residual risk

- The export endpoint reuses `listPage` with a cursor derived from a different column. Its ordering
  assumption was not verified.
- The database collation for `id` was assumed to be numeric, not lexical.

## Why this is the shape, not just the answer

- The finding names the trigger, the mechanism, and the impact separately, so a reader can disagree with
  one part.
- The fix offers two valid options rather than one arbitrary patch.
- The acceptance test is stated so that it fails before and passes after.
- The rejected candidate is recorded, which is what separates a review from a list of suspicions.
