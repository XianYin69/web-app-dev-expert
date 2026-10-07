---
name: web-app-dev-expert
version: 0.1.0
description: >
  Web application engineering expert: HTTP semantics, idempotency and caching
  (ETag, Cache-Control); server-side REST, GraphQL, WebSocket, SSE; auth and
  sessions (Cookie SameSite/Secure/HttpOnly, JWT, OAuth2, OIDC); CSRF, SSRF,
  XSS, injection defences, security headers, CSP; SSR and static generation;
  front/back contracts and versioning; database access and migrations; queues
  and rate limiting; observability; build and deploy (containers, reverse
  proxy, TLS, CORS, canary, rollback); performance budgets (Core Web Vitals,
  bundle size, lazy loading). Visual design, browser framework code, contract
  design and e2e automation are delegated to sibling skills via dependence.
license: MIT
metadata:
  category: development
---

# web-app-dev-expert

使用 `web-app-dev-expert` 来完成 Web 应用工程类请求（服务端行为、安全、交付、性能预算）。

## Scope

- In: HTTP/cache semantics, server APIs, auth & sessions, security headers,
  SSR/SSG, contracts & versioning, data access & migrations, queues & rate
  limiting, observability, build/deploy, performance budgets.
- Out (delegated, see [dependence](dependence/dependence.md)): visual and
  interaction design → `web-design-expert`; browser framework code →
  `frontend-dev`; contract design → `interface-design-expert`; e2e
  automation → `webapp-testing`.

## Reading order

[branch](branch/branch.md) → [asset](asset/asset.md) →
[references](references/references.md) →
[resistance](resistance/resistance.md) → [scripts](scripts/scripts.md)

## Workflow

Analyse → pick protocol and rendering strategy → specify the contract →
implement → probe with `scripts/` → review against `resistance/` → ship
with a rollback plan.

## Red lines

- No secrets in repo or logs — [secrets](resistance/secrets.md).
- No prod DDL, no `DELETE` without `WHERE` —
  [data-change-guardrails](resistance/data-change-guardrails.md).
- CORS / auth changes need a rollback plan — [change-rollback](resistance/change-rollback.md).
- No invented performance numbers — [evidence-rule](resistance/evidence-rule.md).
- Every `.md` ≤ 50 lines; zero dangling links; see [resistance](resistance/resistance.md).
