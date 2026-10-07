# Rollback plan template

Required before any change to CORS, authentication, session handling, TLS,
schema, or cache keys — see [change-rollback](../../resistance/change-rollback.md).

## Change summary
- What: one sentence.
- Blast radius: routes, tenants, cookie scope, cache keys affected.
- Deploy method: flag | canary % | full.

## Trigger conditions
| Signal | Threshold | Source |
|---|---|---|
| error rate | > baseline × N for M min | RED dashboard |
| p99 latency | > X ms | route histogram |
| auth failures | > Y % spike | login metric |
| CSP violations | > Z / min | report endpoint |

## Rollback procedure
1. Command (copy-paste ready): `______`
2. Flag/config to flip first (fastest path): `______`
3. Migration handling: forward-fix only / reversible down — state which,
   and why (see [data-access-and-migrations](../knowledge/data-access-and-migrations.md)).
4. Cache purge scope and expected cold-start cost.
5. Who is paged, and the decision deadline.

## Data safety
- No destructive step in the rollback path. If one seems necessary, stop and
  escalate — see [data-change-guardrails](../../resistance/data-change-guardrails.md).
- Restore point / backup verified within the last N hours: yes | no.

## Post-rollback
- Confirm the metric returns to baseline; record the evidence.
- Write the incident note into a [decision record](decision-record.md) with
  the revisit trigger.

## Dry run
- Tested on staging at (timestamp): `______`
- Measured rollback duration: `______`
