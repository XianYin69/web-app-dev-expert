# CHANGELOG

本文件遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与语义化版本。

## 0.1.1 - 2026-10-07
### Added
- `README.md`：定位、边界外派、快速使用、目录结构、用法约定、许可。
- `CHANGELOG.md`：版本记录（本文件）。
- `scripts/scripts.md`：脚本索引——12 个探针的取证对象、入参、输出与退出码，加
  自检脚本约定（只读、无凭据、`parse-skipped` 不得当作通过）。
- `scripts/check_links.py`：红线自检——相对链接与正文 `scripts/…` 路径引用解析、
  `.md` ≤50 行、`--strict-url`；悬空必须为 0。
- `scripts/deps_check.py`：`deps.json` 六字段与 `source_url` 原始链接校验，`local://`
  目标在位性、`checked_at` 时效。
- `scripts/_common.py`：共用根路径、文本遍历与统一 `RESULT PASS|FAIL` 出口。
- 验证留痕：正反双链辩论（`logic_chain.py debate`，正方 7 步 / 反方 4 步 → 通过）与
  逐支门禁验证（干净样本 rc=0、缺陷样本 rc=1、不可用 rc=2 全部符合约定）。
- 补齐正文已引用但缺失的 6 个探针：`check_idempotency.py`、`check_api_contract.py`、
  `probe_injection_surface.py`、`probe_open_redirect.py`、`report_bundle_budget.py`、
  `scan_dependency_vulns.py`（纯标准库、只读、可 `--format json`）。

### Fixed
- `sample_web_vitals.py`：`un sized` 非法标识符致 SyntaxError（整支不可跑）与 `[^]*?`
  非法字符集致 PatternError，改为 `unsized` / `(?s)`。
- `check_tls_chain.py`：CPython 3.14 的 `getpeercert()['subject']` 为嵌套元组，
  `dict(...)` 直接 ValueError；加 `flatten()` 归一，现可对真实主机出结论。
- 六支探针与 `scan_dependency_vulns.py`：补 `TimeoutError` 分支（3.14 读超时不再抛栈），
  不可达一律 rc=2 并报因。
- 悬空引用归零：`SKILL.md → scripts/scripts.md` 与六处 `scripts/*.py` 正文引用。

### Changed
- `SKILL.md` 52 → 50 行、`asset/knowledge/http-semantics-and-caching.md` 51 → 50 行，
  压缩换行不改语义，回到 ≤50 行红线内。

## 0.1.0 - 2026-10-07
### Added
- 首次生成（Skill_Generator 创建路径）：`SKILL.md` YAML frontmatter 与一句话提示词、
  `agent/` 四格式提示词。
- `branch/`：需求分析、实现、部署、回滚四条流程（文件夹名＝流程名）。
- `asset/`：九叶判据（HTTP 语义与缓存、服务端 API 形态、身份与会话、安全加固、渲染与
  静态生成、数据访问与迁移、队列与限流、可观测与部署、性能预算）＋ `knowledge_tree.json`、
  `checklists/`（security-review、release-gate）、`templates/`（decision-record、rollback-plan）。
- `references/`：规范出处（RFC 9110/9111/6265/6749/9068/9700/8446、WHATWG SSE、W3C CSP、
  OWASP、MDN、OpenAPI、GraphQL、OSV、OCI）＋知识树拓扑。
- `resistance/`：secrets、data-change-guardrails、change-rollback、evidence-rule 四条约束。
- `scripts/`：初版 6 个探针（check_cookie_attrs、check_response_headers、check_tls_chain、
  probe_cors_preflight、sample_web_vitals、test_cache_compression）。
- `dependence/deps.json`：外派技能 `local://` 声明（每条附 `source_url`）。
- `planned_tasks/`：README + template.json（声明交 SMS 调度器，技能自身不执行）。
- `LICENSE`：MIT；`.gitignore`：忽略 `tmp/`、`__pycache__/`、`*.pyc`、IDE、`.env`、`*.log`。
