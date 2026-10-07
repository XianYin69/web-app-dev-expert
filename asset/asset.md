# asset — knowledge tree (nine leaves)

Root: [SKILL.md](../SKILL.md) · Topology: [references/知识树.md](../references/知识树.md)
Machine form: [knowledge_tree.json](knowledge_tree.json)

| # | Leaf | Covers |
|---|---|---|
| 1 | [http-semantics-and-caching](knowledge/http-semantics-and-caching.md) | methods, status codes, idempotency, ETag, Cache-Control |
| 2 | [server-api-patterns](knowledge/server-api-patterns.md) | REST, GraphQL, WebSocket, SSE, versioning |
| 3 | [auth-and-session](knowledge/auth-and-session.md) | Cookie attributes, sessions, JWT, OAuth2, OIDC |
| 4 | [security-hardening](knowledge/security-hardening.md) | CSP, XSS, injection, SSRF, CORS, TLS headers |
| 5 | [rendering-and-static-generation](knowledge/rendering-and-static-generation.md) | SSR, SSG, ISR, hydration, output caching |
| 6 | [data-access-and-migrations](knowledge/data-access-and-migrations.md) | pooling, transactions, expand/contract migrations |
| 7 | [queues-and-rate-limiting](knowledge/queues-and-rate-limiting.md) | jobs, DLQ, backpressure, quotas |
| 8 | [observability-and-deployment](knowledge/observability-and-deployment.md) | logs, traces, metrics, containers, canary |
| 9 | [performance-budgets](knowledge/performance-budgets.md) | Core Web Vitals, bundle size, lazy loading |

## Support material

- Checklists: [release-gate](checklists/release-gate.md) ·
  [security-review](checklists/security-review.md)
- Templates: [decision-record](templates/decision-record.md) ·
  [rollback-plan](templates/rollback-plan.md)

## Boundaries

Visual/interaction design, browser framework code, contract design and e2e
automation are owned by sibling skills — see
[dependence](../dependence/dependence.md). This tree stops at the application
layer: it states *what the server must guarantee*, not which framework writes it.
