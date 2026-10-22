# Quality Attributes

> A quality attribute that is not measurable is a wish. Write each one as a scenario with a stimulus, a
> response, and a measure.

## 1. Scenario format

```text
Source:      <who or what generates the stimulus>
Stimulus:    <event>
Artifact:    <component affected>
Environment: <normal / peak / degraded / recovery>
Response:    <observable reaction>
Measure:     <number and unit, with percentile and window>
```

Example: *Source:* a compute node. *Stimulus:* hard power loss. *Artifact:* order service. *Environment:*
normal load, 3 replicas. *Response:* in-flight requests fail, clients retry, no data loss. *Measure:*
< 0.1% failed requests after retry; zero acknowledged writes lost; recovery < 60 s.

## 2. Attribute catalogue

| Attribute | Typical measures | Common conflict |
| --- | --- | --- |
| Availability | uptime %, error budget, MTTR | consistency, cost |
| Reliability | error rate, data loss events | time-to-market |
| Latency | p50/p95/p99, deadline miss rate | throughput, cost |
| Throughput | requests/s at SLO, batch size | latency (queueing) |
| Scalability | cost per unit at 10x, linearity | simplicity |
| Consistency | staleness bound, read-your-writes | availability, latency |
| Durability | RPO, restore time | write latency |
| Security | attack surface, privilege breadth | usability, latency |
| Operability | deploy frequency, toil hours, blast radius | feature velocity |
| Cost | $ per 1k requests, $ per GB-month | resilience |
| Evolvability | time to add a field/service, coupling score | performance |
| Compliance | data residency, retention, auditability | cost, latency |

## 3. Conflict patterns

Decide these explicitly; they are the actual content of most architecture reviews.

- **Consistency vs availability** — under partition, choose which one degrades. Write down the business
  consequence of stale reads.
- **Latency vs throughput** — batching improves throughput and worsens tail latency. Name the percentile
  that matters for the user journey.
- **Coupling vs duplication** — sharing a library couples release cycles; copying decouples and diverges.
  Choose per boundary, not globally.
- **Simplicity vs resilience** — every redundancy mechanism is another failure mode and another thing to
  operate.
- **Cost vs everything** — cross-zone and cross-region traffic is often the dominant bill line; state the
  assumed volume.

## 4. Decomposition heuristics

- **Data ownership first.** A boundary is real only if one component owns a piece of state and others ask
  it. Boundaries drawn around code with shared database writes are organizational, not architectural.
- **Transaction boundaries define services.** If two operations must be atomic, they belong in one
  transactional domain or need an explicit saga with compensation.
- **Chattiness test.** Count synchronous calls on the critical path. If a single user request fans out
  to more than a handful of services, latency and failure probability multiply.
- **Blast radius test.** If this component fails, what stops working? If the answer is "everything", the
  decomposition is decorative.
- **Team test (Conway).** A boundary that no team can own will decay. State who operates it.

## 5. Anti-patterns

| Pattern | Symptom | Correction |
| --- | --- | --- |
| Distributed monolith | Services deploy together, share schema, synchronous chains | Re-draw along data ownership or merge them back |
| Resume-driven design | Technology chosen for the CV, constraints retrofitted | State the constraint first, then the technology |
| Premature decomposition | 12 services, 2 engineers, one database | Start with a modular monolith and explicit seams |
| Shared database | Every service reads every table | Assign ownership; expose intent-specific APIs |
| Event soup | Events with no schema, no owner, no consumer contract | Schema registry, ownership, versioning policy |
| Observability later | No traces until the first incident | Instrument the critical path before launch |
| One-way door unlabeled | Irreversible migration presented as routine | Label it, add a rehearsal and a decision gate |
