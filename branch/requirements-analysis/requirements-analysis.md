# requirements-analysis — 需求分析流程

输入：用户诉求（新功能、改造、故障、评审）。产出：叶定位 + 约束清单 + 方案候选。

## 步骤

1. **归类**：把诉求映射到知识树叶（1 语义 / 2 API / 3 身份 / 4 安全 /
   5 呈现 / 6 数据 / 7 队列 / 8 运行 / 9 性能），拓扑见
   [知识树](../../references/知识树.md)。跨叶按「契约 → 实现 → 交付」排序。
2. **边界判定**：若主问题属于视觉设计、浏览器框架实操、契约设计或 e2e 自动化，
   移交兄弟技能（[dependence](../../dependence/dependence.md)），本流程只输出
   服务端需保证的接口与约束。
3. **取事实**：环境、版本、流量形状、现有契约、指标基线。缺事实就跑探针
   （[scripts](../../scripts/scripts.md)），跑不了就标注 `unknown` —— 见
   [evidence-rule](../../resistance/evidence-rule.md)。
4. **列约束**：逐条对照 [resistance](../../resistance/resistance.md) 四红线，
   标出本次会触碰的条款。
5. **出候选**：2–3 个方案，各写成本、可逆性、证据；不可逆项必须配
   [rollback-plan](../../asset/templates/rollback-plan.md)。
6. **定稿**：难逆的决策落 [decision-record](../../asset/templates/decision-record.md)。

## 退出条件

- 叶已定位、事实有来源、触碰的约束已列出、方案含可逆性说明。
- 未满足前不得进入 [implementation](../implementation/implementation.md)。

## 常见误判

- 把「页面慢」直接归到 9（性能）而忽略 8（部署/反代超时）或 6（N+1）。
- 把 CORS 报错当鉴权 bug 修 —— 先分清预检与凭证规则（叶 4）。
- 用实验室指标回答现场问题（阈值判定须 p75 现场数据）。
