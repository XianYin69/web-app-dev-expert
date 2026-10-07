# Decision record template

Copy to `docs/decisions/NNN-<slug>.md` when a choice is hard to reverse.

## Title
One line: the decision taken.

## Status
proposed | accepted | superseded by NNN | deprecated

## Context
- Force: traffic shape, team size, existing stack, deadline, compliance need.
- Measured facts only, with the probe or dashboard that produced them.
  Unverified numbers must be marked `assumed`.

## Options considered
| Option | Cost | Reversibility | Evidence |
|---|---|---|---|
| A | | | |
| B | | | |

## Decision
Chosen option and the two strongest reasons.

## Consequences
- Positive: what gets cheaper or faster.
- Negative: what we now carry (lock-in, extra ops, migration debt).
- Boundary: which sibling skill owns the follow-on work
  (see [dependence](../../dependence/dependence.md)).

## Revisit trigger
The condition that reopens this decision (e.g. p99 > X ms, tenant count > N,
provider sunset date).

## Verification
- Probe command(s): `python -B scripts/<probe>.py <target>`
- Metric that must move, and by how much.
