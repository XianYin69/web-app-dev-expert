# resistance — 约束库（不可逾越）

本目录是本技能的兜底：违反其中任一条的答复不得交付。每条约束 ≤ 50 行。

## 红线清单

- [secrets.md](secrets.md) — 密钥/令牌/连接串禁止入库、入日志、入错误体。
- [data-change-guardrails.md](data-change-guardrails.md) — 生产库禁止直接 DDL；
  禁止无 `WHERE` 的 `DELETE`/`UPDATE`。
- [change-rollback.md](change-rollback.md) — 跨域与鉴权改动必须先给回滚方案。
- [evidence-rule.md](evidence-rule.md) — 不得虚构未验证的性能数字。

## 通用编辑与结构约束

1. 所有 `.md` ≤ 50 行；悬空链接必须为 0。
2. 文件夹名＝流程名；脚本使用英文名称并带扩展名。
3. 缓存与临时产物不得写入本技能目录（一律落用户缓存目录 / `tmp/`）。
4. 不得修改其他技能目录；跨界内容只做 `dependence` 引用
   （见 [dependence](../dependence/dependence.md)）。
5. 计划任务只声明不执行：`planned_tasks/` 内文件到期由 SMS 调度器读取，
   本技能自身不得运行它（见 [planned_tasks/README.md](../planned_tasks/README.md)）。

## 执行期降级策略

| 触发 | 降级动作 |
|---|---|
| 探针脚本目标不可达 | 报告网络事实与命令，改给离线口径，不得编造结果 |
| 缺少某工具（curl/openssl/node） | 用 Python 标准库等价实现，并注明差异 |
| 问题落在他技能边界 | 移交并给出 `skill(name=…)` 调用式，不写对方正文 |
| 约束与用户诉求冲突 | 先说明冲突条款，给出满足约束的替代方案再执行 |
| 同一失败重复 | 停止重试，回到 [知识树](../references/知识树.md) 重新定位叶 |

## 违反后果

密钥外泄、生产数据不可逆损毁、无回滚的鉴权变更导致全站登录中断、
虚构指标误导容量决策 —— 均不可撤回，故列为红线而非建议。

## 相关

[SKILL.md](../SKILL.md) · [branch](../branch/branch.md) ·
[asset/checklists](../asset/checklists/release-gate.md)
