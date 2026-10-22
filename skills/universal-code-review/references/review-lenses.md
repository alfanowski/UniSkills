# Review Lenses

> Apply in order. Each lens has a surface only if the change touches it; skip with a reason, not by
> accident.

## 1. Control flow

- Can every branch be reached? Is any branch now unreachable?
- Are loops bounded? What is the termination argument for the new loop?
- Are early returns / `break` / `continue` / `throw` in the right place?
- Does an added `await`/`yield` change ordering or atomicity?
- Are switch/match arms exhaustive after the change (new enum value, new variant)?
- Recursion depth bounded by input size?

## 2. Data flow and state

- What are the possible values of each new or modified variable at each use?
- Can it be null/undefined/empty/NaN at a point where the code assumes otherwise?
- Is a value mutated after being shared? Aliasing across threads/tasks?
- Does the change introduce a second source of truth for the same fact?
- Is a cache or memo keyed on everything it depends on?
- Are units consistent (ms vs s, bytes vs KiB, cents vs dollars, inclusive vs exclusive ranges)?

## 3. Boundaries and edge cases

- Empty collection, single element, maximum size.
- Zero, negative, maximum integer, overflow, underflow, division by zero.
- Unicode, normalization, case folding, locale, time zone, DST transitions.
- Clock skew, monotonic vs wall clock, leap seconds where relevant.
- Partial input, truncated stream, retry after partial success.
- First run vs steady state (cold cache, empty table, missing index).

## 4. Contracts and compatibility

- Preconditions: did the change weaken one without updating callers?
- Postconditions: does a caller rely on an ordering or side effect that changed?
- Invariants: which one is now violated in an intermediate state?
- Public API/ABI: is this a breaking change? Is it versioned?
- Serialization: does the new field break old readers? Is it optional on the wire?
- Error taxonomy: does a new exception type escape an unchanged `catch`?
- Database: is the migration reversible? Does it lock? Is the backfill ordered correctly relative to
  the deploy?

## 5. Resources and lifetime

- Allocation inside a loop; growth proportional to input without a bound.
- File descriptors, sockets, DB connections, locks: acquired on every path, released on every path?
- Transactions: committed/rolled back on every branch, including exceptions and cancellation?
- Background tasks: awaited, cancelled, or leaked?
- Temporary files: cleaned on failure too?
- Retries: bounded, jittered, idempotent?

## 6. Concurrency and async

- Shared mutable state without a lock or ownership rule.
- Check-then-act races (TOCTOU) on files, DB rows, caches.
- Lock ordering and potential deadlock; lock held across I/O.
- Atomics: correct memory ordering, correct read-modify-write primitive.
- Async cancellation: is cleanup guaranteed? Is `CancelledError` swallowed?
- Thread/task pools: unbounded queue, starvation, blocking call on an event loop.

## 7. Error handling

- Swallowed exceptions (`except: pass`, empty catch).
- Errors converted into silent defaults that hide corruption.
- Error messages that lose the original cause or leak internals.
- Partial failure: is the system left in a consistent state?
- Fail-open vs fail-closed: which did the change choose, and is it the right one for this operation?

## 8. Tests

- Does a test fail if the fix is reverted? (If not, it is not a regression test.)
- Is the new branch exercised, not just the happy path?
- Are assertions specific enough to catch a wrong value, not just "no exception"?
- Is the test deterministic (time, randomness, network, ordering)?
- Does the test encode the intended contract or the current implementation?

## 9. Language-specific quick checks

| Family | High-yield checks |
| --- | --- |
| Python | Mutable default args, late binding in closures, `is` vs `==`, broad `except`, blocking calls in async, `__eq__` without `__hash__` |
| JS/TS | `==` coercion, `this` binding, floating promise, `NaN` comparisons, mutation of shared objects, missing `await` in try/catch |
| Go | Nil map write, goroutine leak, loop variable capture, error ignored, `defer` in loop, context cancellation |
| Rust | `unwrap` on fallible path, `clone` hiding a borrow problem, `unsafe` invariants, integer casts truncating, `Send`/`Sync` assumptions |
| Java/C# | `equals`/`hashCode` contract, resource leaks, checked exception swallowing, mutable statics, thread-safety of collections |
| C/C++ | Bounds, lifetime, signed/unsigned mixing, integer overflow, aliasing, exception safety, RAII gaps |
| SQL | N+1, missing index on a new predicate, non-sargable expressions, lock scope, transaction isolation assumptions |

These are prompts, not findings. A finding still needs a reachable trigger.
