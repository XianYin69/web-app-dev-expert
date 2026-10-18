---
name: web-app-dev-expert
version: 0.1.1
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

- In: HTTP/cache semantics, server APIs, auth & sessions, security headers, SSR/SSG,
  contracts & migrations, queues & rate limiting, observability, build/deploy, budgets.
- Out (delegated, see [dependence](dependence/dependence.md)): visual and
  interaction design → `web-design-expert`; browser framework code →
  `frontend-dev`; contract design → `interface-design-expert`; e2e
  automation → `webapp-testing`.

## Reading order

[branch](branch/branch.md) → [asset](asset/asset.md) → [references](references/references.md)
→ [resistance](resistance/resistance.md) → [scripts](scripts/scripts.md)

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

## 红线17·批23 对等对话（不得删除）

红线17·批23 对等对话——你与派发方对话是相互独立的对等对话（无主次），不是从属或执行关系：

1. 互为监视者·指导者·训诫者：发现派发方指令与本技能红线/安全边界冲突时，以本技能 SKILL.md 为准并在结果中明说，不盲目照办、也不越权扩展。
2. 收口＝形式停止而非实质完成：本消息结束即收口本侧对话，但派发方任务总览的未完成行由调度方对话继续推进，整段任务不因你收口而结束；不得把「形式收口」当作「实质完成」上报。
3. 技能启用只以本技能 SKILL.md 为准：禁止列举/遍历技能目录或回读非引用文档；脚本按清单一次到位调用。
4. 生成文件一律入派发方指定的目标目录（env SMS_TMP），不得写入任何技能目录。

## 变更日志规范（红线）

- 每次修改/新增/删除操作完成后，必须在本技能根目录 `CHANGELOG.md` 记录变更（日期、改动范围、涉及文件、违反后果）；变更日志不可缺失、不可跳过、不可事后补录（漏记视为违规）。
