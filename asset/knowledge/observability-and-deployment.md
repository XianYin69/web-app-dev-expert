# Leaf 8 — Observability and deployment

Parent: [asset](../asset.md) · Next: [performance-budgets](performance-budgets.md)

## Structured logs

- One JSON schema: `ts`, `level`, `msg`, `trace_id`, `span_id`, `route`,
  `status`, `dur_ms`, `tenant`. Free text stays in `msg` only.
- Never log credentials, tokens, cookies, `Authorization`, full request bodies,
  or national ids; put an allow-list in the serialiser, not in review comments.
- Sample high-cardinality success logs; keep 100% of errors and slow requests.

## Tracing and metrics

- Propagate `traceparent` across proxies, queues and callbacks; a job that
  loses its context breaks the request-to-worker story.
- RED metrics per route (rate, errors, duration histogram) plus USE per
  resource (utilisation, saturation, errors). Histograms over averages —
  p99 is where incidents live.
- Alerts fire on symptoms (SLO burn rate), not causes; every alert links to a
  dashboard and a runbook.

## Build and container

- Reproducible builds: pinned lockfiles, fixed base digest, build args recorded
  as OCI annotations. Multi-stage keeps the runtime image minimal and non-root.
- The image is immutable; config arrives via env or mounted secrets, never by
  editing the container after start.
- Healthcheck = dependency-aware readiness, distinct from liveness; a liveness
  probe that checks the DB restarts pods during a DB outage.

## Reverse proxy, TLS, CORS

- Terminate TLS at the edge, forward `X-Forwarded-Proto`/`For` and trust only
  the proxy hop; the app must not accept spoofed forwarded headers.
- Certificates: automated renewal with a monitored expiry date; keep the full
  chain (leaf → intermediate → root) or mobile clients fail intermittently.
- Timeouts: proxy read timeout > app p99, or you get 502s that the app logs
  as successes.

## Progressive delivery

- Deploy behind a flag; canary by percentage with automatic rollback on SLO
  burn. Migrations run before the code that needs them, never after.
- Every release records: version, change list, rollback command, measured
  before/after metrics. See [templates](../templates/rollback-plan.md).

## Probes

`scripts/check_tls_chain.py` · `scripts/scan_dependency_vulns.py`
