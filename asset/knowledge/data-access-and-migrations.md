# Leaf 6 — Data access and migrations

Parent: [asset](../asset.md) · Next: [queues-and-rate-limiting](queues-and-rate-limiting.md)

## Access layer

- One place owns connections: a pool with a bounded max, an acquire timeout,
  and an idle reaper. Unbounded pools turn a slow query into an outage.
- Read paths use read replicas when latency tolerates replication lag; write
  paths stay on the primary. Never route a just-written read to a replica
  without a session-consistency guarantee.
- Query shape: explicit column lists, indexed predicates, bounded result sets.
  `SELECT *` breaks contract stability and covering-index reuse.
- N+1 is a design bug: batch by key, or use a dataloader with per-request scope.

## Transactions

- Keep transactions short and free of network calls; a transaction that spans
  an HTTP request holds a connection and a lock.
- Pick an isolation level deliberately; document why. Use `SELECT ... FOR UPDATE`
  or optimistic version columns for read-modify-write races, not retry loops.
- Every mutation records an audit trail (actor, reason, timestamp) — required
  for support and for compliance reviews.

## Migrations

- Expand → migrate → contract: add nullable column, backfill in batches, make
  it non-null, then drop the old column in a later release.
- Migrations are forward-only in code, reversible by deploy: keep a tested
  down path or a documented restore point.
- Locking DDL: check table size and lock semantics first (`ALTER` on a large
  table can block writes); use online/`CONCURRENTLY` variants where supported.
- Backfills: batched, throttled, resumable, idempotent, and interruptible;
  report rows/sec so the blast radius is visible.
- Never run DDL against production by hand; never `DELETE`/`UPDATE` without a
  `WHERE` — see [data-change-guardrails](../../resistance/data-change-guardrails.md).

## Probes

`scripts/scan_dependency_vulns.py` · review gate: [release-gate](../checklists/release-gate.md)
