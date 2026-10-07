# deployment — 交付流程

输入：探针全绿的构建产物。产出：线上版本 + 基线指标 + 发布记录。

## 前置（缺一不得上线）

- [ ] [rollback-plan](../../asset/templates/rollback-plan.md) 已填且演练过
      （约束 [change-rollback](../../resistance/change-rollback.md)）
- [ ] [release-gate](../../asset/checklists/release-gate.md) 全绿
- [ ] 迁移已先行且为 expand 段（代码不依赖尚未存在的列）
- [ ] 镜像不可变、非 root、readiness 与 liveness 分离（叶 8）
- [ ] 证书链完整、到期 > 30 天：`python -B scripts/check_tls_chain.py --host <host>`

## 步骤

1. **构建**：锁文件固定版本，构建参数写入 OCI 注解；产物版本号可追溯到提交。
2. **发布形态**：优先 feature flag → 金丝雀（1% → 10% → 50% → 100%），
   每档观察窗口 ≥ 一个 p99 周期。
3. **观察**：RED（请求率、错误率、时延直方图）+ USE（资源利用率/饱和度/错误）；
   性能看 p75 现场 Core Web Vitals（叶 9）。
4. **判定**：达到阈值即自动回滚（阈值写在 rollback-plan 里，不临场决定）。
5. **记录**：版本、改动清单、回滚命令、前后指标差值入发布记录。
6. **收尾**：清理旧 flag 与临时限流；把遗留项转成
   [planned_tasks](../../planned_tasks/README.md) 声明（本技能不自行执行）。

## 禁止

- 无监控窗口直接全量。
- 用「重启一下」代替回滚。
- 在发布中顺手改 CORS/鉴权配置 —— 那是一次独立变更，须另附回滚方案。

## 相关

[observability-and-deployment](../../asset/knowledge/observability-and-deployment.md)
