# rollback — 回滚流程

输入：触发阈值命中，或变更受阻需退回。产出：回到基线 + 事件记录。

## 步骤

1. **确认触发**：指标 + 数值 + 窗口与 [rollback-plan](../../asset/templates/rollback-plan.md)
   第 2 条一致；不一致先判是否为观测误差，不凭感觉回滚。
2. **走最快可逆路径**：先翻 feature flag / 配置开关，再考虑重新部署上一版本。
3. **执行回滚命令**：使用方案里那条可复制命令；记录执行时间与执行人。
4. **数据面**：迁移默认**只向前修复**，不回退 schema；确需回退必须已演练 down 路径。
   禁止在回滚中做任何破坏性数据操作
   （[data-change-guardrails](../../resistance/data-change-guardrails.md)）。
5. **缓存面**：按方案范围 purge；预期冷启动 origin 压力，必要时临时收紧并发。
6. **验证**：错误率、p99、认证成功率回到基线；跑
   `python -B scripts/check_response_headers.py --url <url>` 与
   `python -B scripts/check_cookie_attrs.py --url <url>` 复核头与 Cookie 未被回退带坏。
7. **记录**：现象、触发指标、回滚耗时、根因假设，落
   [decision-record](../../asset/templates/decision-record.md) 并写 revisit trigger。

## 不可回滚项（须提前判定）

- HSTS `preload` 与长 `max-age`：下发后在客户端缓存期内不可撤回。
- 已发出的 JWT / 已种下的 Cookie 作用域变更：只能靠吊销或等待过期。
- 已进入公共缓存的错配响应：需 purge，且受 `s-maxage` 窗口限制。

## 禁止

- 把「再改一次」当回滚。
- 回滚后不验证就宣布恢复。
- 回滚后不写记录 —— 下一次事故将重复同一决策。
