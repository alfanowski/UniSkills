# Vision

## The problem

Engineers do not lack prompts. They lack **procedures that survive contact with reality**.

What people actually do today:

1. Keep a document of prompts that worked once.
2. Paste the relevant half into a chat, with the context that made it work last time.
3. Get an answer whose quality is unverifiable, because nothing in the prompt says what evidence would
   make it wrong.
4. Repeat the next day with a slightly different prompt.

The failure is structural, not stylistic. A prompt encodes *what to say*. It does not encode *what to
check, in what order, with what proof, and when to stop*. So the output is fluent, plausible, and
occasionally catastrophically wrong in a way that reads exactly like confidence.

Existing skill collections mostly reproduce the same shape with better packaging: a large `SKILL.md`
that tells the model to be a senior expert, followed by a checklist. That is a prompt with a schema.

## The thesis

Three things separate a skill from a prompt:

1. **A decision procedure.** Ordered steps with inputs, exit conditions, and explicit failure handling.
2. **An evidence contract.** Every load-bearing claim carries a label and a pointer, and the reader can
   check it.
3. **A cost budget.** The skill states how deep to go for which risk, and when to stop.

UniSkills is a suite built on those three, plus the infrastructure to keep them true over time:
validators, evaluation cases, and a catalog that distinguishes what exists from what is planned.

## What UniSkills is

A portable collection of **universal** skills — not tied to one repository, language, vendor, or agent
runtime — covering the recurring intellectual work of software engineering:

- reviewing a change and deciding whether it is safe;
- finding out why something fails;
- deciding what to build and how to structure it;
- establishing what is actually true, from sources;
- reasoning about cost, performance, and failure;
- understanding an artifact whose source you do not have.

Each skill is installable alone, composable with the others, and small enough to load without crowding
out the actual task.

## What UniSkills is not

| Not this | Because |
| --- | --- |
| A persona library ("act as a 10x engineer") | Tone does not change correctness |
| A prompt dump | No exits, no evidence, no evaluation |
| A single mega-skill | Loads everything, optimizes nothing, evaluates nothing |
| A model-specific product | The format is the Agent Skills standard; the method is model-agnostic |
| An autonomous agent | Skills do not grant permissions and do not act without authorization |
| A guarantee | Every output states its own limits; no skill claims exhaustiveness |

## Design principles

| Principle | Mechanism, not slogan |
| --- | --- |
| Efficiency | Reading rings, locator-first, shaped tool output, evidence reuse keys, checkpoints |
| Order | Fixed section contract per skill, numbered workflow, output template |
| Honest claims | Seven evidence labels, mandatory gap field, `UNKNOWN` as a valid answer |
| Adversarial quality | Mandatory "what would make this wrong" step above `QUICK` depth |
| Proportionality | Four depth profiles with concrete obligations, chosen by risk |
| Portability | Agent Skills format, no vendor APIs in the skills, no hardcoded paths |
| Modularity | One capability per skill, shared content by reference, packs never fork |
| Safety | Read-only default, explicit authorization gates, untrusted content stays data |
| Measurability | Deterministic validators + structured eval cases, never invented metrics |

## The low-level attention principle

The internal phrase "reason like you are reading assembly" means **resolution**, not product scope. It
is the habit of asking *how* a thing works rather than *what it appears to do*: which states exist, how
data and control move, which invariants must hold, where the trust boundary is, how it fails, and what
evidence would confirm it.

That habit is defined once in [universal-method.md](universal-method.md), embedded in compressed form in
every skill, and applied differently per domain. It does **not** imply an assembly-analysis skill, and
UniSkills deliberately does not ship one: instruction-level reasoning lives as an on-demand reference
inside `reverse-engineering`, where the question actually calls for it. See
[decision-log.md](decision-log.md#d2--no-standalone-assembly-flagship).

## Who this is for

- Engineers who already know the domain and want the *procedure* to be consistent under time pressure.
- Teams that want review and audit output to be comparable across people and sessions.
- People building agent systems who need skills with a testable contract rather than a vibe.
- Anyone who has been burned by a confident answer that turned out to be unverifiable.

## What success looks like

Not download counts. These:

1. Two engineers using the same skill on the same artifact produce the *same shape* of output, and can
   reconcile their findings.
2. Every finding in a review is checkable by a third party from the pointer alone.
3. A skill can be installed alone, in a fresh environment, and still work.
4. The validators catch a regression before a human does.
5. A planned skill is never mistaken for an existing one.

## Naming

"UniSkills" = **Universal Skills**. The name is not trademarked or claimed exclusively; the survey
records existing projects that use similar names and the risk that follows from it. The positioning is
narrow on purpose: portable, evidence-driven skills with evaluations, for people who review technical
work for a living.
