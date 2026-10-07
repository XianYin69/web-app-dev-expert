# implementation — 实现流程

输入：已定稿方案。产出：可运行代码/配置 + 探针证据 + 契约更新。

## 步骤

1. **契约先行**：先改 OpenAPI/GraphQL schema 与错误体定义，再生成桩与类型；
   契约设计评审移交 `interface-design-expert`。
2. **语义落位**：方法/状态码/幂等键/缓存头按叶 1 实现；分页与错误包按叶 2。
3. **信任层**：Cookie 属性、会话轮换、令牌校验（固定算法、校验 `iss/aud/exp`）
   按叶 3；响应头与编码/参数化按叶 4。
4. **状态层**：连接池有上限与获取超时；迁移走 expand → migrate → contract；
   消费者幂等 + DLQ（叶 6、7）。
5. **呈现层**：渲染模型按叶 5；hydration 只覆盖必要岛屿。
6. **可观测**：结构化日志字段与 `traceparent` 传播随代码一起提交（叶 8）。
7. **预算**：新增依赖前测体积；预算文件随改动更新（叶 9）。

## 自检（提交前逐条跑）

```
python -B scripts/check_api_contract.py --spec <spec> --base <url>
python -B scripts/check_response_headers.py --url <url>
python -B scripts/check_cookie_attrs.py --url <url>
python -B scripts/probe_cors_preflight.py --url <url> --origin <origin>
python -B scripts/probe_injection_surface.py --url <url>
python -B scripts/scan_dependency_vulns.py --lock <lockfile>
```

## 退出条件

探针全绿、契约一致、清单核对完成
（[release-gate](../../asset/checklists/release-gate.md) ·
[security-review](../../asset/checklists/security-review.md)）。

## 禁止

- 未跑探针就宣称「已修复」；未测就报性能数字
  （[evidence-rule](../../resistance/evidence-rule.md)）。
- 在代码或日志里写密钥（[secrets](../../resistance/secrets.md)）。
- 直接对生产库执行 DDL 或无 `WHERE` 的删改
  （[data-change-guardrails](../../resistance/data-change-guardrails.md)）。
