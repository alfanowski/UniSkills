# Example: Cross-Tenant Read in a Report Export

> Synthetic example. Invented code and identifiers. Demonstrates a source-to-sink security finding with
> reachability, not a payload.

## The surface

```python
@app.get("/reports/{report_id}/export")
def export_report(report_id: int, user=Depends(current_user)):
    report = load_report(report_id)          # loads by primary key only
    rows = db.execute(
        "SELECT * FROM report_rows WHERE report_id = :rid", {"rid": report.id}
    )
    return csv_stream(rows)
```

Authorization middleware requires a valid session. Report ids are sequential integers.

## What a UniSkills security review returns

**Authorization:** repository owned by the requesting team; static review only; no active testing.
**Verdict:** FAIL

### S1 — Missing tenant predicate allows reading another tenant's report by id

- **Severity:** HIGH · **Confidence:** high · **Status:** CONFIRMED (static path)
- **Actor / precondition:** any authenticated user in tenant A; knows or guesses a `report_id` belonging
  to tenant B (ids are sequential).
- **Chain:** `report_id` (path parameter, attacker-chosen) → `load_report(report_id)` which filters only
  on `id` → `report` object → `report_rows` query on `report.id` → CSV response containing another
  tenant's rows.
- **Evidence:** `app/reports.py:41` (parameter), `app/reports.py:43` (load), `app/reports.py:44`
  (downstream query). No tenant filter in either query; no ownership check between load and use.
- **Blocked by:** nothing on this path. The middleware proves *a* session, not *ownership*.
- **Impact:** confidential report contents of any tenant, bounded by report id enumeration. Detection is
  unlikely: the request is a normal authenticated GET.
- **Fix:** make the query tenant-scoped at the data layer —
  `SELECT ... WHERE report_id = :rid AND tenant_id = :tid` — and pass the tenant from the session, never
  from the request. Then add an authorization test that asserts 404 (not 403) for a foreign id.
- **Acceptance:** a test that creates a report in tenant B, authenticates as tenant A, requests the
  export, and asserts 404 with no rows in the response body.

### Control register (excerpt)

| Control | Status | Evidence | Note |
| --- | --- | --- | --- |
| Authentication | present | middleware configured | applies to all `/reports/*` |
| Object-level authorization | **absent** | `reports.py:43` | no tenant or owner predicate |
| Tenant scoping in queries | **absent** | `reports.py:44` | filters on report id only |
| Rate limiting | cannot determine | no config in scope | affects enumeration cost, not impact |
| Audit logging | absent | no log call on export | reduces detection |

### Residual risk and coverage

- The same `load_report` helper is used by two other handlers (`app/reports.py:88`, `app/admin.py:31`).
  They were not reviewed; if they share the pattern, the finding applies there too.
- Deployment may add a row-level security policy not visible in application code. If so, the impact
  downgrades to `MEDIUM`, but the application-level check is still missing.
- Enumeration feasibility depends on rate limiting, which was out of scope.

## What this example demonstrates

- The finding is not "missing authorization check". It is a specific actor, precondition, and path.
- The fix is structural (tenant in the predicate) rather than a string check on the response.
- The acceptance test asserts non-disclosure, not just a status code.
- The residual risk section names the two conditions that would change the severity.
