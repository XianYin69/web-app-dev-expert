# web-app-dev-expert

Web 应用工程的资深专家顾问技能：在**设计、实现、上线、回滚**服务端行为、安全交付与性能
预算时给出**可执行**的专家判断——判据、清单、探针、回滚方案四件齐出。

## 定位与边界

九叶：HTTP 语义与缓存 · 服务端 API 形态 · 身份与会话 · 安全加固 · 渲染与静态生成 · 数据
访问与迁移 · 队列与限流 · 可观测与部署 · 性能预算。外派（见
[dependence](dependence/dependence.md)）：视觉交互 → `web-design-expert`；浏览器框架实操
→ `frontend-dev`；契约设计 → `interface-design-expert`；e2e 自动化 → `webapp-testing`。

## 快速使用

```
python -B scripts/check_response_headers.py --url https://host/path
python -B scripts/check_cookie_attrs.py --url https://host/login
python -B scripts/probe_cors_preflight.py --url https://api/host/x --origin https://app.host
python -B scripts/test_cache_compression.py --url https://host/app.js
python -B scripts/check_idempotency.py --url https://api/host/orders --body '{"a":1}'
python -B scripts/sample_web_vitals.py --url https://host --field metrics.json
python -B scripts/report_bundle_budget.py --dir dist --budget budget.json
python -B scripts/scan_dependency_vulns.py --lock package-lock.json
python -B scripts/check_links.py --root . --strict-url; python -B scripts/deps_check.py
```

## 目录结构

| 路径 | 内容 |
|---|---|
| `SKILL.md` / `agent/` | 入口（frontmatter＋一句话提示词）／四格式提示词 |
| `branch/` | 四条流程：需求分析 → 实现 → 部署 → 回滚（文件夹名＝流程名） |
| `asset/knowledge/`、`knowledge_tree.json` | 九叶判据与机读索引 |
| `asset/checklists/`、`asset/templates/` | security-review、release-gate；decision-record、rollback-plan |
| `references/` | 规范出处（每条经本机 200 核验）＋知识树拓扑 |
| `resistance/` | secrets、data-change-guardrails、change-rollback、evidence-rule |
| `scripts/` | 12 探针＋check_links/deps_check 自检（见 [scripts.md](scripts/scripts.md)） |
| `dependence/`、`planned_tasks/` | 依赖声明（每条附 `source_url`）／计划任务（交 SMS 调度器） |

## 用法约定

定位知识树叶 → 选协议与渲染策略 → 定契约 → 实现 → `scripts/` 探针取证 → 按 `resistance/`
复核 → 带回滚方案上线。**无证据不下结论**：性能数字须来自 `--field` 实测或探针输出
（[evidence-rule](resistance/evidence-rule.md)）。许可：MIT（见 `LICENSE`）；版本见 `CHANGELOG.md`。
