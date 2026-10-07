# Release gate checklist

Run before any production release. Every unchecked item blocks the release.

## Contract and semantics

- [ ] Live surface matches the published contract (`check_api_contract.py`)
- [ ] Breaking changes carry a deprecation window and a `Sunset` date
- [ ] Error envelope is stable; no stack traces or internal hostnames leak
- [ ] New endpoints define pagination bounds and a max result size

## Security

- [ ] Security headers present and correct (`check_response_headers.py`)
- [ ] CSP enforced, not report-only, unless a report-only period is documented
- [ ] Session cookies: `HttpOnly`, `Secure`, explicit `SameSite`
      (`check_cookie_attrs.py`)
- [ ] CORS allow-list is exact origins; no `*` with credentials
- [ ] TLS chain complete, expiry > 30 days (`check_tls_chain.py`)
- [ ] No secrets in code, images, logs or error payloads
- [ ] Dependency scan clean or exceptions approved (`scan_dependency_vulns.py`)

## Data

- [ ] Migrations are expand-first, tested against a production-sized dataset
- [ ] No `DELETE`/`UPDATE` without `WHERE`; no manual DDL
- [ ] Backfill is batched, throttled, resumable, idempotent
- [ ] Rollback of the release does not require rolling back the migration

## Reliability

- [ ] Rate limits and queue depth caps exist on expensive endpoints
- [ ] Timeouts: proxy read timeout > app p99; retries only on idempotent calls
- [ ] Health checks separate liveness from readiness
- [ ] Dashboards and alerts exist for the new route (RED) and its dependencies

## Performance

- [ ] Budget file updated; `report_bundle_budget.py` passes
- [ ] Field metrics for the touched route are recorded before and after

## Delivery

- [ ] Feature flag or canary plan with a stated rollback command
- [ ] Rollback plan reviewed: [templates/rollback-plan.md](../templates/rollback-plan.md)
