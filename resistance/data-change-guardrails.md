# data-change-guardrails — 数据操作护栏

## 生产库禁止动作

1. **禁止直接 DDL**：`ALTER`/`DROP`/`TRUNCATE`/`CREATE INDEX` 只能通过版本化的
   迁移脚本执行，且执行前须给出锁语义、表行数与预计耗时。
2. **禁止无 `WHERE` 的 `DELETE`/`UPDATE`**：任何此类语句视为错误代码，
   不得生成、不得建议、不得「先跑再说」。
3. 删除类操作默认软删除或先 `SELECT` 计数确认，再在同事务中执行，
   并把行数写进审计记录。
4. 禁止在生产库上跑基准测试、随机压测或全表扫描型分析查询。
5. 禁止把备份/导出文件放进仓库或临时公网位置
   （与 [secrets](secrets.md) 同一条红线）。

## 必须的前置条件

- 迁移走 expand → migrate → contract 三段（见
  [data-access-and-migrations](../asset/knowledge/data-access-and-migrations.md)）。
- 每条破坏性变更配一份可执行的回滚或恢复点说明
  （[change-rollback](change-rollback.md)）。
- 回填任务：分批、限速、可续跑、幂等、可中断，并上报 rows/sec。
- 变更前后各取一次指标（行数、p99、错误率），差值写进发布记录。

## 答复口径

当用户要求「直接在生产上删一下」时：说明受阻条款，给出等价安全路径
（影子表 + 切换、或带 `WHERE` 与 `LIMIT` 的分批脚本 + 审计），
不得静默执行也不得假装执行。

## 违反后果

不可逆数据损毁、锁表导致服务中断、审计链断裂无法追责 —— 均不可撤回。
