# Cost Model

> Estimate top-down before measuring bottom-up. The layer that dominates decides what is worth
> measuring at all.

## 1. The layer stack

Each layer is typically one to three orders of magnitude more expensive than the one above it. If a
lower layer dominates, optimizing the upper one is wasted work.

| Layer | Typical order of magnitude | What to look for |
| --- | --- | --- |
| L1 cache / registers | ~1 ns | tight loops, branch prediction, vectorization |
| L2/L3 cache | ~10 ns | working set size, pointer chasing, layout |
| Main memory | ~100 ns | allocation rate, copies, cache misses |
| Syscall | ~1 µs | read/write per small item, `stat` storms |
| Local SSD I/O | ~100 µs | random vs sequential, fsync per record |
| Same-datacenter network | ~0.5 ms | round trips per request, chatty protocols |
| Cross-region network | ~50–150 ms | synchronous fan-out, chatty APIs |
| Human-scale interaction | > 100 ms | perceived latency thresholds |

These are orders of magnitude for reasoning, not benchmark results. Never publish them as measurements
of a specific system.

## 2. Algorithmic layer

- State complexity in terms of the actual input: `n` = rows, requests, tokens, users.
- Distinguish per-request from per-item cost: an O(n) scan inside a per-item loop is O(n²).
- Count hidden traversals: ORM lazy loading, serializer walking an object graph, validation re-scanning
  a list, repeated `len()` on a linked structure.
- Check for accidental quadratic behavior in string building, list concatenation, and nested filtering.

## 3. Memory layer

- Allocation rate matters more than peak heap for GC-heavy runtimes.
- Copies: every serialization boundary usually copies. Count them per request.
- Working set: if the hot data exceeds the last-level cache, expect a step change, not a slope.
- Object layout: pointer-heavy structures cost cache misses; arrays of structs vs structs of arrays.

## 4. I/O layer

- Round trips dominate bytes for small payloads. Batch before you compress.
- `fsync` per record is a different cost class from buffered writes.
- Random reads on spinning media and on network storage behave very differently from local SSD.
- Connection setup (TCP + TLS) can exceed the request cost for short-lived connections.

## 5. Concurrency and queueing

Little's law: `L = λ × W` (items in system = arrival rate × time in system). Use it to check whether an
observed queue depth is consistent with the claimed service time.

Utilization curve: as utilization `ρ → 1`, wait time grows roughly as `ρ / (1 − ρ)`. Consequences:

- At 50% utilization, halving service time roughly halves latency.
- At 90%, halving service time may barely move the tail, because queueing dominates.
- Adding capacity at high utilization buys less than reducing variance.

Lock contention behaves like a queue with a service time equal to the critical section. Shrinking the
critical section helps; adding threads at high contention can hurt.

## 6. Runtime and GC

- Stop-the-world pauses appear in the tail, not the mean.
- Allocation-heavy code pays for collection even when the collector is "concurrent".
- Pooling helps only when allocation or construction is demonstrably expensive; it adds lifetime bugs.

## 7. Estimation worksheet

For one request:

```text
1. Count operations per layer:      allocs = _, syscalls = _, rtt = _, queries = _
2. Multiply by per-layer cost:      total ≈ Σ (count × unit cost)
3. Identify the dominant layer:     max contribution and its share
4. Sanity-check with a measurement: if measured ≫ estimate, a hidden layer is active
5. If measured ≪ estimate, the model is wrong — find out why before trusting it
```

The worksheet is for prioritization. It is not a substitute for measurement, and its output must be
labeled `DERIVED`.
