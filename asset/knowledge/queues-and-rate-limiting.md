# Leaf 7 — Job queues and rate limiting

Parent: [asset](../asset.md) · Next: [observability-and-deployment](observability-and-deployment.md)

## Queue design

- Enqueue intent, not state: the payload is a small id + version; workers
  re-read current data so a stale message cannot corrupt state.
- At-least-once delivery is the default assumption → handlers must be
  idempotent (dedupe key, unique constraint, or state-machine guard).
- Visibility timeout must exceed the p99 handler duration, or the job runs twice.
- Poison messages: bounded retries with exponential backoff + jitter, then a
  dead-letter queue with the failure reason, then a replay tool.
- Separate queues by class of service (latency-sensitive vs bulk) so a backfill
  cannot starve user-facing work.

## Throughput control

- Worker concurrency is bounded by the downstream limit (DB pool, API quota),
  not by CPU. Set concurrency = pool share × safe factor.
- Backpressure: cap queue depth, shed or delay new work at the threshold, and
  surface the metric so autoscaling can act on it.
- Long jobs: checkpoint progress so a restart resumes instead of restarting.

## Rate limiting

- Choose the algorithm per goal: token bucket for bursts, sliding window for
  hard quotas, leaky bucket for shaping outbound calls.
- Key on the smallest stable identity (tenant + principal + route); a global
  limiter lets one noisy tenant evict everyone.
- Distributed limiters need a shared store with atomic ops; a local-only
  limiter multiplies the quota by the replica count.
- Return `429` with `Retry-After` and a machine-readable limit header; log the
  key at low cardinality so abuse is diagnosable without PII.
- Protect expensive endpoints (auth, search, export, password reset) first;
  add a concurrency cap for anything that fans out to other services.

## Probes

`scripts/check_idempotency.py` · review gate: [release-gate](../checklists/release-gate.md)
