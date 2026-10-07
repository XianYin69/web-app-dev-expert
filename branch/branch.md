# branch — 流程分支库

主干是四条线性流程，文件夹名＝流程名。每条流程的输入、动作、产出、退出条件
写在各自目录的同名 md 里；约束一律来自 [resistance](../resistance/resistance.md)。

## 流程索引

| 流程 | 何时进入 | 出口 |
|---|---|---|
| [requirements-analysis](requirements-analysis/requirements-analysis.md) | 新需求、改造、故障定位 | 定位到知识树叶 + 约束清单 |
| [implementation](implementation/implementation.md) | 方案已定，开始写代码/配置 | 探针全绿 + 契约一致 |
| [deployment](deployment/deployment.md) | 准备上线 | 发布记录 + 指标基线 |
| [rollback](rollback/rollback.md) | 触发阈值或变更受阻 | 回到基线 + 事件记录 |

## 知识树（九叶）

语义 1-2 · 信任 3-4 · 呈现 5 · 状态 6-7 · 运行 8-9 ——
拓扑与叶间因果边见 [references/知识树.md](../references/知识树.md)。

## 分支选择规则

1. 先跑 requirements-analysis：未定位到叶之前不写代码。
2. 触及 CORS / 鉴权 / TLS / 缓存键 / 迁移 → 必须先产出
   [rollback-plan](../asset/templates/rollback-plan.md)（约束
   [change-rollback](../resistance/change-rollback.md)）。
3. 落在他技能边界的问题 → 移交并在答复里给出 `skill(name=…)` 调用式，
   不进入 implementation。
4. 任一流程内同一失败重复出现 → 停止重试，回到第 1 步重新定位。

## 产出物约定

- 决策：[decision-record](../asset/templates/decision-record.md)
- 上线：[release-gate](../asset/checklists/release-gate.md)
- 安全：[security-review](../asset/checklists/security-review.md)
- 证据：探针命令 + 日期（约束 [evidence-rule](../resistance/evidence-rule.md)）
