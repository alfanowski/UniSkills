# Ideation Lenses

> A lens is a way of looking that produces mechanisms you would not have written from the obvious
> framing. Use at least three; each must produce at least two candidates.

## 1. Decomposition

Split the system along its natural seams and ask where the problem actually lives.

Prompts: Which stage produces the symptom? If we could only fix one stage, which one dominates? What
is the smallest component that could be replaced independently?

Produces: localized fixes, interface changes, pipeline stage replacement.

## 2. Inversion

Ask how to *guarantee* the bad outcome, then invert.

Prompts: How would we deliberately make this slow / fragile / expensive? Which of those are we already
doing by accident?

Produces: removal of accidental complexity, simplification, deletion of a step.

## 3. Constraint removal

Drop one constraint at a time and see what becomes possible. Then ask what it would cost to relax it.

Prompts: If we had no legacy compatibility, what would we build? If latency did not matter? If we could
change the data model? Which constraint is load-bearing and which is inherited habit?

Produces: staged migrations, compatibility shims, negotiated scope changes.

## 4. Prior art

Look at how three unrelated fields solved the same structural problem.

Prompts: Who has this exact constraint but a different domain (databases, compilers, logistics,
networking)? What is the standard technique there? What did they stop doing?

Produces: proven mechanisms transplanted with adaptation, not cargo-culted.

## 5. Extreme scaling

Push one dimension to 100x or to zero and observe which design survives.

Prompts: What breaks at 100x volume? At 1/100th? What if the team were one person? What if the data
were 1,000x larger? Which option degrades gracefully?

Produces: designs with explicit operating envelopes, and identification of the actual binding constraint.

## 6. Time horizon

Ask what the right answer is for one week, one year, and five years.

Prompts: Which option is cheapest to try now? Which accumulates debt? Which becomes cheaper the longer
we wait? Is this a one-way or two-way door?

Produces: sequencing strategies, spikes, throwaway prototypes, deliberate postponement.

## 7. Status quo and "do nothing"

Make the baseline explicit.

Prompts: What happens if we do nothing for six months? What is the cost of the current workaround? Who
is already solving this manually?

Produces: a real comparison point; often reveals the problem is smaller than assumed.

## 8. Mechanism check (mandatory before evaluation)

For each candidate, complete this sentence: *"This works by ___ , which changes ___ , so the outcome
becomes ___ ."* If you cannot fill the blanks without adjectives, the candidate is a slogan and must be
either developed or dropped.

## 9. Distinctness test

Two options are distinct only if they differ in at least one of:

- where state lives;
- who performs the work (client, server, operator, third party);
- when the work happens (sync, async, batch, on read);
- what is cached or precomputed;
- what is deleted rather than added;
- the failure mode under load.

If none differ, they are one option with cosmetic variation. Merge them.

## 10. Generation budget

Stop generating when a new lens produces only recombinations of existing mechanisms. Six options is
usually the practical ceiling for a decision that must be made by a human; more options reduce decision
quality rather than improving it.
